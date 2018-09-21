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

"""Test the ReportProcessor object."""

from unittest.mock import patch

from masu.exceptions import MasuProcessingError
from masu.external import (AMAZON_WEB_SERVICES, AWS_LOCAL_SERVICE_PROVIDER)
from masu.processor.report_processor import (ReportProcessor, ReportProcessorError)
from masu.processor.aws.aws_report_processor import AWSReportProcessor

from tests import MasuTestCase
from tests.external.downloader.aws import fake_arn


class ReportProcessorTest(MasuTestCase):
    """Test Cases for the ReportProcessor object."""

    def test_initializer_aws(self):
        """Test to initializer for AWS"""
        processor = ReportProcessor(schema_name='testcustomer',
                                     report_path='/my/report/file',
                                     compression='GZIP',
                                     provider=AMAZON_WEB_SERVICES)
        self.assertIsNotNone(processor._processor)

    def test_initializer_local(self):
        """Test to initializer for Local"""
        processor = ReportProcessor(schema_name='testcustomer',
                                     report_path='/my/report/file',
                                     compression='GZIP',
                                     provider=AWS_LOCAL_SERVICE_PROVIDER)
        self.assertIsNotNone(processor._processor)

    @patch('masu.processor.aws.aws_report_processor.AWSReportProcessor.__init__', side_effect=MasuProcessingError)
    def test_initializer_error(self, fake_processor):
        """Test to initializer with error."""
        with self.assertRaises(ReportProcessorError):
            ReportProcessor(schema_name='testcustomer',
                            report_path='/my/report/file',
                            compression='GZIP',
                            provider=AMAZON_WEB_SERVICES)

    def test_initializer_invalid_provider(self):
        """Test to initializer with invalid provider"""
        with self.assertRaises(ReportProcessorError):
            ReportProcessor(schema_name='testcustomer',
                            report_path='/my/report/file',
                            compression='GZIP',
                            provider='unknown')

    @patch('masu.processor.aws.aws_report_processor.AWSReportProcessor.process', return_value=None)
    def test_aws_process(self, fake_process):
        """Test to process for AWS"""
        processor = ReportProcessor(schema_name='testcustomer',
                                     report_path='/my/report/file',
                                     compression='GZIP',
                                     provider=AMAZON_WEB_SERVICES)
        try:
            processor.process()
        except Exception:
            self.fail('unexpected error')

    @patch('masu.processor.aws.aws_report_processor.AWSReportProcessor.process', side_effect=MasuProcessingError)
    def test_aws_process_error(self, fake_process):
        """Test to process for AWS with processing error"""

        processor = ReportProcessor(schema_name='testcustomer',
                                     report_path='/my/report/file',
                                     compression='GZIP',
                                     provider=AMAZON_WEB_SERVICES)
        with self.assertRaises(ReportProcessorError):
            processor.process()