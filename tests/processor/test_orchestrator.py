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

from masu.processor.orchestrator import Orchestrator

from tests import MasuTestCase

class FakeDownloader():
    def download_current_report():
        return ['/var/tmp/masu/region/aws/catch-clearly.csv',
                '/var/tmp/masu/base/aws/professor-hour-industry-television.csv']


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
        self.assertEqual(account.get_provider(), 'Test Provider')


    @patch('masu.external.report_downloader.ReportDownloader._set_downloader', return_value=FakeDownloader)
    def test_download_curs(self, mock_downloader):
        """Test downloading cost usage reports."""
        orchestrator = Orchestrator()

        reports = orchestrator.download_curs()

        self.assertEqual(len(reports), 2)

    @patch('masu.external.report_downloader.ReportDownloader._set_downloader', return_value=FakeDownloader)
    @patch('masu.external.accounts_accessor.AccountsAccessor.get_accounts', return_value=[])
    def test_download_curs_no_accounts(self, mock_downloader, mock_accounts_accessor):
        """Test downloading cost usage reports."""
        orchestrator = Orchestrator()
        reports = orchestrator.download_curs()

        self.assertEqual(len(reports), 0)
