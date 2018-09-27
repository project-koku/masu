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

"""Test the download task."""

import random
import string
import shutil
import tempfile
import logging
import os
from datetime import date, datetime, timedelta
from unittest.mock import call, patch, Mock

import faker

from masu.config import Config
from masu.database import AWS_CUR_TABLE_MAP
from masu.database.report_db_accessor import ReportDBAccessor
from masu.database.reporting_common_db_accessor import ReportingCommonDBAccessor
from masu.database.report_stats_db_accessor import ReportStatsDBAccessor
from masu.external.report_downloader import ReportDownloader, ReportDownloaderError
from masu.processor.expired_data_remover import ExpiredDataRemover
from masu.processor._tasks.download import _get_report_files
from masu.processor._tasks.process import _process_report_file
from masu.processor.tasks import (get_report_files,
                                  process_report_file,
                                  remove_expired_data)

from tests import MasuTestCase
from tests.external.downloader.aws import fake_arn

class FakeDownloader(Mock):
    def download_report(date_time):
        fake = faker.Faker()
        path = '/var/tmp/masu'
        fake_files = []
        for _ in range(1,random.randint(5,50)):
            fake_files.append({'file': '{}/{}/aws/{}-{}.csv'.format(path,
                                                                    fake.word(),
                                                                    fake.word(),
                                                                    fake.word()),
                               'compression': random.choice(['GZIP', 'PLAIN'])})
        return fake_files


class GetReportFileTests(MasuTestCase):
    """Test Cases for the celery task."""

    fake = faker.Faker()

    @patch('masu.processor._tasks.download.ReportDownloader._set_downloader',
           return_value=FakeDownloader)
    def test_get_report(self, fake_downloader):
        """Test task"""
        account = fake_arn(service='iam', generate_account_id=True)
        report = _get_report_files(customer_name=self.fake.word(),
                                   authentication=account,
                                   provider_type='AWS',
                                   report_name=self.fake.word(),
                                   provider_uuid='6e212746-484a-40cd-bba0-09a19d132d64',
                                   billing_source=self.fake.word())

        self.assertIsInstance(report, list)
        self.assertGreater(len(report), 0)

    @patch('masu.processor._tasks.download.ReportDownloader._set_downloader',
           return_value=FakeDownloader)
    def test_disk_status_logging(self, fake_downloader):
        """Test task for logging when temp directory exists."""
        logging.disable(logging.NOTSET)

        os.makedirs(Config.TMP_DIR, exist_ok=True)

        account = fake_arn(service='iam', generate_account_id=True)
        expected = 'INFO:masu.processor._tasks.download:Avaiable disk space'
        with self.assertLogs('masu.processor._tasks.download', level='INFO') as logger:
            _get_report_files(customer_name=self.fake.word(),
                              authentication=account,
                              provider_type='AWS',
                              report_name=self.fake.word(),
                              provider_uuid='6e212746-484a-40cd-bba0-09a19d132d64',
                              billing_source=self.fake.word())
            statement_found = False
            for log in logger.output:
                if expected in log:
                    statement_found = True
            self.assertTrue(statement_found)

        shutil.rmtree(Config.TMP_DIR, ignore_errors=True)

    @patch('masu.processor._tasks.download.ReportDownloader._set_downloader',
           return_value=FakeDownloader)
    def test_disk_status_logging_no_dir(self, fake_downloader):
        """Test task for logging when temp directory does not exist."""
        logging.disable(logging.NOTSET)

        shutil.rmtree(Config.TMP_DIR, ignore_errors=True)

        account = fake_arn(service='iam', generate_account_id=True)
        expected = 'INFO:masu.processor._tasks.download:Unable to find avaiable disk space. {} does not exist'.format(Config.TMP_DIR)
        with self.assertLogs('masu.processor._tasks.download', level='INFO') as logger:
            _get_report_files(customer_name=self.fake.word(),
                              authentication=account,
                              provider_type='AWS',
                              report_name=self.fake.word(),
                              provider_uuid='6e212746-484a-40cd-bba0-09a19d132d64',
                              billing_source=self.fake.word())
            self.assertIn(expected, logger.output)

    @patch('masu.processor._tasks.download.ReportDownloader._set_downloader',
           side_effect=Exception('only a test'))
    def test_get_report_exception(self, fake_downloader):
        """Test task"""
        account = fake_arn(service='iam', generate_account_id=True)

        with self.assertRaises(Exception):
            _get_report_files(customer_name=self.fake.word(),
                              authentication=account,
                              provider_type='AWS',
                              report_name=self.fake.word(),
                              provider_uuid='6e212746-484a-40cd-bba0-09a19d132d64',
                              billing_source=self.fake.word())

    @patch('masu.processor._tasks.download.ReportDownloader._set_downloader',
           return_value=FakeDownloader)
    @patch('masu.database.provider_db_accessor.ProviderDBAccessor.get_setup_complete',
           return_value=True)
    def test_get_report_with_override(self, fake_accessor, fake_downloader):
        """Test _get_report_files on non-initial load with override set."""
        Config.INGEST_OVERRIDE = True
        Config.INITIAL_INGEST_NUM_MONTHS = 5
        initial_month_qty = Config.INITIAL_INGEST_NUM_MONTHS

        account = fake_arn(service='iam', generate_account_id=True)
        with patch.object(ReportDownloader, 'get_reports') as download_call:
            _get_report_files(customer_name=self.fake.word(),
                            authentication=account,
                            provider_type='AWS',
                            report_name=self.fake.word(),
                            provider_uuid='6e212746-484a-40cd-bba0-09a19d132d64',
                            billing_source=self.fake.word())

            download_call.assert_called_with(initial_month_qty)

        Config.INGEST_OVERRIDE = False
        Config.INITIAL_INGEST_NUM_MONTHS = 2

class ProcessReportFileTests(MasuTestCase):
    """Test Cases for the Orchestrator object."""

    @patch('masu.processor._tasks.process.ReportProcessor')
    @patch('masu.processor._tasks.process.ReportStatsDBAccessor')
    def test_process_file(self, mock_accessor, mock_processor):
        """Test the process_report_file functionality."""
        report_dir = tempfile.mkdtemp()
        path = '{}/{}'.format(report_dir, 'file1.csv')
        request = {'report_path': path,
                   'compression': 'gzip',
                   'schema_name': 'acct10001org20002',
                   'provider': 'AWS',
                   'provider_uuid': '6e212746-484a-40cd-bba0-09a19d132d64',
                   'start_date': str(datetime.today())}

        mock_proc = mock_processor()
        mock_acc = mock_accessor()

        _process_report_file(**request)

        mock_proc.process.assert_called()
        mock_acc.log_last_started_datetime.assert_called()
        mock_acc.log_last_completed_datetime.assert_called()
        mock_acc.commit.assert_called()
        shutil.rmtree(report_dir)



class TestProcessorTasks(MasuTestCase):
    """Test cases for Processor Celery tasks."""

    @classmethod
    def setUpClass(cls):
        """Set up the class."""
        super().setUpClass()
        cls.fake = faker.Faker()
        cls.fake_reports = [
            {
                'file': cls.fake.word(),
                'compression': 'GZIP'
            },
            {
                'file': cls.fake.word(),
                'compression': 'PLAIN'
            }
        ]

        cls.fake_account = fake_arn(service='iam', generate_account_id=True)
        cls.today = datetime.today()
        cls.yesterday = datetime.today() - timedelta(days=1)


    def setUp(self):
        super().setUp()

        self.fake_get_report_args = {'customer_name': self.fake.word(),
                                     'authentication': self.fake_account,
                                     'provider_type': 'AWS',
                                     'schema_name': self.fake.word(),
                                     'billing_source': self.fake.word(),
                                     'provider_uuid': '6e212746-484a-40cd-bba0-09a19d132d64'}

    @patch('masu.processor.tasks._get_report_files')
    @patch('masu.processor.tasks.process_report_file')
    def test_get_report_files_second_task_called(self,
                                                 mock_process_files,
                                                 mock_get_files):
        """Test that the chained task is called."""
        mock_process_files.delay = Mock()
        mock_get_files.return_value = self.fake_reports

        get_report_files(**self.fake_get_report_args)

        expected_calls = [
            call(self.fake_get_report_args.get('schema_name'),
                 report['file'],
                 report['compression'])
            for report in self.fake_reports
        ]

        mock_process_files.delay.has_calls(expected_calls, any_order=True)

    @patch('masu.processor.tasks._get_report_files',
           return_value=[])
    @patch('masu.processor.tasks.process_report_file')
    def test_get_report_files_second_task_not_called(self,
                                                     mock_process_files,
                                                     mock_get_files):
        """Test that the chained task is not called."""
        mock_process_files.delay = Mock()
        get_report_files(**self.fake_get_report_args)
        mock_process_files.delay.assert_not_called()

    @patch('masu.processor.tasks.ReportStatsDBAccessor.get_last_completed_datetime')
    @patch('masu.processor.tasks.ReportStatsDBAccessor.get_last_started_datetime')
    @patch('masu.processor.tasks._get_report_files')
    @patch('masu.processor.tasks.process_report_file')
    def test_get_report_files_timestamps_aligned(self,
                                                 mock_process_files,
                                                 mock_get_files,
                                                 mock_started,
                                                 mock_completed):
        """
        Test that the chained task is not called when start timestamp is before
        end timestamp since both started and completed times are present.
        """
        mock_process_files.delay = Mock()
        mock_get_files.return_value = self.fake_reports

        mock_started.return_value = self.yesterday
        mock_completed.return_value = self.today

        get_report_files(**self.fake_get_report_args)
        mock_process_files.delay.assert_not_called()

    @patch('masu.processor.tasks.ReportStatsDBAccessor.get_last_completed_datetime')
    @patch('masu.processor.tasks.ReportStatsDBAccessor.get_last_started_datetime')
    @patch('masu.processor.tasks._get_report_files')
    @patch('masu.processor.tasks.process_report_file')
    def test_get_report_files_timestamps_misaligned(self,
                                                    mock_process_files,
                                                    mock_get_files,
                                                    mock_started,
                                                    mock_completed):
        """
        Test that the chained task is called when start timestamp is before
        end timestamp.
        """
        mock_process_files.delay = Mock()
        mock_get_files.return_value = self.fake_reports

        mock_started.return_value = self.today
        mock_completed.return_value = self.yesterday

        get_report_files(**self.fake_get_report_args)
        mock_process_files.delay.assert_not_called()

    @patch('masu.processor.tasks.ReportStatsDBAccessor.get_last_completed_datetime')
    @patch('masu.processor.tasks.ReportStatsDBAccessor.get_last_started_datetime')
    @patch('masu.processor.tasks._get_report_files')
    @patch('masu.processor.tasks.process_report_file')
    def test_get_report_files_timestamps_empty_start(self,
                                               mock_process_files,
                                               mock_get_files,
                                               mock_started,
                                               mock_completed):
        """
        Test that the chained task is called when no start time is set.
        """
        mock_process_files.delay = Mock()
        mock_get_files.return_value = self.fake_reports

        mock_started.return_value = None
        mock_completed.return_value = self.today
        get_report_files(**self.fake_get_report_args)
        mock_process_files.delay.assert_called()

    @patch('masu.processor.tasks.ReportStatsDBAccessor.get_last_completed_datetime')
    @patch('masu.processor.tasks.ReportStatsDBAccessor.get_last_started_datetime')
    @patch('masu.processor.tasks._get_report_files')
    @patch('masu.processor.tasks.process_report_file')
    def test_get_report_files_timestamps_empty_end(self,
                                               mock_process_files,
                                               mock_get_files,
                                               mock_started,
                                               mock_completed):
        """
        Test that the chained task is not called when no end time is set since
        processing is in progress.
        """
        mock_process_files.delay = Mock()
        mock_get_files.return_value = self.fake_reports

        mock_started.return_value = self.today
        mock_completed.return_value = None
        get_report_files(**self.fake_get_report_args)
        mock_process_files.delay.assert_not_called()

    @patch('masu.processor.tasks.ReportStatsDBAccessor.get_last_completed_datetime')
    @patch('masu.processor.tasks.ReportStatsDBAccessor.get_last_started_datetime')
    @patch('masu.processor.tasks._get_report_files')
    @patch('masu.processor.tasks.process_report_file')
    @patch('masu.external.date_accessor.DateAccessor.today')
    def test_get_report_files_timestamps_empty_end_timeout(self,
                                               mock_date,
                                               mock_process_files,
                                               mock_get_files,
                                               mock_started,
                                               mock_completed):
        """
        Test that the chained task is called when no end time is set since
        processing has exceeded the timeout.
        """
        mock_process_files.delay = Mock()
        mock_get_files.return_value = self.fake_reports

        mock_started.return_value = self.today
        mock_completed.return_value = None

        mock_date.return_value = self.today + timedelta(hours=3)

        get_report_files(**self.fake_get_report_args)
        mock_process_files.delay.assert_called()

    @patch('masu.processor.tasks.ReportStatsDBAccessor.get_last_completed_datetime')
    @patch('masu.processor.tasks.ReportStatsDBAccessor.get_last_started_datetime')
    @patch('masu.processor.tasks._get_report_files')
    @patch('masu.processor.tasks.process_report_file')
    @patch('masu.external.date_accessor.DateAccessor.today')
    def test_get_report_files_timestamps_empty_end_no_timeout(self,
                                               mock_date,
                                               mock_process_files,
                                               mock_get_files,
                                               mock_started,
                                               mock_completed):
        """
        Test that the chained task is not called when no end time is set since
        processing is in progress but completion timeout has not been reached.
        """
        mock_process_files.delay = Mock()
        mock_get_files.return_value = self.fake_reports

        mock_started.return_value = self.today
        mock_completed.return_value = None

        mock_date.return_value = self.today + timedelta(hours=1)

        get_report_files(**self.fake_get_report_args)
        mock_process_files.delay.assert_not_called()

    @patch('masu.processor.tasks.ReportStatsDBAccessor.get_last_completed_datetime')
    @patch('masu.processor.tasks.ReportStatsDBAccessor.get_last_started_datetime')
    @patch('masu.processor.tasks._get_report_files')
    @patch('masu.processor.tasks.process_report_file')
    def test_get_report_files_timestamps_empty_both(self,
                                               mock_process_files,
                                               mock_get_files,
                                               mock_started,
                                               mock_completed):
        """
        Test that the chained task is called when no timestamps are set.
        """
        mock_process_files.delay = Mock()
        mock_get_files.return_value = self.fake_reports

        mock_started.return_value = None
        mock_completed.return_value = None
        get_report_files(**self.fake_get_report_args)
        mock_process_files.delay.assert_called()

    @patch('masu.processor.aws.aws_report_processor.AWSReportProcessor.update_summary_tables')
    @patch('masu.processor.tasks._process_report_file')
    def test_process_report_file(self, mock_process_files, mock_update_task):
        """Test process report file functionality."""
        schema_name = self.fake.word()
        report_path = 'path/to/file'
        compression = 'GZIP'
        provider = 'AWS'
        start_date = datetime.utcnow()
        provider_uuid = '6e212746-484a-40cd-bba0-09a19d132d64'
        process_report_file(schema_name, report_path, compression, provider, start_date, provider_uuid)

        mock_process_files.assert_called_with(
            schema_name,
            report_path,
            compression,
            provider,
            provider_uuid,
            start_date
        )

class TestRemoveExpiredDataTasks(MasuTestCase):
    """Test cases for Processor Celery tasks."""

    @patch.object(ExpiredDataRemover, 'remove')
    def test_remove_expired_data(self, fake_remover):
        """Test task"""
        expected_results = [{'account_payer_id': '999999999',
                             'billing_period_start': '2018-06-24 15:47:33.052509'}]
        fake_remover.return_value = expected_results

        expected = 'INFO:masu.processor._tasks.remove_expired:Expired Data: {}'

        logging.disable(logging.NOTSET) # We are currently disabling all logging below CRITICAL in masu/__init__.py
        with self.assertLogs('masu.processor._tasks.remove_expired') as logger:
            remove_expired_data(schema_name='acct10001org20002', provider='AWS', simulate=True)
            self.assertIn(expected.format(str(expected_results)), logger.output)
