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
from masu.processor.tasks.download import _get_report_files

from tests import MasuTestCase


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

    @patch('masu.processor.tasks.download.ReportDownloader._set_downloader',
           return_value=FakeDownloader)
    def test_get_report(self, fake_downloader):
        """Test task"""
        account = ''.join(random.choice(string.digits) for _ in range(12))
        report = _get_report_files(customer_name=self.fake.word(),
                                   access_credential='arn:aws:iam::{}:role/{}'.format(account,
                                                                                      self.fake.word()),
                                   provider_type='AWS',
                                   report_name=self.fake.word(),
                                   report_source=self.fake.word())

        self.assertIsInstance(report, list)
        self.assertGreater(len(report), 0)

    @patch('masu.processor.tasks.download.ReportDownloader._set_downloader',
           side_effect=Exception('only a test'))
    def test_get_report_exception(self, fake_downloader):
        """Test task"""
        account = ''.join(random.choice(string.digits) for _ in range(12))

        report = _get_report_files(customer_name=self.fake.word(),
                                   access_credential='arn:aws:iam::{}:role/{}'.format(account,
                                                                                       self.fake.word()),
                                   provider_type='AWS',
                                   report_name=self.fake.word(),
                                   report_source=self.fake.word())

        self.assertEqual(report, [])
