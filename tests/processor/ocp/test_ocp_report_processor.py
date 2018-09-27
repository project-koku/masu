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

"""Test the OCPReportProcessor."""
import gzip

from sqlalchemy.sql.expression import delete

from masu.exceptions import MasuProcessingError
from masu.external import GZIP_COMPRESSED, UNCOMPRESSED
from masu.processor.ocp.ocp_report_processor import OCPReportProcessor
from tests import MasuTestCase



class OCPReportProcessorTest(MasuTestCase):
    """Test Cases for the OCPReportProcessor object."""

    @classmethod
    def setUpClass(cls):
        """Set up the test class with required objects."""
        # These test reports should be replaced with OCP reports once processor is impelmented.
        cls.test_report = './tests/data/test_cur.csv'
        cls.test_report_gzip = './tests/data/test_cur.csv.gz'

        cls.processor = OCPReportProcessor(
            schema_name='acct10001org20002',
            report_path=cls.test_report,
            compression=UNCOMPRESSED,
        )

    def test_initializer(self):
        """Test initializer."""
        self.assertIsNotNone(self.processor._schema_name)
        self.assertIsNotNone(self.processor._report_path)
        self.assertIsNotNone(self.processor._compression)

    def test_initializer_unsupported_compression(self):
        """Assert that an error is raised for an invalid compression."""
        with self.assertRaises(MasuProcessingError):
            OCPReportProcessor(schema_name='acct10001org20002',
                               report_path=self.test_report,
                               compression='unsupported')

    def test_process_default(self):
        """Test the processing of an uncompressed file."""
        processor = OCPReportProcessor(
            schema_name='acct10001org20002',
            report_path=self.test_report,
            compression=UNCOMPRESSED,
        )
        processor.process()
        # TODO verify database state once implemented

    def test_process_gzip(self):
        """Test the processing of an uncompressed file."""
        processor = OCPReportProcessor(
            schema_name='acct10001org20002',
            report_path=self.test_report_gzip,
            compression=GZIP_COMPRESSED,
        )
        processor.process()
        # TODO verify database state once implemented
