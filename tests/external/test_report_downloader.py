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

"""Test the ReportDownloader object."""

from unittest.mock import patch

from masu.external import AMAZON_WEB_SERVICES
from masu.external.downloader.aws.aws_report_downloader import AWSReportDownloader
from masu.external.report_downloader import ReportDownloader, ReportDownloaderError
from tests import MasuTestCase

class FakeDownloader():
    pass


class ReportDownloaderTest(MasuTestCase):
    """Test Cases for the ReportDownloader object."""

    def setUp(self):
        pass

    @patch('masu.external.downloader.aws.aws_report_downloader.AWSReportDownloader.__init__', return_value=None)
    def test_initializer(self, fake_downloader):
        """Test to initializer"""
        downloader = ReportDownloader(customer_name='customer name',
                                      access_credential='mycred',
                                      report_source='hereiam',
                                      report_name='bestreport',
                                      provider_type=AMAZON_WEB_SERVICES)
        self.assertIsNotNone(downloader._downloader)

    def test_invalid_provider_type(self):
        """Test that error is thrown with invalid account source."""

        with self.assertRaises(ReportDownloaderError):
            _ = ReportDownloader(customer_name='customer name',
                                 access_credential='mycred',
                                 report_source='hereiam',
                                 report_name='bestreport',
                                 provider_type='unknown')
