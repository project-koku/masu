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
"""Test the report downloader base class."""

import os.path
from unittest.mock import patch

from faker import Faker
from pyfakefs.fake_filesystem_unittest import TestCaseMixin

from masu.processor.report_downloader import ReportDownloader
from tests import MasuTestCase

class ReportDownloaderTest(MasuTestCase, TestCaseMixin):
    """Test Cases for ReportDownloader."""

    fake = Faker()
    patch_path = True

    def setUp(self):
        self.setUpPyfakefs()

    def test_report_downloader_no_path(self):
        downloader = ReportDownloader()
        self.assertIsInstance(downloader, ReportDownloader)
        self.assertIsNotNone(downloader.download_path)
        self.assertTrue(os.path.exists(downloader.download_path))

    def test_report_downloader(self):
        dl_path = '/{}/{}/{}'.format(self.fake.word().lower(),
                                     self.fake.word().lower(),
                                     self.fake.word().lower())
        downloader = ReportDownloader(download_path=dl_path)
        self.assertEqual(downloader.download_path, dl_path)
