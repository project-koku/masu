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
import calendar
import datetime
import logging
from unittest.mock import patch

from masu.database import OCP_REPORT_TABLE_MAP
from masu.database.ocp_report_db_accessor import OCPReportDBAccessor
from masu.database.report_manifest_db_accessor import ReportManifestDBAccessor
from masu.database.reporting_common_db_accessor import ReportingCommonDBAccessor
from masu.external.date_accessor import DateAccessor
from masu.processor.ocp.ocp_report_summary_updater import OCPReportSummaryUpdater

from tests import MasuTestCase
from tests.database.helpers import ReportObjectCreator


class OCPReportSummaryUpdaterTest(MasuTestCase):
    """Test cases for the OCPReportSummaryUpdater class."""

    @classmethod
    def setUpClass(cls):
        """Set up the test class with required objects."""
        super().setUpClass()
        cls.common_accessor = ReportingCommonDBAccessor()
        cls.column_map = cls.common_accessor.column_map
        cls.updater = OCPReportSummaryUpdater(schema='acct10001org20002')

        cls.accessor = cls.updater._accessor
        cls.report_schema = cls.accessor.report_schema
        cls.session = cls.accessor._session

        cls.all_tables = list(OCP_REPORT_TABLE_MAP.values())

        cls.creator = ReportObjectCreator(
            cls.accessor,
            cls.column_map,
            cls.report_schema.column_types
        )

        cls.date_accessor = DateAccessor()
        billing_start = cls.date_accessor.today_with_timezone('UTC').replace(day=1)
        cls.manifest_dict = {
            'assembly_id': '1234',
            'billing_period_start_datetime': billing_start,
            'num_total_files': 2,
            'provider_id': 1
        }
        cls.manifest_accessor = ReportManifestDBAccessor()

    @classmethod
    def tearDownClass(cls):
        """Tear down the test class."""
        super().tearDownClass()
        cls.updater.close_session()
        cls.common_accessor.close_session()

    def setUp(self):
        """Set up each test."""
        super().setUp()
        if self.accessor._conn.closed:
            self.accessor._conn = self.accessor._db.connect()
        if self.accessor._pg2_conn.closed:
            self.accessor._pg2_conn = self.accessor._get_psycopg2_connection()
        if self.accessor._cursor.closed:
            self.accessor._cursor = self.accessor._get_psycopg2_cursor()

        today = DateAccessor().today_with_timezone('UTC')
        report_period = self.creator.create_ocp_report_period(today)
        report = self.creator.create_ocp_report(report_period, today)
        self.creator.create_ocp_usage_line_item(
            report_period,
            report
        )
        self.manifest = self.manifest_accessor.add(self.manifest_dict)
        self.manifest_accessor.commit()

    def tearDown(self):
        """Return the database to a pre-test state."""
        super().tearDown()

        for table_name in self.all_tables:
            tables = self.accessor._get_db_obj_query(table_name).all()
            for table in tables:
                self.accessor._session.delete(table)
        self.accessor.commit()

        manifests = self.manifest_accessor._get_db_obj_query().all()
        for manifest in manifests:
            self.manifest_accessor.delete(manifest)
        self.manifest_accessor.commit()

    @patch('masu.processor.ocp.ocp_report_summary_updater.OCPReportDBAccessor.populate_line_item_aggregate_table')
    @patch('masu.processor.ocp.ocp_report_summary_updater.OCPReportDBAccessor.populate_line_item_daily_summary_table')
    @patch('masu.processor.ocp.ocp_report_summary_updater.OCPReportDBAccessor.populate_line_item_daily_table')
    def test_update_summary_tables_with_manifest(self, mock_daily, mock_sum,
                                                 mock_agg):
        """Test that summary tables are properly run."""
        self.manifest.num_processed_files = self.manifest.num_total_files
        manifest_id = self.manifest.id
        self.manifest_accessor.commit()

        start_date = self.date_accessor.today_with_timezone('UTC')
        end_date = start_date + datetime.timedelta(days=1)
        bill_date = start_date.replace(day=1).date()

        period = self.accessor.get_usage_periods_by_date(bill_date)[0]
        period.summary_data_creation_datetime = start_date
        self.accessor.commit()

        expected_start_date = start_date.strftime('%Y-%m-%d')
        expected_end_date = end_date.strftime('%Y-%m-%d')

        self.assertIsNone(period.summary_data_updated_datetime)

        self.updater.update_summary_tables(
            start_date,
            end_date,
            manifest_id
        )

        mock_daily.assert_called_with(expected_start_date, expected_end_date)
        mock_sum.assert_called_with(expected_start_date, expected_end_date)
        mock_agg.assert_called()

        self.assertIsNotNone(period.summary_data_creation_datetime)
        self.assertIsNotNone(period.summary_data_updated_datetime)

    @patch('masu.processor.ocp.ocp_report_summary_updater.OCPReportDBAccessor.populate_line_item_aggregate_table')
    @patch('masu.processor.ocp.ocp_report_summary_updater.OCPReportDBAccessor.populate_line_item_daily_summary_table')
    @patch('masu.processor.ocp.ocp_report_summary_updater.OCPReportDBAccessor.populate_line_item_daily_table')
    def test_update_summary_tables_new_period(self, mock_daily, mock_sum,
                                              mock_agg):
        """Test that summary tables are run for a full month."""

        self.manifest.num_processed_files = self.manifest.num_total_files
        manifest_id = self.manifest.id
        self.manifest_accessor.commit()

        start_date = self.date_accessor.today_with_timezone('UTC')
        end_date = start_date + datetime.timedelta(days=1)
        bill_date = start_date.replace(day=1).date()

        period = self.accessor.get_usage_periods_by_date(bill_date)[0]

        last_day_of_month = calendar.monthrange(
                    bill_date.year,
                    bill_date.month
                )[1]

        expected_start_date = start_date.replace(day=1).strftime('%Y-%m-%d')
        expected_end_date = end_date.replace(day=last_day_of_month)\
            .strftime('%Y-%m-%d')

        self.assertIsNone(period.summary_data_creation_datetime)
        self.assertIsNone(period.summary_data_updated_datetime)

        self.updater.update_summary_tables(
            start_date,
            end_date,
            manifest_id
        )

        mock_daily.assert_called_with(expected_start_date, expected_end_date)
        mock_sum.assert_called_with(expected_start_date, expected_end_date)
        mock_agg.assert_called()

        self.assertIsNotNone(period.summary_data_creation_datetime)
        self.assertIsNotNone(period.summary_data_updated_datetime)

    @patch('masu.processor.ocp.ocp_report_summary_updater.OCPReportDBAccessor.populate_line_item_aggregate_table')
    @patch('masu.processor.ocp.ocp_report_summary_updater.OCPReportDBAccessor.populate_line_item_daily_summary_table')
    @patch('masu.processor.ocp.ocp_report_summary_updater.OCPReportDBAccessor.populate_line_item_daily_table')
    def test_update_summary_tables_new_period_last_month(self, mock_daily,
                                                         mock_sum, mock_agg):
        """Test that summary tables are run for the month of the manifest."""
        billing_start = self.date_accessor.today_with_timezone('UTC').replace(day=1)
        billing_start = billing_start.replace(month=(billing_start.month - 1))
        manifest_dict = {
            'assembly_id': '1234',
            'billing_period_start_datetime': billing_start,
            'num_total_files': 2,
            'provider_id': 1
        }
        self.manifest_accessor.delete(self.manifest)
        self.manifest_accessor.commit()
        self.manifest = self.manifest_accessor.add(manifest_dict)
        self.manifest_accessor.commit()

        self.manifest.num_processed_files = self.manifest.num_total_files
        manifest_id = self.manifest.id
        self.manifest_accessor.commit()

        start_date = self.date_accessor.today_with_timezone('UTC')
        end_date = start_date + datetime.timedelta(days=1)
        bill_date = billing_start.date()

        self.creator.create_ocp_report_period(billing_start)
        period = self.accessor.get_usage_periods_by_date(bill_date)[0]

        last_day_of_month = calendar.monthrange(
                    bill_date.year,
                    bill_date.month
                )[1]

        expected_start_date = bill_date.strftime('%Y-%m-%d')
        expected_end_date = bill_date.replace(day=last_day_of_month)\
            .strftime('%Y-%m-%d')

        self.assertIsNone(period.summary_data_creation_datetime)
        self.assertIsNone(period.summary_data_updated_datetime)

        self.updater.update_summary_tables(
            start_date,
            end_date,
            manifest_id
        )

        mock_daily.assert_called_with(expected_start_date, expected_end_date)
        mock_sum.assert_called_with(expected_start_date, expected_end_date)
        mock_agg.assert_called()

        self.assertIsNotNone(period.summary_data_creation_datetime)
        self.assertIsNotNone(period.summary_data_updated_datetime)

    @patch('masu.processor.ocp.ocp_report_summary_updater.OCPReportDBAccessor.populate_line_item_aggregate_table')
    @patch('masu.processor.ocp.ocp_report_summary_updater.OCPReportDBAccessor.populate_line_item_daily_summary_table')
    @patch('masu.processor.ocp.ocp_report_summary_updater.OCPReportDBAccessor.populate_line_item_daily_table')
    def test_update_summary_tables_new_period_not_done_processing(self,
                                                                  mock_daily,
                                                                  mock_sum,
                                                                  mock_agg):
        """Test that summary tables are not run for a full month."""

        manifest_id = self.manifest.id

        start_date = self.date_accessor.today_with_timezone('UTC')
        end_date = start_date + datetime.timedelta(days=1)
        bill_date = start_date.replace(day=1).date()

        period = self.accessor.get_usage_periods_by_date(bill_date)[0]

        expected_start_date = start_date.strftime('%Y-%m-%d')
        expected_end_date = end_date.strftime('%Y-%m-%d')

        self.assertIsNone(period.summary_data_creation_datetime)
        self.assertIsNone(period.summary_data_updated_datetime)

        self.updater.update_summary_tables(
            start_date,
            end_date,
            manifest_id
        )

        mock_daily.assert_called_with(expected_start_date, expected_end_date)
        mock_sum.assert_called_with(expected_start_date, expected_end_date)
        mock_agg.assert_called()

        self.assertIsNotNone(period.summary_data_creation_datetime)
        self.assertIsNotNone(period.summary_data_updated_datetime)

    @patch('masu.processor.ocp.ocp_report_summary_updater.OCPReportDBAccessor.populate_line_item_aggregate_table')
    @patch('masu.processor.ocp.ocp_report_summary_updater.OCPReportDBAccessor.populate_line_item_daily_summary_table')
    @patch('masu.processor.ocp.ocp_report_summary_updater.OCPReportDBAccessor.populate_line_item_daily_table')
    def test_update_summary_tables_without_manifest(self, mock_daily, mock_sum,
                                                    mock_agg):
        """Test that summary tables are properly run without a manifest."""

        start_date = DateAccessor().today_with_timezone('UTC')
        end_date = start_date + datetime.timedelta(days=1)
        bill_date = start_date.replace(day=1).date()

        period = self.accessor.get_usage_periods_by_date(bill_date)[0]
        period.summary_data_updated_datetime = start_date
        self.accessor.commit()

        expected_start_date = start_date.strftime('%Y-%m-%d')
        expected_end_date = end_date.strftime('%Y-%m-%d')

        self.updater.update_summary_tables(
            start_date,
            end_date
        )

        mock_daily.assert_called_with(expected_start_date, expected_end_date)
        mock_sum.assert_called_with(expected_start_date, expected_end_date)
        mock_agg.assert_called()

        self.assertIsNotNone(period.summary_data_creation_datetime)
        self.assertGreater(period.summary_data_updated_datetime, start_date)
