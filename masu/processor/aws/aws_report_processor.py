#
# Copyright 2018 Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

"""Processor for Cost Usage Reports."""

import csv
import gzip
import io
import json
import logging
from os import listdir, path

from masu.config import Config
from masu.database import AWS_CUR_TABLE_MAP
from masu.database.aws_report_db_accessor import AWSReportDBAccessor
from masu.database.report_manifest_db_accessor import ReportManifestDBAccessor
from masu.database.reporting_common_db_accessor import ReportingCommonDBAccessor
from masu.external import GZIP_COMPRESSED
from masu.processor.report_processor_base import ReportProcessorBase
from masu.util.common import clear_temp_directory

LOG = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class ProcessedReport:
    """Cost usage report transcribed to our database models.

    Effectively a struct for associated database tables.
    """

    def __init__(self):
        """Initialize new cost entry containers."""
        self.bills = {}
        self.cost_entries = {}
        self.line_items = []
        self.products = {}
        self.reservations = {}
        self.pricing = {}

    def remove_processed_rows(self):
        """Clear a batch of rows from their containers."""
        self.bills = {}
        self.cost_entries = {}
        self.line_items = []
        self.products = {}
        self.reservations = {}
        self.pricing = {}


# pylint: disable=too-many-instance-attributes
class AWSReportProcessor(ReportProcessorBase):
    """Cost Usage Report processor."""

    # pylint:disable=too-many-arguments
    def __init__(self, schema_name, report_path, compression, provider_id, manifest_id=None):
        """Initialize the report processor.

        Args:
            schema_name (str): The name of the customer schema to process into
            report_path (str): Where the report file lives in the file system
            compression (CONST): How the report file is compressed.
                Accepted values: UNCOMPRESSED, GZIP_COMPRESSED

        """
        super().__init__(
            schema_name=schema_name,
            report_path=report_path,
            compression=compression,
            provider_id=provider_id
        )

        self.manifest_id = manifest_id
        self._report_name = path.basename(report_path)
        self._datetime_format = Config.AWS_DATETIME_STR_FORMAT
        self._batch_size = Config.REPORT_PROCESSING_BATCH_SIZE

        self.processed_report = ProcessedReport()

        # Gather database accessors
        with ReportingCommonDBAccessor() as report_common_db:
            self.column_map = report_common_db.column_map

        with AWSReportDBAccessor(self._schema_name, self.column_map) as report_db:
            self.report_schema = report_db.report_schema
            self.existing_bill_map = report_db.get_cost_entry_bills()
            self.existing_cost_entry_map = report_db.get_cost_entries()
            self.existing_product_map = report_db.get_products()
            self.existing_pricing_map = report_db.get_pricing()
            self.existing_reservation_map = report_db.get_reservations()

        self.line_item_columns = None

        LOG.info('Initialized report processor for file: %s and schema: %s',
                 self._report_name, self._schema_name)

    def process(self):
        """Process CUR file.

        Returns:
            (None)

        """
        row_count = 0
        self._delete_line_items()
        opener, mode = self._get_file_opener(self._compression)
        is_finalized_data = self._check_for_finalized_bill()
        # pylint: disable=invalid-name
        with opener(self._report_path, mode) as f:
            with AWSReportDBAccessor(self._schema_name, self.column_map) as report_db:
                LOG.info('File %s opened for processing', str(f))
                reader = csv.DictReader(f)
                for row in reader:
                    bill_id = self.create_cost_entry_objects(row, report_db)
                    if len(self.processed_report.line_items) >= self._batch_size:
                        LOG.debug('Saving report rows %d to %d for %s', row_count,
                                  row_count + len(self.processed_report.line_items),
                                  self._report_name)
                        self._save_to_db(report_db)

                        row_count += len(self.processed_report.line_items)
                        self._update_mappings()

                if self.processed_report.line_items:
                    LOG.debug('Saving report rows %d to %d for %s', row_count,
                              row_count + len(self.processed_report.line_items),
                              self._report_name)
                    self._save_to_db(report_db)

                    row_count += len(self.processed_report.line_items)

                if is_finalized_data:
                    report_db.mark_bill_as_finalized(bill_id)
                    report_db.commit()
                report_db.vacuum_table(AWS_CUR_TABLE_MAP['line_item'])

        LOG.info('Completed report processing for file: %s and schema: %s',
                 self._report_name, self._schema_name)

        return is_finalized_data

    def _check_for_finalized_bill(self):
        """Read one line of the report file to check for finalization.

        Returns:
            (Boolean): Whether the bill is finalized

        """
        opener, mode = self._get_file_opener(self._compression)
        # pylint: disable=invalid-name
        with opener(self._report_path, mode) as f:
            reader = csv.DictReader(f)
            row = reader.__next__()
            invoice_id = row.get('bill/InvoiceId')
            return invoice_id is not None and invoice_id != ''

    # pylint: disable=no-self-use
    def remove_temp_cur_files(self, report_path):
        """Remove temporary report files."""
        LOG.info('Cleaning up temporary report files for %s', report_path)
        current_assembly_id = None
        files = listdir(report_path)
        for file in files:
            file_path = '{}/{}'.format(report_path, file)
            if file.endswith('Manifest.json'):
                with open(file_path, 'r') as manifest_file_handle:
                    manifest_json = json.load(manifest_file_handle)
                    current_assembly_id = manifest_json.get('assemblyId')

        removed_files = []
        if current_assembly_id:
            removed_files = clear_temp_directory(report_path, current_assembly_id)

        return removed_files

    # pylint: disable=inconsistent-return-statements, no-self-use
    def _get_file_opener(self, compression):
        """Get the file opener for the file's compression.

        Args:
            compression (str): The compression format for the file.

        Returns:
            (file opener, str): The proper file stream handler for the
                compression and the read mode for the file

        """
        if compression == GZIP_COMPRESSED:
            return gzip.open, 'rt'
        return open, 'r'    # assume uncompressed by default

    def _save_to_db(self, report_db_accessor):
        """Save current batch of records to the database."""
        columns = tuple(self.processed_report.line_items[0].keys())
        csv_file = self._write_processed_rows_to_csv()

        # This will commit all pricing, products, and reservations
        # on the session
        report_db_accessor.commit()
        # This will add line items to the line item table
        report_db_accessor.bulk_insert_rows(
            csv_file,
            AWS_CUR_TABLE_MAP['line_item'],
            columns
        )

    def _delete_line_items(self):
        """Delete stale data for the report being processed, if necessary."""
        if not self.manifest_id:
            return False

        with ReportManifestDBAccessor() as manifest_accessor:
            manifest = manifest_accessor.get_manifest_by_id(self.manifest_id)
            if manifest.num_processed_files != 0:
                return False
            # Override the bill date to correspond with the manifest
            bill_date = manifest.billing_period_start_datetime.date()
            provider_id = manifest.provider_id

        LOG.info('Deleting data for schema: %s and bill date: %s',
                 self._schema_name, str(bill_date))

        with AWSReportDBAccessor(self._schema_name, self.column_map) as accessor:
            bills = accessor.get_cost_entry_bills_query_by_provider(provider_id)
            bills = bills.filter_by(billing_period_start=bill_date).all()
            for bill in bills:
                line_item_query = accessor.get_lineitem_query_for_billid(bill.id)
                line_item_query.delete()
                accessor.commit()

        return True

    def _update_mappings(self):
        """Update cache of database objects for reference."""
        self.existing_cost_entry_map.update(self.processed_report.cost_entries)
        self.existing_product_map.update(self.processed_report.products)
        self.existing_pricing_map.update(self.processed_report.pricing)
        self.existing_reservation_map.update(self.processed_report.reservations)

        self.processed_report.remove_processed_rows()

    def _write_processed_rows_to_csv(self):
        """Output CSV content to file stream object."""
        values = [tuple(item.values())
                  for item in self.processed_report.line_items]

        file_obj = io.StringIO()
        writer = csv.writer(
            file_obj,
            delimiter='\t',
            quoting=csv.QUOTE_NONE,
            quotechar=''
        )
        writer.writerows(values)
        file_obj.seek(0)

        return file_obj

    def _get_data_for_table(self, row, table_name):
        """Extract the data from a row for a specific table.

        Args:
            row (dict): A dictionary representation of a CSV file row
            table_name (str): The DB table fields are required for

        Returns:
            (dict): The data from the row keyed on the DB table's column names

        """
        # Memory can come as a single number or a number with a unit
        # e.g. "1" vs. "1 Gb" so it gets special cased.
        if 'product/memory' in row and row['product/memory'] is not None:
            memory_list = row['product/memory'].split(' ')
            if len(memory_list) > 1:
                memory, unit = row['product/memory'].split(' ')
            else:
                memory = memory_list[0]
                unit = None
            row['product/memory'] = memory
            row['product/memory_unit'] = unit

        column_map = self.column_map[table_name]

        return {column_map[key]: value
                for key, value in row.items()
                if key in column_map}

    # pylint: disable=no-self-use
    def _process_tags(self, row, tag_prefix='resourceTags'):
        """Return a JSON string of AWS resource tags.

        Args:
            row (dict): A dictionary representation of a CSV file row
            tag_prefix (str): A specifier used to identify a value as a tag

        Returns:
            (str): A JSON string of AWS resource tags

        """
        tag_dict = {}
        for key, value in row.items():
            if tag_prefix in key and row[key]:
                key_value = key.split(':')
                if len(key_value) > 1:
                    tag_dict[key_value[-1]] = value
        return json.dumps(tag_dict)

    # pylint: disable=no-self-use
    def _get_cost_entry_time_interval(self, interval):
        """Split the cost entry time interval into start and end.

        Args:
            interval (str): The time interval from the cost usage report.

        Returns:
            (str, str): Separated start and end strings

        """
        start, end = interval.split('/')
        return start, end

    def _create_cost_entry_bill(self, row, report_db_accessor):
        """Create a cost entry bill object.

        Args:
            row (dict): A dictionary representation of a CSV file row

        Returns:
            (str): A cost entry bill object id

        """
        table_name = AWS_CUR_TABLE_MAP['bill']
        start_date = row.get('bill/BillingPeriodStartDate')
        bill_type = row.get('bill/BillType')
        payer_account_id = row.get('bill/PayerAccountId')

        key = (bill_type, payer_account_id, start_date, self._provider_id)
        if key in self.processed_report.bills:
            return self.processed_report.bills[key]

        if key in self.existing_bill_map:
            return self.existing_bill_map[key]

        data = self._get_data_for_table(row, table_name)

        data['provider_id'] = self._provider_id

        bill_id = report_db_accessor.insert_on_conflict_do_nothing(
            table_name,
            data,
            conflict_columns=['bill_type', 'payer_account_id',
                              'billing_period_start', 'provider_id']
        )

        self.processed_report.bills[key] = bill_id

        return bill_id

    def _create_cost_entry(self, row, bill_id, report_db_accessor):
        """Create a cost entry object.

        Args:
            row (dict): A dictionary representation of a CSV file row
            bill_id (str): The current cost entry bill id

        Returns:
            (str): The DB id of the cost entry object

        """
        table_name = AWS_CUR_TABLE_MAP['cost_entry']
        interval = row.get('identity/TimeInterval')
        start, end = self._get_cost_entry_time_interval(interval)

        key = (bill_id, start)
        if key in self.processed_report.cost_entries:
            return self.processed_report.cost_entries[key]

        if key in self.existing_cost_entry_map:
            return self.existing_cost_entry_map[key]

        data = {
            'bill_id': bill_id,
            'interval_start': start,
            'interval_end': end
        }

        cost_entry_id = report_db_accessor.insert_on_conflict_do_nothing(
            table_name,
            data
        )
        self.processed_report.cost_entries[key] = cost_entry_id

        return cost_entry_id

    # pylint: disable=too-many-arguments
    def _create_cost_entry_line_item(self,
                                     row,
                                     cost_entry_id,
                                     bill_id,
                                     product_id,
                                     pricing_id,
                                     reservation_id,
                                     report_db_accesor):
        """Create a cost entry line item object.

        Args:
            row (dict): A dictionary representation of a CSV file row
            cost_entry_id (str): A processed cost entry object id
            bill_id (str): A processed cost entry bill object id
            product_id (str): A processed product object id
            pricing_id (str): A processed pricing object id
            reservation_id (str): A processed reservation object id

        Returns:
            (None)

        """
        table_name = AWS_CUR_TABLE_MAP['line_item']
        data = self._get_data_for_table(row, table_name)
        data = report_db_accesor.clean_data(
            data,
            table_name
        )

        data['tags'] = self._process_tags(row)
        data['cost_entry_id'] = cost_entry_id
        data['cost_entry_bill_id'] = bill_id
        data['cost_entry_product_id'] = product_id
        data['cost_entry_pricing_id'] = pricing_id
        data['cost_entry_reservation_id'] = reservation_id

        self.processed_report.line_items.append(data)

        if self.line_item_columns is None:
            self.line_item_columns = list(data.keys())

    def _create_cost_entry_pricing(self, row, report_db_accessor):
        """Create a cost entry pricing object.

        Args:
            row (dict): A dictionary representation of a CSV file row

        Returns:
            (str): The DB id of the pricing object

        """
        table_name = AWS_CUR_TABLE_MAP['pricing']

        term = row.get('pricing/term') if row.get('pricing/term') else 'None'
        unit = row.get('pricing/unit') if row.get('pricing/unit') else 'None'

        key = '{term}-{unit}'.format(term=term, unit=unit)
        if key in self.processed_report.pricing:
            return self.processed_report.pricing[key]

        if key in self.existing_pricing_map:
            return self.existing_pricing_map[key]

        data = self._get_data_for_table(
            row,
            table_name
        )
        value_set = set(data.values())
        if value_set == {''}:
            return

        pricing_id = report_db_accessor.insert_on_conflict_do_nothing(
            table_name,
            data
        )
        self.processed_report.pricing[key] = pricing_id

        return pricing_id

    def _create_cost_entry_product(self, row, report_db_accessor):
        """Create a cost entry product object.

        Args:
            row (dict): A dictionary representation of a CSV file row

        Returns:
            (str): The DB id of the product object

        """
        table_name = AWS_CUR_TABLE_MAP['product']
        sku = row.get('product/sku')
        product_name = row.get('product/ProductName')
        region = row.get('product/region')
        key = (sku, product_name, region)

        if key in self.processed_report.products:
            return self.processed_report.products[key]

        if key in self.existing_product_map:
            return self.existing_product_map[key]

        data = self._get_data_for_table(
            row,
            table_name
        )
        value_set = set(data.values())
        if value_set == {''}:
            return

        product_id = report_db_accessor.insert_on_conflict_do_nothing(
            table_name,
            data,
            conflict_columns=['sku', 'product_name', 'region']
        )
        self.processed_report.products[key] = product_id

        return product_id

    def _create_cost_entry_reservation(self, row, report_db_accessor):
        """Create a cost entry reservation object.

        Args:
            row (dict): A dictionary representation of a CSV file row

        Returns:
            (str): The DB id of the reservation object

        """
        table_name = AWS_CUR_TABLE_MAP['reservation']
        arn = row.get('reservation/ReservationARN')
        line_item_type = row.get('lineItem/LineItemType', '').lower()
        reservation_id = None

        if arn in self.processed_report.reservations:
            reservation_id = self.processed_report.reservations.get(arn)
        elif arn in self.existing_reservation_map:
            reservation_id = self.existing_reservation_map[arn]

        if reservation_id is None or line_item_type == 'rifee':
            data = self._get_data_for_table(
                row,
                table_name
            )
            value_set = set(data.values())
            if value_set == {''}:
                return
        else:
            return reservation_id

        # Special rows with additional reservation information
        if line_item_type == 'rifee':
            reservation_id = report_db_accessor.insert_on_conflict_do_update(
                table_name,
                data,
                conflict_columns=['reservation_arn'],
                set_columns=list(data.keys())
            )
        else:
            reservation_id = report_db_accessor.insert_on_conflict_do_nothing(
                table_name,
                data,
                conflict_columns=['reservation_arn']
            )
        self.processed_report.reservations[arn] = reservation_id

        return reservation_id

    def create_cost_entry_objects(self, row, report_db_accesor):
        """Create the set of objects required for a row of data."""
        bill_id = self._create_cost_entry_bill(row, report_db_accesor)
        cost_entry_id = self._create_cost_entry(row, bill_id, report_db_accesor)
        product_id = self._create_cost_entry_product(row, report_db_accesor)
        pricing_id = self._create_cost_entry_pricing(row, report_db_accesor)
        reservation_id = self._create_cost_entry_reservation(row, report_db_accesor)
        self._create_cost_entry_line_item(
            row,
            cost_entry_id,
            bill_id,
            product_id,
            pricing_id,
            reservation_id,
            report_db_accesor
        )

        return bill_id
