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
from masu.external.downloader.aws.aws_report_downloader import AWSReportDownloader, AWSReportDownloaderError
from masu.external.report_downloader import ReportDownloader, ReportDownloaderError
from tests import MasuTestCase

class FakeDownloader():
    pass


class ReportDownloaderTest(MasuTestCase):
    """Test Cases for the ReportDownloader object."""

    file_list = ['/var/tmp/masu/region/aws/catch-clearly.csv',
                 '/var/tmp/masu/base/aws/professor-hour-industry-television.csv']

    @patch('masu.external.downloader.aws.aws_report_downloader.AWSReportDownloader.__init__', return_value=None)
    def test_initializer(self, fake_downloader):
        """Test to initializer"""
        downloader = ReportDownloader(customer_name='customer name',
                                      access_credential='mycred',
                                      report_source='hereiam',
                                      report_name='bestreport',
                                      provider_type=AMAZON_WEB_SERVICES)
        self.assertIsNotNone(downloader._downloader)

    @patch('masu.external.report_downloader.ReportDownloader._set_downloader', side_effect=AWSReportDownloaderError)
    def test_initializer_downloader_exception(self, fake_downloader):
        """Test to initializer where _set_downloader throws exception"""
        with self.assertRaises(ReportDownloaderError):
            ReportDownloader(customer_name='customer name',
                                 access_credential='mycred',
                                 report_source='hereiam',
                                 report_name='bestreport',
                                 provider_type=AMAZON_WEB_SERVICES)

    def test_invalid_provider_type(self):
        """Test that error is thrown with invalid account source."""

        with self.assertRaises(ReportDownloaderError):
            ReportDownloader(customer_name='customer name',
                                 access_credential='mycred',
                                 report_source='hereiam',
                                 report_name='bestreport',
                                 provider_type='unknown')

    @patch('masu.external.downloader.aws.aws_report_downloader.AWSReportDownloader.__init__', return_value=None)
    def test_get_current_report(self, fake_downloader):
        """Test get_current_report function."""
        downloader = ReportDownloader(customer_name='customer name',
                                      access_credential='mycred',
                                      report_source='hereiam',
                                      report_name='bestreport',
                                      provider_type=AMAZON_WEB_SERVICES)
        with patch.object(AWSReportDownloader, 'download_current_report', return_value=self.file_list):
            files = downloader.get_current_report()
            self.assertEqual(len(files), len(self.file_list))

    @patch('masu.external.downloader.aws.aws_report_downloader.AWSReportDownloader.__init__', return_value=None)
    def test_get_current_report_error(self, fake_downloader):
        """Test get_current_report function with error."""
        downloader = ReportDownloader(customer_name='customer name',
                                      access_credential='mycred',
                                      report_source='hereiam',
                                      report_name='bestreport',
                                      provider_type=AMAZON_WEB_SERVICES)
        with patch.object(AWSReportDownloader, 'download_current_report', side_effect=Exception('some error')):
            with self.assertRaises(ReportDownloaderError):
                downloader.get_current_report()
