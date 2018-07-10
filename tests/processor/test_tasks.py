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

import faker
from unittest.mock import patch, Mock

from masu.external.report_downloader import ReportDownloaderError
from masu.processor._tasks.download import _get_report_files
from masu.processor._tasks.process import _process_report_file

from tests import MasuTestCase
from tests.external.downloader.aws import fake_arn


class FakeDownloader(Mock):
    def download_current_report():
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
                                   access_credential=account,
                                   provider_type='AWS',
                                   report_name=self.fake.word(),
                                   report_source=self.fake.word())

        self.assertIsInstance(report, list)
        self.assertGreater(len(report), 0)

    @patch('masu.processor._tasks.download.ReportDownloader._set_downloader',
           side_effect=Exception('only a test'))
    def test_get_report_exception(self, fake_downloader):
        """Test task"""
        account = fake_arn(service='iam', generate_account_id=True)

        report = _get_report_files(customer_name=self.fake.word(),
                                   access_credential=account,
                                   provider_type='AWS',
                                   report_name=self.fake.word(),
                                   report_source=self.fake.word())

        self.assertEqual(report, [])

    @patch('masu.processor._tasks.download._get_report_files',
           return_value=['file1', 'file2'])
    @patch('masu.processor.tasks.process_report_file')
    def test_second_task_called(self, mock_process_files, mock_get_files):
        mock_process_files.delay = Mock()

        account = fake_arn(service='iam', generate_account_id=True)

        reports = _get_report_files(customer_name=self.fake.word(),
                                    access_credential=account,
                                    provider_type='AWS',
                                    report_name=self.fake.word(),
                                    report_source=self.fake.word())

        schema_name = self.fake.word()
        for report_dict in reports:
            request = {'schema_name': schema_name,
                       'report_path': report_dict.get('file'),
                       'compression': report_dict.get('compression')}
            process_report_file.delay(**request)

            mock_process_files.assert_called_with(
                schema_name,
                report_dict.get('file'),
                report_dict.get('compression')
            )

    @patch('masu.processor._tasks.download._get_report_files',
           return_value=[])
    @patch('masu.processor.tasks.process_report_file')
    def test_second_task_not_called(self, mock_process_files, mock_get_files):
        mock_process_files.delay = Mock()

        account = fake_arn(service='iam', generate_account_id=True)

        reports = _get_report_files(customer_name=self.fake.word(),
                                   access_credential=account,
                                   provider_type='AWS',
                                   report_name=self.fake.word(),
                                   report_source=self.fake.word())
        for report_dict in reports:
            request = {'schema_name': schema_name,
                       'report_path': report_dict.get('file'),
                       'compression': report_dict.get('compression')}
            process_report_file.delay(**request)

        mock_process_files.assert_not_called()

class ProcessReportFileTests(MasuTestCase):
    """Test Cases for the Orchestrator object."""

    @patch('masu.processor.report_processor.ReportProcessor')
    @patch('masu.processor.report_processor.ReportProcessor.process', return_value=2)
    def test_process_file(self, fake_processor, fake_process):
        """Test task"""
        request = {'report_path': '/test/path/file1.csv',
                   'compression': 'gzip',
                   'schema_name': 'testcustomer'}
        _process_report_file(**request)
