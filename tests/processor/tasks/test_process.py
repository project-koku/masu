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

"""Test the process task."""

from unittest.mock import patch

from masu.processor.cur_process_request import CURProcessRequest
from masu.processor.tasks.process import process_report_file

from tests import MasuTestCase


class ProcessReportFileTests(MasuTestCase):
    """Test Cases for the Orchestrator object."""

    def setUp(self):
        pass

    @patch('masu.processor.report_processor.ReportProcessor')
    @patch('masu.processor.report_processor.ReportProcessor.process', return_value=2)
    def test_process_file(self, fake_processor, fake_process):
        """Test task"""
        request = CURProcessRequest()
        request.report_path = '/test/path/file1.csv'
        request.compression = 'gzip'
        request.schema_name = 'testcustomer'

        process_report_file(request)
