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

"""Test the OCPReportDBAccessor utility object."""
from dateutil.relativedelta import relativedelta
from unittest.mock import patch
from decimal import Decimal

import psycopg2

from masu.database import OCP_REPORT_TABLE_MAP
from masu.database.ocp_report_db_accessor import OCPReportDBAccessor
from masu.database.reporting_common_db_accessor import ReportingCommonDBAccessor
from masu.processor.ocp.ocp_report_charge_updater import OCPReportChargeUpdater
from tests import MasuTestCase
from tests.database.helpers import ReportObjectCreator


class OCPReportChargeUpdaterTest(MasuTestCase):
    """Test Cases for the OCPReportChargeUpdater object."""

    @classmethod
    def setUpClass(cls):
        """Set up the test class with required objects."""
        cls.common_accessor = ReportingCommonDBAccessor()
        cls.column_map = cls.common_accessor.column_map
        cls.accessor = OCPReportDBAccessor(
            schema='acct10001org20002',
            column_map=cls.column_map
        )
        cls.updater = OCPReportChargeUpdater(
            schema='acct10001org20002',
            provider_uuid='6e212746-484a-40cd-bba0-09a19d132d64'
        )
        cls.report_schema = cls.accessor.report_schema
        cls.creator = ReportObjectCreator(
            cls.accessor,
            cls.column_map,
            cls.report_schema.column_types
        )
        cls.all_tables = list(OCP_REPORT_TABLE_MAP.values())

    @classmethod
    def tearDownClass(cls):
        """Close the DB session."""
        cls.accessor.close_session()
        cls.updater.close_session()

    def setUp(self):
        """"Set up a test with database objects."""
        super().setUp()
        if self.accessor._conn.closed:
            self.accessor._conn = self.accessor._db.connect()
        if self.accessor._pg2_conn.closed:
            self.accessor._pg2_conn = self.accessor._get_psycopg2_connection()
        if self.accessor._cursor.closed:
            self.accessor._cursor = self.accessor._get_psycopg2_cursor()

        reporting_period = self.creator.create_ocp_report_period()

        report = self.creator.create_ocp_report(reporting_period, reporting_period.report_period_start)
        self.creator.create_ocp_usage_line_item(
            reporting_period,
            report
        )

    def tearDown(self):
        """Return the database to a pre-test state."""
        self.accessor._session.rollback()

        for table_name in self.all_tables:
            tables = self.accessor._get_db_obj_query(table_name).all()
            for table in tables:
                self.accessor._session.delete(table)

    @patch('masu.database.ocp_rate_db_accessor.OCPRateDBAccessor.get_cpu_rates')
    @patch('masu.database.ocp_rate_db_accessor.OCPRateDBAccessor.get_memory_rates')
    def test_update_summary_charge_info_cpu(self, mock_db_mem_rate, mock_db_cpu_rate):
        """Test that OCP charge information is updated for cpu."""
        cpu_rate = {'fixed_rate': {'value': '200', 'unit': 'USD'}}
        cpu_rate_value = float(cpu_rate.get('fixed_rate').get('value'))
        mock_db_cpu_rate.return_value = cpu_rate
        mock_db_mem_rate.return_value = None

        usage_period = self.accessor.get_current_usage_period()
        start_date = usage_period.report_period_start.date() + relativedelta(days=-1)
        end_date = usage_period.report_period_end.date() + relativedelta(days=+1)

        self.accessor.populate_line_item_daily_table(start_date, end_date)
        self.accessor.populate_line_item_daily_summary_table(start_date, end_date)

        self.updater.update_summary_charge_info()

        table_name = OCP_REPORT_TABLE_MAP['line_item_daily_summary']
        items = self.accessor._get_db_obj_query(table_name).all()
        for item in items:
            max_cpu_value = float(max(item.pod_usage_cpu_core_hours, item.pod_request_cpu_core_hours))
            self.assertEqual(round(max_cpu_value*cpu_rate_value, 3),
                             round(float(item.pod_charge_cpu_cores), 3))

    @patch('masu.database.ocp_rate_db_accessor.OCPRateDBAccessor.get_cpu_rates')
    @patch('masu.database.ocp_rate_db_accessor.OCPRateDBAccessor.get_memory_rates')
    def test_update_summary_charge_info_mem(self, mock_db_mem_rate, mock_db_cpu_rate):
        """Test that OCP charge information is updated for memory."""
        mem_rate = {'fixed_rate': {'value': '100', 'unit': 'USD'}}
        mem_rate_value = float(mem_rate.get('fixed_rate').get('value'))
        mock_db_mem_rate.return_value = mem_rate
        mock_db_cpu_rate.return_value = None

        usage_period = self.accessor.get_current_usage_period()
        start_date = usage_period.report_period_start.date() + relativedelta(days=-1)
        end_date = usage_period.report_period_end.date() + relativedelta(days=+1)

        self.accessor.populate_line_item_daily_table(start_date, end_date)
        self.accessor.populate_line_item_daily_summary_table(start_date, end_date)

        self.updater.update_summary_charge_info()

        table_name = OCP_REPORT_TABLE_MAP['line_item_daily_summary']

        items = self.accessor._get_db_obj_query(table_name).all()
        for item in items:
            max_mem_value = float(max(item.pod_usage_memory_gigabytes, item.pod_request_memory_gigabytes))
            self.assertEqual(round(max_mem_value*mem_rate_value, 3),
                             round(float(item.pod_charge_memory_gigabytes), 3))

    @patch('masu.database.ocp_rate_db_accessor.OCPRateDBAccessor.get_cpu_rates')
    @patch('masu.database.ocp_rate_db_accessor.OCPRateDBAccessor.get_memory_rates')
    def test_update_summary_charge_info_mem_cpu(self, mock_db_mem_rate, mock_db_cpu_rate):
        """Test that OCP charge information is updated for cpu and memory."""
        mem_rate = {'fixed_rate': {'value': '100', 'unit': 'USD'}}
        cpu_rate = {'fixed_rate': {'value': '200', 'unit': 'USD'}}

        cpu_rate_value = float(cpu_rate.get('fixed_rate').get('value'))
        mem_rate_value = float(mem_rate.get('fixed_rate').get('value'))

        mock_db_mem_rate.return_value = mem_rate
        mock_db_cpu_rate.return_value = cpu_rate

        usage_period = self.accessor.get_current_usage_period()
        start_date = usage_period.report_period_start.date() + relativedelta(days=-1)
        end_date = usage_period.report_period_end.date() + relativedelta(days=+1)

        self.accessor.populate_line_item_daily_table(start_date, end_date)
        self.accessor.populate_line_item_daily_summary_table(start_date, end_date)
        self.updater.update_summary_charge_info()

        table_name = OCP_REPORT_TABLE_MAP['line_item_daily_summary']

        items = self.accessor._get_db_obj_query(table_name).all()
        for item in items:
            max_cpu_value = float(max(item.pod_usage_cpu_core_hours, item.pod_request_cpu_core_hours))
            max_mem_value = float(max(item.pod_usage_memory_gigabytes, item.pod_request_memory_gigabytes))
            self.assertEqual(round(max_mem_value*mem_rate_value, 3),
                             round(float(item.pod_charge_memory_gigabytes), 3))
            self.assertEqual(round(max_cpu_value*cpu_rate_value, 3),
                             round(float(item.pod_charge_cpu_cores), 3))

    def test_get_tier_rate(self):
        """Test the tier helper function."""
        rate_json = {"tiered_rate": [{
            "usage_start": "0E-10",
            "usage_end": "10",
            "value": "0.12",
            "unit": "USD"
        },
        {
            "usage_start": "11",
            "usage_end": "20",
            "value": "0.14",
            "unit": "USD"
        },
        {
            "usage_start": "21",
            "usage_end": None,
            "value": "0.18",
            "unit": "USD"
        }]}
        test_matrix = [{'usage': 5, 'expected_rate': 0.12},
                       {'usage': 15, 'expected_rate': 0.14},
                       {'usage': 25, 'expected_rate': 0.18}]

        for test in test_matrix:
            tier_rate = self.updater._get_tier_rate(rate_json.get('tiered_rate'), test.get('usage'))
            self.assertEqual(round(float(tier_rate), 2), test.get('expected_rate'))

    def test_calculate_rate(self):
        """Test the tier helper function to calculate total rate."""
        rate_json = {"tiered_rate": [{
            "usage_start": None,
            "usage_end": "10",
            "value": "0.12",
            "unit": "USD"
        },
        {
            "usage_start": "11",
            "usage_end": "20",
            "value": "0.14",
            "unit": "USD"
        },
        {
            "usage_start": '21',
            "value": '0.18',
            "unit": "USD"
        }],
        'fixed_rate': 
        {
            'value': '100',
            'unit': 'USD'
        }}
        test_matrix = [{'usage': 5, 'expected_rate': 100.12},
                       {'usage': 15, 'expected_rate': 100.14},
                       {'usage': 25, 'expected_rate': 100.18}]

        for test in test_matrix:
            tier_rate = self.updater._calculate_rate(rate_json, test.get('usage'))
            self.assertEqual(round(float(tier_rate), 2), test.get('expected_rate'))

    def test_calculate_charge(self):
        """Test the helper function to calculate charge."""
        rate_json = {"tiered_rate": [{
            "usage_start": None,
            "usage_end": "10",
            "value": "0.12",
            "unit": "USD"
        },
        {
            "usage_start": "11",
            "usage_end": "20",
            "value": "0.14",
            "unit": "USD"
        },
        {
            "usage_start": '21',
            "usage_end": None,
            "value": '0.18',
            "unit": "USD"
        }],
        'fixed_rate': 
        {
            'value': '100',
            'unit': 'USD'
        }}
        usage_dictionary = {1: Decimal(5), 2: Decimal(15), 3: Decimal(25)}

        expected_results = {1: {'expected_rate': 100.12, 'expected_charge': Decimal(500.6)},
                            2: {'expected_rate': 100.14, 'expected_charge': Decimal(1502.1)},
                            3: {'expected_rate': 100.18, 'expected_charge': Decimal(2504.5)}}

        charge_dictionary = self.updater._calculate_charge(rate_json, usage_dictionary)

        for key, entry in expected_results.items():
            calculated_charge = charge_dictionary[key].get('charge')
            self.assertEqual(round(float(calculated_charge), 1), entry.get('expected_charge'))
