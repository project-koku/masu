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

"""Test the AWSReportProcessor."""
from collections import defaultdict
import csv
import copy
import datetime
from decimal import Decimal
import gzip
from itertools import islice
import json
import random
import shutil
import tempfile

from sqlalchemy.sql.expression import delete

from masu.config import Config
from masu.database import AWS_CUR_TABLE_MAP
from masu.database.report_db_accessor import ReportDBAccessor
from masu.database.report_stats_db_accessor import ReportStatsDBAccessor
from masu.database.reporting_common_db_accessor import ReportingCommonDBAccessor
from masu.exceptions import MasuProcessingError
from masu.external import GZIP_COMPRESSED, UNCOMPRESSED
from masu.processor.aws.aws_report_processor import AWSReportProcessor, ProcessedReport
import masu.util.common as common_util
from tests import MasuTestCase


class ProcessedReportTest(MasuTestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the test class with required objects."""
        cls.report = ProcessedReport()

    def test_remove_processed_rows(self):
        test_entry = {'test': 'entry'}
        self.report.cost_entries.update(test_entry)
        self.report.line_items.append(test_entry)
        self.report.products.update(test_entry)
        self.report.pricing.update(test_entry)
        self.report.reservations.update(test_entry)

        self.report.remove_processed_rows()

        self.assertEqual(self.report.cost_entries, {})
        self.assertEqual(self.report.line_items, [])
        self.assertEqual(self.report.products, {})
        self.assertEqual(self.report.pricing, {})
        self.assertEqual(self.report.reservations, {})


class AWSReportProcessorTest(MasuTestCase):
    """Test Cases for the AWSReportProcessor object."""

    @classmethod
    def setUpClass(cls):
        """Set up the test class with required objects."""
        cls.test_report = './tests/data/test_cur.csv'
        cls.test_report_gzip = './tests/data/test_cur.csv.gz'

        cls.processor = AWSReportProcessor(
            schema_name='testcustomer',
            report_path=cls.test_report,
            compression=UNCOMPRESSED,
        )

        cls.accessor = cls.processor.report_db
        cls.report_schema = cls.accessor.report_schema
        cls.session = cls.accessor._session


        _report_tables = copy.deepcopy(AWS_CUR_TABLE_MAP)
        _report_tables.pop('line_item_daily', None)
        _report_tables.pop('line_item_daily_summary', None)
        _report_tables.pop('line_item_aggregates', None)
        cls.report_tables = list(_report_tables.values())
        # Grab a single row of test data to work with
        with open(cls.test_report, 'r') as f:
            reader = csv.DictReader(f)
            cls.row = next(reader)

    @classmethod
    def tearDownClass(cls):
        cls.accessor.close_connections()
        cls.accessor.close_session()

    def tearDown(self):
        """Return the database to a pre-test state."""
        self.session.rollback()

        for table_name in self.report_tables:
            self.accessor._cursor.execute(f'DELETE FROM {table_name}')
        self.accessor._pg2_conn.commit()

        self.processor.processed_report.remove_processed_rows()

        self.processor.line_item_columns = None

    def test_initializer(self):
        """Test initializer."""
        self.assertIsNotNone(self.processor._schema_name)
        self.assertIsNotNone(self.processor._report_path)
        self.assertIsNotNone(self.processor._report_name)
        self.assertIsNotNone(self.processor._compression)
        self.assertEqual(
            self.processor._datetime_format,
            Config.AWS_DATETIME_STR_FORMAT
        )
        self.assertEqual(
            self.processor._batch_size,
            Config.REPORT_PROCESSING_BATCH_SIZE
        )

    def test_initializer_unsupported_compression(self):
        """Assert that an error is raised for an invalid compression."""
        with self.assertRaises(MasuProcessingError):
            AWSReportProcessor(schema_name='testcustomer',
                               report_path=self.test_report,
                               compression='unsupported')

    def test_process_default(self):
        """Test the processing of an uncompressed file."""
        counts = {}
        processor = AWSReportProcessor(
            schema_name='testcustomer',
            report_path=self.test_report,
            compression=UNCOMPRESSED,
        )
        report_db = processor.report_db
        report_schema = report_db.report_schema
        for table_name in self.report_tables:
            table = getattr(report_schema, table_name)
            count = report_db._session.query(table).count()
            counts[table_name] = count

        processor.process()

        for table_name in self.report_tables:
            table = getattr(report_schema, table_name)
            count = report_db._session.query(table).count()

            if table_name == 'reporting_awscostentryreservation':
                self.assertTrue(count >= counts[table_name])
            else:
                self.assertTrue(count > counts[table_name])

        self.assertTrue(processor.report_db._conn.closed)
        self.assertTrue(processor.report_db._pg2_conn.closed)

    def test_process_gzip(self):
        """Test the processing of a gzip compressed file."""
        counts = {}
        processor = AWSReportProcessor(
            schema_name='testcustomer',
            report_path=self.test_report_gzip,
            compression=GZIP_COMPRESSED
        )
        report_db = processor.report_db
        report_schema = report_db.report_schema
        for table_name in self.report_tables:
            table = getattr(report_schema, table_name)
            count = report_db._session.query(table).count()
            counts[table_name] = count

        processor.process()

        for table_name in self.report_tables:
            table = getattr(report_schema, table_name)
            count = report_db._session.query(table).count()

            if table_name == 'reporting_awscostentryreservation':
                self.assertTrue(count >= counts[table_name])
            else:
                self.assertTrue(count > counts[table_name])

        self.assertTrue(processor.report_db._conn.closed)
        self.assertTrue(processor.report_db._pg2_conn.closed)

    def test_process_duplicates(self):
        """Test that row duplicates are not inserted into the DB."""
        counts = {}
        processor = AWSReportProcessor(
            schema_name='testcustomer',
            report_path=self.test_report,
            compression=UNCOMPRESSED
        )

        # Process for the first time
        processor.process()
        report_db = processor.report_db
        report_schema = report_db.report_schema

        for table_name in self.report_tables:
            table = getattr(report_schema, table_name)
            count = report_db._session.query(table).count()
            counts[table_name] = count

        processor = AWSReportProcessor(
            schema_name='testcustomer',
            report_path=self.test_report,
            compression=UNCOMPRESSED
        )
        # Process for the second time
        processor.process()

        for table_name in self.report_tables:
            table = getattr(report_schema, table_name)
            count = report_db._session.query(table).count()
            self.assertTrue(count == counts[table_name])

    def test_get_file_opener_default(self):
        """Test that the default file opener is returned."""
        opener, mode = self.processor._get_file_opener(UNCOMPRESSED)

        self.assertEqual(opener, open)
        self.assertEqual(mode, 'r')

    def test_get_file_opener_gzip(self):
        """Test that the gzip file opener is returned."""
        opener, mode = self.processor._get_file_opener(GZIP_COMPRESSED)

        self.assertEqual(opener, gzip.open)
        self.assertEqual(mode, 'rt')

    def test_update_mappings(self):
        """Test that mappings are updated."""
        test_entry = {'key': 'value'}
        counts = {}
        ce_maps = {
            'cost_entry': self.processor.existing_cost_entry_map,
            'product': self.processor.existing_product_map,
            'pricing': self.processor.existing_pricing_map,
            'reservation': self.processor.existing_reservation_map
        }

        for name, ce_map in ce_maps.items():
            counts[name] =  len(ce_map.values())
            ce_map.update(test_entry)

        self.processor._update_mappings()

        for name, ce_map in ce_maps.items():
            self.assertTrue(len(ce_map.values()) > counts[name])
            for key in test_entry:
                self.assertIn(key, ce_map)

    def test_write_processed_rows_to_csv(self):
        """Test that the CSV bulk upload file contains proper data."""
        bill_id = self.processor._create_cost_entry_bill(self.row)
        cost_entry_id = self.processor._create_cost_entry(self.row, bill_id)
        product_id = self.processor._create_cost_entry_product(self.row)
        pricing_id = self.processor._create_cost_entry_pricing(self.row)
        reservation_id = self.processor._create_cost_entry_reservation(self.row)
        self.processor._create_cost_entry_line_item(
            self.row,
            cost_entry_id,
            bill_id,
            product_id,
            pricing_id,
            reservation_id
        )

        file_obj = self.processor._write_processed_rows_to_csv()

        line_item_data = self.processor.processed_report.line_items.pop()
        # Convert data to CSV format
        expected_values = [str(value) if value else None
                           for value in line_item_data.values()]

        reader = csv.reader(file_obj)
        new_row = next(reader)
        new_row = new_row[0].split('\t')
        actual = {}

        for i, key in enumerate(line_item_data.keys()):
            actual[key] = new_row[i] if new_row[i] else None

        self.assertEqual(actual.keys(), line_item_data.keys())
        self.assertEqual(list(actual.values()), expected_values)

    def test_get_data_for_table(self):
        """Test that a row is disected into appropriate data structures."""
        column_map = self.processor.report_common_db.column_map

        for table_name in self.report_tables:
            expected_columns = sorted(column_map[table_name].values())
            data = self.processor._get_data_for_table(self.row, table_name)

            for key in data:
                self.assertIn(key, expected_columns)

    def test_process_tags(self):
        """Test that tags are properly packaged in a JSON string."""
        row = {
            'resourceTags\\User': 'value',
            'notATag': 'value',
            'resourceTags\\System': 'value'
        }

        expected = {key: value for key, value in row.items()
                    if 'resourceTags' in key}
        actual = json.loads(self.processor._process_tags(row))

        self.assertNotIn(row['notATag'], actual)
        self.assertEqual(expected, actual)

    def test_get_cost_entry_time_interval(self):
        """Test that an interval string is properly split."""
        fmt = Config.AWS_DATETIME_STR_FORMAT
        end = datetime.datetime.utcnow()
        expected_start = (end - datetime.timedelta(days=1)).strftime(fmt)
        expected_end = end.strftime(fmt)
        interval = expected_start + '/' + expected_end

        actual_start, actual_end = \
            self.processor._get_cost_entry_time_interval(interval)

        self.assertEqual(expected_start, actual_start)
        self.assertEqual(expected_end, actual_end)

    def test_create_cost_entry_bill(self):
        """Test that a cost entry bill id is returned."""
        table_name = AWS_CUR_TABLE_MAP['bill']
        table = getattr(self.report_schema, table_name)
        id_column = getattr(table, 'id')
        bill_id = self.processor._create_cost_entry_bill(self.row)

        self.assertIsNotNone(bill_id)

        query = self.accessor._get_db_obj_query(table_name)
        id_in_db = query.order_by(id_column.desc()).first().id

        self.assertEqual(bill_id, id_in_db)

    def test_create_cost_entry_bill_existing(self):
        """Test that a cost entry bill id is returned from an existing bill."""
        table_name = AWS_CUR_TABLE_MAP['bill']
        table = getattr(self.report_schema, table_name)
        id_column = getattr(table, 'id')
        bill_id = self.processor._create_cost_entry_bill(self.row)

        query = self.accessor._get_db_obj_query(table_name)
        bill = query.first()

        self.processor.current_bill = bill

        new_bill_id = self.processor._create_cost_entry_bill(self.row)

        self.assertEqual(bill_id, new_bill_id)

        self.processor.current_bill = None

    def test_create_cost_entry(self):
        """Test that a cost entry id is returned."""
        table_name = AWS_CUR_TABLE_MAP['cost_entry']
        table = getattr(self.report_schema, table_name)
        id_column = getattr(table, 'id')

        bill_id = self.processor._create_cost_entry_bill(self.row)

        cost_entry_id = self.processor._create_cost_entry(self.row,
                                                          bill_id)
        self.accessor.commit()

        self.assertIsNotNone(cost_entry_id)

        query = self.accessor._get_db_obj_query(table_name)
        id_in_db = query.order_by(id_column.desc()).first().id

        self.assertEqual(cost_entry_id, id_in_db)

    def test_create_cost_entry_existing(self):
        """Test that a cost entry id is returned from an existing entry."""
        table_name = AWS_CUR_TABLE_MAP['cost_entry']
        table = getattr(self.report_schema, table_name)
        id_column = getattr(table, 'id')

        bill_id = self.processor._create_cost_entry_bill(self.row)
        self.accessor.commit()

        interval = self.row.get('identity/TimeInterval')
        start, end = self.processor._get_cost_entry_time_interval(interval)
        expected_id = random.randint(1,9)
        self.processor.existing_cost_entry_map[start] = expected_id

        cost_entry_id = self.processor._create_cost_entry(self.row,
                                                          bill_id)

        self.assertEqual(cost_entry_id, expected_id)

    def test_create_cost_entry_line_item(self):
        """Test that line item data is returned properly."""
        bill_id = self.processor._create_cost_entry_bill(self.row)
        cost_entry_id = self.processor._create_cost_entry(self.row, bill_id)
        product_id = self.processor._create_cost_entry_product(self.row)
        pricing_id = self.processor._create_cost_entry_pricing(self.row)
        reservation_id = self.processor._create_cost_entry_reservation(self.row)

        self.accessor.commit()

        self.processor._create_cost_entry_line_item(
            self.row,
            cost_entry_id,
            bill_id,
            product_id,
            pricing_id,
            reservation_id
        )

        line_item = None
        if self.processor.processed_report.line_items:
            line_item = self.processor.processed_report.line_items[-1]

        data = copy.deepcopy(line_item)
        data.pop('hash')
        data_str = self.processor._create_line_item_hash_string(data)
        hash_str = self.processor.hasher.hash_string_to_hex(data_str)

        self.assertIsNotNone(line_item)
        self.assertIn('tags', line_item)
        self.assertEqual(line_item.get('cost_entry_id'), cost_entry_id)
        self.assertEqual(line_item.get('cost_entry_bill_id'), bill_id)
        self.assertEqual(line_item.get('cost_entry_product_id'), product_id)
        self.assertEqual(line_item.get('cost_entry_pricing_id'), pricing_id)
        self.assertEqual(
            line_item.get('cost_entry_reservation_id'),
            reservation_id
        )
        self.assertEqual(line_item.get('hash'), hash_str)

        self.assertIsNotNone(self.processor.line_item_columns)

    def test_create_cost_entry_product(self):
        """Test that a cost entry product id is returned."""
        table_name = AWS_CUR_TABLE_MAP['product']
        table = getattr(self.report_schema, table_name)
        id_column = getattr(table, 'id')

        product_id = self.processor._create_cost_entry_product(self.row)

        self.accessor.commit()

        self.assertIsNotNone(product_id)

        query = self.accessor._get_db_obj_query(table_name)
        id_in_db = query.order_by(id_column.desc()).first().id

        self.assertEqual(product_id, id_in_db)

    def test_create_cost_entry_product_already_processed(self):
        """Test that an already processed product id is returned."""
        expected_id = random.randint(1,9)
        sku = self.row.get('product/sku')
        product_name = self.row.get('product/ProductName')
        region = self.row.get('product/region')
        key = (sku, product_name, region)
        self.processor.processed_report.products.update({key: expected_id})

        product_id = self.processor._create_cost_entry_product(self.row)

        self.assertEqual(product_id, expected_id)

    def test_create_cost_entry_product_existing(self):
        """Test that a previously existing product id is returned."""
        expected_id = random.randint(1,9)
        sku = self.row.get('product/sku')
        product_name = self.row.get('product/ProductName')
        region = self.row.get('product/region')
        key = (sku, product_name, region)
        self.processor.existing_product_map.update({key: expected_id})

        product_id = self.processor._create_cost_entry_product(self.row)

        self.assertEqual(product_id, expected_id)

    def test_create_cost_entry_pricing(self):
        """Test that a cost entry pricing id is returned."""
        table_name = AWS_CUR_TABLE_MAP['pricing']
        table = getattr(self.report_schema, table_name)
        id_column = getattr(table, 'id')

        pricing_id = self.processor._create_cost_entry_pricing(self.row)

        self.accessor.commit()

        self.assertIsNotNone(pricing_id)

        query = self.accessor._get_db_obj_query(table_name)
        id_in_db = query.order_by(id_column.desc()).first().id

        self.assertEqual(pricing_id, id_in_db)

    def test_create_cost_entry_pricing_already_processed(self):
        """Test that an already processed pricing id is returned."""
        expected_id = random.randint(1,9)

        key = '{term}-{unit}'.format(
            term=self.row['pricing/term'],
            unit=self.row['pricing/unit']
        )
        self.processor.processed_report.pricing.update({key: expected_id})

        pricing_id = self.processor._create_cost_entry_pricing(self.row)

        self.assertEqual(pricing_id, expected_id)

    def test_create_cost_entry_pricing_existing(self):
        """Test that a previously existing pricing id is returned."""
        expected_id = random.randint(1,9)

        key = '{term}-{unit}'.format(
            term=self.row['pricing/term'],
            unit=self.row['pricing/unit']
        )
        self.processor.existing_pricing_map.update({key: expected_id})

        pricing_id = self.processor._create_cost_entry_pricing(self.row)

        self.assertEqual(pricing_id, expected_id)

    def test_create_cost_entry_reservation(self):
        """Test that a cost entry reservation id is returned."""
        # Ensure a reservation exists on the row
        arn = 'TestARN'
        row = copy.deepcopy(self.row)
        row['reservation/ReservationARN'] = arn

        table_name = AWS_CUR_TABLE_MAP['reservation']
        table = getattr(self.report_schema, table_name)
        id_column = getattr(table, 'id')

        reservation_id = self.processor._create_cost_entry_reservation(row)

        self.accessor.commit()

        self.assertIsNotNone(reservation_id)

        query = self.accessor._get_db_obj_query(table_name)
        id_in_db = query.order_by(id_column.desc()).first().id

        self.assertEqual(reservation_id, id_in_db)

    def test_create_cost_entry_reservation_update(self):
        """Test that a cost entry reservation id is returned."""
        # Ensure a reservation exists on the row
        arn = 'TestARN'
        row = copy.deepcopy(self.row)
        row['reservation/ReservationARN'] = arn
        row['reservation/NumberOfReservations'] = 1

        table_name = AWS_CUR_TABLE_MAP['reservation']
        table = getattr(self.report_schema, table_name)
        id_column = getattr(table, 'id')

        reservation_id = self.processor._create_cost_entry_reservation(row)

        self.accessor.commit()

        self.assertIsNotNone(reservation_id)

        query = self.accessor._get_db_obj_query(table_name)
        id_in_db = query.order_by(id_column.desc()).first().id

        self.assertEqual(reservation_id, id_in_db)

        row['lineItem/LineItemType'] = 'RIFee'
        res_count = row['reservation/NumberOfReservations']
        row['reservation/NumberOfReservations'] = res_count + 1
        reservation_id = self.processor._create_cost_entry_reservation(row)
        self.accessor.commit()

        self.assertEqual(reservation_id, id_in_db)

        db_row = query.filter_by(id=id_in_db).first()
        self.assertEqual(db_row.number_of_reservations,
                         row['reservation/NumberOfReservations'])



    def test_create_cost_entry_reservation_already_processed(self):
        """Test that an already processed reservation id is returned."""
        expected_id = random.randint(1,9)
        arn = self.row.get('reservation/ReservationARN')
        self.processor.processed_report.reservations.update({arn: expected_id})

        reservation_id = self.processor._create_cost_entry_reservation(self.row)

        self.assertEqual(reservation_id, expected_id)

    def test_create_cost_entry_reservation_existing(self):
        """Test that a previously existing reservation id is returned."""
        expected_id = random.randint(1,9)
        arn = self.row.get('reservation/ReservationARN')
        self.processor.existing_reservation_map.update({arn: expected_id})

        product_id = self.processor._create_cost_entry_reservation(self.row)

        self.assertEqual(product_id, expected_id)

    def test_get_line_item_hash_columns(self):
        """Test that the correct list of columns is returned."""
        table_name = AWS_CUR_TABLE_MAP['line_item']
        columns = self.processor.column_map[table_name].values()
        expected = [column for column in columns if column != 'invoice_id']

        result = self.processor._get_line_item_hash_columns()

        self.assertEqual(result, expected)

    def test_create_line_item_hash_string(self):
        """Test that a hash string is properly formatted."""
        bill_id = self.processor._create_cost_entry_bill(self.row)
        cost_entry_id = self.processor._create_cost_entry(self.row, bill_id)
        product_id = self.processor._create_cost_entry_product(self.row)
        pricing_id = self.processor._create_cost_entry_pricing(self.row)
        reservation_id = self.processor._create_cost_entry_reservation(self.row)

        self.accessor.commit()

        self.processor._create_cost_entry_line_item(
            self.row,
            cost_entry_id,
            bill_id,
            product_id,
            pricing_id,
            reservation_id
        )

        line_item = None
        if self.processor.processed_report.line_items:
            line_item = self.processor.processed_report.line_items[-1]

        line_item = common_util.stringify_json_data(copy.deepcopy(line_item))
        line_item.pop('hash')
        data = [line_item.get(column, 'None')
                for column in self.processor.hash_columns]
        expected = ':'.join(data)

        result = self.processor._create_line_item_hash_string(line_item)

        self.assertEqual(result, expected)
        result = self.processor._create_line_item_hash_string(line_item)

        self.assertEqual(result, expected)

    def test_remove_temp_cur_files(self):
        """Test to remove temporary cost usage files."""
        cur_dir = tempfile.mkdtemp()

        manifest_data = {"assemblyId": "6e019de5-a41d-4cdb-b9a0-99bfba9a9cb5"}
        manifest = '{}/{}'.format(cur_dir, 'koku-Manifest.json')
        with open(manifest, 'w') as outfile:
            json.dump(manifest_data, outfile)

        file_list = [{'file': '6e019de5-a41d-4cdb-b9a0-99bfba9a9cb5-koku-1.csv.gz',
                      'processed_date': datetime.datetime(year=2018, month=5, day=3)},
                     {'file': '6e019de5-a41d-4cdb-b9a0-99bfba9a9cb5-koku-2.csv.gz',
                      'processed_date': datetime.datetime(year=2018, month=5, day=3)},
                     {'file': '2aeb9169-2526-441c-9eca-d7ed015d52bd-koku-1.csv.gz',
                      'processed_date': datetime.datetime(year=2018, month=5, day=2)},
                     {'file': '6c8487e8-c590-4e6a-b2c2-91a2375c0bad-koku-1.csv.gz',
                      'processed_date': datetime.datetime(year=2018, month=5, day=1)},
                     {'file': '6c8487e8-c590-4e6a-b2c2-91a2375d0bed-koku-1.csv.gz',
                      'processed_date': None}]
        expected_delete_list = []
        for item in file_list:
            path = '{}/{}'.format(cur_dir, item['file'])
            f = open(path, 'w')
            stats = ReportStatsDBAccessor(item['file'])
            stats.update(last_completed_datetime=item['processed_date'])
            stats.commit()
            stats.close_session()
            f.close()
            if not item['file'].startswith(manifest_data.get('assemblyId')) and item['processed_date']:
                expected_delete_list.append(path)

        removed_files = self.processor.remove_temp_cur_files(cur_dir)
        self.assertEqual(sorted(removed_files), sorted(expected_delete_list))
        shutil.rmtree(cur_dir)
