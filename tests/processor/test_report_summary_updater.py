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

"""Test the ReportSummaryUpdater object."""

import datetime
import uuid
from unittest.mock import patch

import pytz

from masu.external import (AMAZON_WEB_SERVICES,
                           AWS_LOCAL_SERVICE_PROVIDER,
                           OPENSHIFT_CONTAINER_PLATFORM,
                           OCP_LOCAL_SERVICE_PROVIDER)
from masu.external.date_accessor import DateAccessor
from masu.processor.aws.aws_report_summary_updater import AWSReportSummaryUpdater
from masu.processor.ocp.ocp_report_summary_updater import OCPReportSummaryUpdater
from masu.processor.report_summary_updater import (ReportSummaryUpdater,
                                                   ReportSummaryUpdaterError)
from tests import MasuTestCase


class ReportSummaryUpdaterTest(MasuTestCase):
    """Test class for the report summary updater."""

    @classmethod
    def setUpClass(cls):
        """Set up the test class."""
        super().setUpClass()
        cls.schema = 'acct10001'
        today = DateAccessor().today_with_timezone('UTC')
        cls.today = today.strftime('%Y-%m-%d')
        cls.tomorrow = (today + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    @patch('masu.processor.report_summary_updater.OCPCloudReportSummaryUpdater.update_summary_tables')
    @patch('masu.processor.report_summary_updater.AWSReportSummaryUpdater.update_summary_tables')
    def test_aws_route(self, mock_update, mock_cloud):
        """Test that AWS report updating works as expected."""
        mock_start = 1
        mock_end = 2
        mock_update.return_value = (mock_start, mock_end)
        updater = ReportSummaryUpdater(self.schema, self.aws_test_provider_uuid)
        self.assertIsInstance(updater._updater, AWSReportSummaryUpdater)
        updater.update_summary_tables(self.today, self.tomorrow)
        mock_update.assert_called_with(self.today, self.tomorrow, self.aws_test_provider_uuid, None)
        mock_cloud.assert_called_with(mock_start, mock_end, self.aws_test_provider_uuid, None)

    @patch('masu.processor.report_summary_updater.OCPCloudReportSummaryUpdater.update_summary_tables')
    @patch('masu.processor.report_summary_updater.AWSReportSummaryUpdater.update_summary_tables')
    def test_aws_local_route(self, mock_update, mock_cloud):
        """Test that AWS Local report updating works as expected."""
        mock_start = 1
        mock_end = 2
        mock_update.return_value = (mock_start, mock_end)
        updater = ReportSummaryUpdater(self.schema, self.aws_test_provider_uuid)
        self.assertIsInstance(updater._updater, AWSReportSummaryUpdater)
        updater.update_summary_tables(self.today, self.tomorrow)
        mock_update.assert_called_with(self.today, self.tomorrow, self.aws_test_provider_uuid, None)
        mock_cloud.assert_called_with(mock_start, mock_end, self.aws_test_provider_uuid, None)

    @patch('masu.processor.report_summary_updater.OCPCloudReportSummaryUpdater.update_summary_tables')
    @patch('masu.processor.report_summary_updater.OCPReportSummaryUpdater.update_summary_tables')
    def test_ocp_route(self, mock_update, mock_cloud):
        """Test that OCP report updating works as expected."""
        mock_start = 1
        mock_end = 2
        mock_update.return_value = (mock_start, mock_end)
        updater = ReportSummaryUpdater(self.schema, self.ocp_test_provider_uuid)
        self.assertIsInstance(updater._updater, OCPReportSummaryUpdater)
        updater.update_summary_tables(self.today, self.tomorrow)
        mock_update.assert_called_with(self.today, self.tomorrow, self.ocp_test_provider_uuid, None)
        mock_cloud.assert_called_with(mock_start, mock_end, self.ocp_test_provider_uuid, None)

    @patch('masu.processor.report_summary_updater.OCPCloudReportSummaryUpdater.update_summary_tables')
    @patch('masu.processor.report_summary_updater.OCPReportSummaryUpdater.update_summary_tables')
    def test_ocp_local_route(self, mock_update, mock_cloud):
        """Test that OCP Local report updating works as expected."""
        mock_start = 1
        mock_end = 2
        mock_update.return_value = (mock_start, mock_end)
        updater = ReportSummaryUpdater(self.schema, self.ocp_test_provider_uuid)
        self.assertIsInstance(updater._updater, OCPReportSummaryUpdater)
        updater.update_summary_tables(self.today, self.tomorrow)
        mock_update.assert_called_with(self.today, self.tomorrow, self.ocp_test_provider_uuid, None)
        mock_cloud.assert_called_with(mock_start, mock_end, self.ocp_test_provider_uuid, None)

    def test_bad_provider(self):
        """Test that an unimplemented provider throws an error."""
        with self.assertRaises(ReportSummaryUpdaterError):
            random_uuid = str(uuid.uuid4())
            _ = ReportSummaryUpdater(self.schema, random_uuid)
