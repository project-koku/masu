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

import random

import faker
from celery.result import AsyncResult
from unittest.mock import patch

from masu.external import AMAZON_WEB_SERVICES
from masu.exceptions import MasuProviderError
from masu.external.report_downloader import ReportDownloaderError
from masu.processor.orchestrator import Orchestrator
from tests import MasuTestCase

class FakeDownloader():
    fake = faker.Faker()

    def download_current_report(self):
        path = '/var/tmp/masu'
        fake_files = []
        for _ in range(1,random.randint(5,50)):
            fake_files.append({'file': '{}/{}/aws/{}-{}.csv'.format(path,
                                                                    self.fake.word(),
                                                                    self.fake.word(),
                                                                    self.fake.word()),
                               'compression': random.choice(['GZIP', 'PLAIN'])})
        return fake_files


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
    @patch('masu.processor.orchestrator.get_report_files.delay', return_value=True)
    def test_prepare(self, mock_downloader, mock_task):
        """Test downloading cost usage reports."""
        orchestrator = Orchestrator()

        reports = orchestrator.prepare()
        self.assertTrue(reports)

    @patch('masu.external.report_downloader.ReportDownloader._set_downloader', return_value=FakeDownloader)
    @patch('masu.external.accounts_accessor.AccountsAccessor.get_accounts', return_value=[])
    def test_prepare_no_accounts(self, mock_downloader, mock_accounts_accessor):
        """Test downloading cost usage reports."""
        orchestrator = Orchestrator()
        reports = orchestrator.prepare()

        self.assertEqual(reports, [])