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
import logging

import faker
from celery.result import AsyncResult
from unittest.mock import patch


from masu.external import AMAZON_WEB_SERVICES
from masu.external.accounts_accessor import (AccountsAccessor, AccountsAccessorError)
from masu.external.report_downloader import ReportDownloaderError
from masu.processor.expired_data_remover import ExpiredDataRemover
from masu.processor.orchestrator import Orchestrator
from tests import MasuTestCase
from tests.external.downloader.aws import fake_arn

class FakeDownloader():
    fake = faker.Faker()
    def download_reports(self, number_of_months=1):
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
    fake = faker.Faker()

    def setUp(self):
        self.mock_accounts = []
        for _ in range(1, random.randint(5,20)):
            self.mock_accounts.append({
                'authentication': fake_arn(service='iam', generate_account_id=True),
                'billing_source': self.fake.word(),
                'customer_name': self.fake.word(),
                'provider_type': 'AWS',
                'schema_name': self.fake.word()})

    def test_initializer(self):
        """Test to init"""
        orchestrator = Orchestrator()

        if len(orchestrator._accounts) != 1:
            self.fail("Unexpected number of test accounts")

        account = orchestrator._accounts.pop()
        self.assertEqual(account.get('authentication'), 'arn:aws:iam::111111111111:role/CostManagement')
        self.assertEqual(account.get('billing_source'), 'test-bucket')
        self.assertEqual(account.get('customer_name'), 'Test Customer')
        self.assertEqual(account.get('provider_type'), AMAZON_WEB_SERVICES)

    @patch('masu.external.account_label.AccountLabel._set_labler', return_value=None)
    @patch('masu.external.report_downloader.ReportDownloader._set_downloader', return_value=FakeDownloader)
    @patch('masu.processor.orchestrator.get_report_files.delay', return_value=True)
    def test_prepare(self, mock_task, mock_downloader, mock_labeler):
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

        self.assertIsNone(reports)

    @patch.object(AccountsAccessor, 'get_accounts')
    @patch('masu.processor.tasks.process_report_file', return_value=None)
    def test_init_all_accounts(self, mock_task, mock_accessor):
        """Test initializing orchestrator with forced billing source."""
        mock_accessor.return_value = self.mock_accounts
        orchestrator_all = Orchestrator()
        self.assertEqual(orchestrator_all._accounts, self.mock_accounts)

    @patch.object(AccountsAccessor, 'get_accounts')
    @patch('masu.processor.tasks.process_report_file', return_value=None)
    def test_init_with_billing_source(self, mock_task, mock_accessor):
        """Test initializing orchestrator with forced billing source."""
        mock_accessor.return_value = self.mock_accounts

        fake_source = random.choice(self.mock_accounts)

        individual = Orchestrator(fake_source.get('billing_source'))
        self.assertEqual(len(individual._accounts), 1)
        found_account = individual._accounts[0]
        self.assertEqual(found_account.get('billing_source'),
                         fake_source.get('billing_source'))

    @patch.object(AccountsAccessor, 'get_accounts')
    @patch('masu.processor.tasks.process_report_file', return_value=None)
    def test_init_all_accounts_error(self, mock_task, mock_accessor):
        """Test initializing orchestrator accounts error."""
        mock_accessor.side_effect = AccountsAccessorError('Sample timeout error')
        try:
            Orchestrator()
        except Exception:
            self.fail('unexpected error')

    @patch.object(ExpiredDataRemover, 'remove')
    @patch('masu.processor.orchestrator.remove_expired_data.delay', return_value=True)
    def test_remove_expired_report_data(self, mock_task, mock_remover):
        """Test removing expired report data."""
        expected_results = [{'account_payer_id': '999999999',
                             'billing_period_start': '2018-06-24 15:47:33.052509'}]
        mock_remover.return_value = expected_results

        expected = 'INFO:masu.processor.orchestrator:Expired data removal queued - customer: Test Customer, Task ID: {}'
        logging.disable(logging.NOTSET) # We are currently disabling all logging below CRITICAL in masu/__init__.py
        with self.assertLogs('masu.processor.orchestrator', level='INFO') as logger:
            orchestrator = Orchestrator()
            results = orchestrator.remove_expired_report_data()
            self.assertTrue(results)
            self.assertEqual(len(results), 1)
            async_id = results.pop().get('async_id')
            self.assertIn(expected.format(async_id), logger.output)

    @patch.object(AccountsAccessor, 'get_accounts')
    @patch.object(ExpiredDataRemover, 'remove')
    @patch('masu.processor.orchestrator.remove_expired_data.delay', return_value=True)
    def test_remove_expired_report_data_no_accounts(self, mock_task, mock_remover, mock_accessor):
        """Test removing expired report data with no accounts."""
        expected_results = [{'account_payer_id': '999999999',
                             'billing_period_start': '2018-06-24 15:47:33.052509'}]
        mock_remover.return_value = expected_results
        mock_accessor.return_value = []

        orchestrator = Orchestrator()
        results = orchestrator.remove_expired_report_data()

        self.assertEqual(results, [])
