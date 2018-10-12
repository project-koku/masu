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

"""Test the OCPReportProcessor."""
import csv
import copy
import gzip
import shutil
import tempfile

from sqlalchemy.sql.expression import delete

from masu.database import OCP_REPORT_TABLE_MAP
from masu.exceptions import MasuProcessingError
from masu.external import GZIP_COMPRESSED, UNCOMPRESSED
from masu.processor.ocp.ocp_report_processor import OCPReportProcessor, ProcessedOCPReport
from tests import MasuTestCase


class ProcessedOCPReportTest(MasuTestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the test class with required objects."""
        cls.report = ProcessedOCPReport()

    def test_remove_processed_rows(self):
        test_entry = {'test': 'entry'}
        self.report.report_periods.update(test_entry)
        self.report.line_items.append(test_entry)
        self.report.reports.update(test_entry)

        self.report.remove_processed_rows()

        self.assertEqual(self.report.report_periods, {})
        self.assertEqual(self.report.line_items, [])
        self.assertEqual(self.report.reports, {})


class OCPReportProcessorTest(MasuTestCase):
    """Test Cases for the OCPReportProcessor object."""

    @classmethod
    def setUpClass(cls):
        """Set up the test class with required objects."""
        # These test reports should be replaced with OCP reports once processor is impelmented.
        cls.test_report = './tests/data/ocp/1a6e1405-d964-4749-aa5b-104f8d280a3b_pod-cpu-usage-ocp.csv'
        cls.test_report_gzip = './tests/data/test_cur.csv.gz'

        cls.processor = OCPReportProcessor(
            schema_name='acct10001org20002',
            report_path=cls.test_report,
            compression=UNCOMPRESSED,
            provider_id=1
        )

        cls.accessor = cls.processor.report_db
        cls.report_schema = cls.accessor.report_schema
        cls.session = cls.accessor._session

        _report_tables = copy.deepcopy(OCP_REPORT_TABLE_MAP)
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
        self.assertIsNotNone(self.processor._compression)

    def test_initializer_unsupported_compression(self):
        """Assert that an error is raised for an invalid compression."""
        with self.assertRaises(MasuProcessingError):
            OCPReportProcessor(schema_name='acct10001org20002',
                               report_path=self.test_report,
                               compression='unsupported',
                               provider_id=1)

    def test_process_default(self):
        """Test the processing of an uncompressed file."""
        counts = {}
        processor = OCPReportProcessor(
            schema_name='acct10001org20002',
            report_path=self.test_report,
            compression=UNCOMPRESSED,
            provider_id=1
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
            if table_name not in ('reporting_ocpusagelineitem_daily', 'reporting_ocpusagelineitem_daily_summary'):
                self.assertTrue(count >= counts[table_name])

        self.assertTrue(processor.report_db._conn.closed)
        self.assertTrue(processor.report_db._pg2_conn.closed)

    def test_process_duplicates(self):
        """Test that row duplicates are not inserted into the DB."""
        counts = {}
        processor = OCPReportProcessor(
            schema_name='acct10001org20002',
            report_path=self.test_report,
            compression=UNCOMPRESSED,
            provider_id=1
        )

        # Process for the first time
        processor.process()

        report_db = processor.report_db
        report_schema = report_db.report_schema

        for table_name in self.report_tables:
            table = getattr(report_schema, table_name)
            count = report_db._session.query(table).count()
            counts[table_name] = count

        processor = OCPReportProcessor(
            schema_name='acct10001org20002',
            report_path=self.test_report,
            compression=UNCOMPRESSED,
            provider_id=1
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
            'report_periods': self.processor.existing_report_periods_map,
            'reports': self.processor.existing_report_map,
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
        cluster_id = '12345'
        report_period_id = self.processor._create_report_period(self.row, cluster_id)
        report_id = self.processor._create_report(self.row, report_period_id)
        self.processor._create_usage_report_line_item(
            self.row,
            report_period_id,
            report_id
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

    def test_create_report_period(self):
        """Test that a report period id is returned."""
        table_name = OCP_REPORT_TABLE_MAP['report_period']
        table = getattr(self.report_schema, table_name)
        id_column = getattr(table, 'id')
        cluster_id = '12345'
        report_period_id = self.processor._create_report_period(self.row, cluster_id)

        self.assertIsNotNone(report_period_id)

        query = self.accessor._get_db_obj_query(table_name)
        id_in_db = query.order_by(id_column.desc()).first().id

        self.assertEqual(report_period_id, id_in_db)

    def test_create_report(self):
        """Test that a report id is returned."""
        table_name = OCP_REPORT_TABLE_MAP['report']
        table = getattr(self.report_schema, table_name)
        id_column = getattr(table, 'id')
        cluster_id = '12345'
        report_period_id = self.processor._create_report_period(self.row, cluster_id)

        report_id = self.processor._create_report(self.row, report_period_id)
        self.accessor.commit()

        self.assertIsNotNone(report_id)

        query = self.accessor._get_db_obj_query(table_name)
        id_in_db = query.order_by(id_column.desc()).first().id

        self.assertEqual(report_id, id_in_db)

    def test_create_usage_report_line_item(self):
        """Test that line item data is returned properly."""
        cluster_id = '12345'
        report_period_id = self.processor._create_report_period(self.row, cluster_id)
        report_id = self.processor._create_report(self.row, report_period_id)

        self.processor._create_usage_report_line_item(
            self.row,
            report_period_id,
            report_id
        )

        line_item = None
        if self.processor.processed_report.line_items:
            line_item = self.processor.processed_report.line_items[-1]

        self.assertIsNotNone(line_item)
        self.assertEqual(line_item.get('report_period_id'), report_period_id)
        self.assertEqual(line_item.get('report_id'), report_id)

        self.assertIsNotNone(self.processor.line_item_columns)

    def test_remove_temp_cur_files(self):
        """Test to remove temporary usage report files."""
        # Update once temporary file logic is implemented.
        cur_dir = tempfile.mkdtemp()
        manifest_id = 1
        expected_delete_list = []

        removed_files = self.processor.remove_temp_cur_files(cur_dir, manifest_id)
        self.assertEqual(sorted(removed_files), sorted(expected_delete_list))

        shutil.rmtree(cur_dir)
