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

"""Test the Orchestrator object."""

from unittest.mock import patch

from masu.external import AMAZON_WEB_SERVICES
from masu.external.report_downloader import ReportDownloaderError
from masu.processor.orchestrator import Orchestrator
from masu.processor.cur_process_request import CURProcessRequest

from tests import MasuTestCase

class FakeDownloader():
    def download_current_report():
        return [{'file': '/var/tmp/masu/region/aws/catch-clearly.csv', 'compression': 'GZIP'},
                {'file': '/var/tmp/masu/base/aws/professor-hour-industry-television.csv', 'compression': 'GZIP'}]


class OrchestratorTest(MasuTestCase):
    """Test Cases for the Orchestrator object."""

    def setUp(self):
        pass

    def test_initializer(self):
        """Test to init"""
        orchestrator = Orchestrator()

        if len(orchestrator._accounts) != 1:
            self.fail("Unexpected number of test accounts")

        account = orchestrator._accounts.pop()
        self.assertEqual(account.get_access_credential(), 'arn:aws:iam::111111111111:role/CostManagement')
        self.assertEqual(account.get_billing_source(), 'test-bucket')
        self.assertEqual(account.get_customer(), 'Test Customer')
        self.assertEqual(account.get_provider_type(), AMAZON_WEB_SERVICES)


    @patch('masu.external.report_downloader.ReportDownloader._set_downloader', return_value=FakeDownloader)
    def test_prepare_curs(self, mock_downloader):
        """Test downloading cost usage reports."""
        orchestrator = Orchestrator()

        reports = orchestrator.prepare_curs()

        self.assertEqual(len(reports), 2)

    @patch('masu.external.report_downloader.ReportDownloader._set_downloader', return_value=FakeDownloader)
    @patch('masu.external.accounts_accessor.AccountsAccessor.get_accounts', return_value=[])
    def test_prepare_curs_no_accounts(self, mock_downloader, mock_accounts_accessor):
        """Test downloading cost usage reports."""
        orchestrator = Orchestrator()
        reports = orchestrator.prepare_curs()

        self.assertEqual(len(reports), 0)

    @patch('masu.processor.tasks.process.process_report_file', return_value=None)
    def test_process_curs(self, mock_task):
        """Test downloading cost usage reports."""
        requests = []
        request1 = CURProcessRequest().report_path = '/test/path/file.csv'
        requests.append(request1)
        print((request1))
        request2 = CURProcessRequest().report_path = '/test/path/file2.csv'
        requests.append(request2)
        print((request2))

        orchestrator = Orchestrator()
        orchestrator._processing_requests = requests
        orchestrator.process_curs()

    @patch('masu.processor.tasks.process.process_report_file', return_value=None)
    @patch('masu.external.accounts_accessor.AccountsAccessor.get_accounts', return_value=[])
    def test_process_curs_not_accounts(self, mock_task, mock_accounts_accessor):
        """Test downloading cost usage reports with no pending requests."""
        orchestrator = Orchestrator()

        orchestrator.process_curs()

    @patch('masu.external.report_downloader.ReportDownloader._set_downloader', side_effect=ReportDownloaderError)
    def test_prepare_curs_download_exception(self, mock_downloader):
        """Test downloading cost usage reports."""
        orchestrator = Orchestrator()
        reports = orchestrator.prepare_curs()

        self.assertEqual(len(reports), 0)
