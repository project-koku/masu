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

"""Test the status endpoint view."""

from collections import namedtuple
from unittest.mock import ANY, Mock, patch, PropertyMock

from masu.api import API_VERSION
from masu.api.status import ApplicationStatus
from tests import MasuTestCase


class StatusAPITest(MasuTestCase):
    """Test Cases for the Status API."""

    def test_status(self):
        """Test the status endpoint."""
        response = self.client.get('/api/v1/status/')
        body = response.json

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')

        self.assertIn('commit', body)
        self.assertIn('python_version', body)
        self.assertIn('platform_info', body)
        self.assertIn('modules', body)
        self.assertIn('api_version', body)
        self.assertIsNotNone(body['commit'])
        self.assertIsNotNone(body['python_version'])
        self.assertIsNotNone(body['platform_info'])
        self.assertIsNotNone(body['modules'])
        self.assertEqual(body['api_version'], API_VERSION)

    @patch('masu.api.status.os.environ')
    def test_commit_with_env(self, mock_os):
        """Test the commit method via environment."""
        expected = 'buildnum'
        mock_os.get.return_value = expected
        result = ApplicationStatus().commit
        self.assertEqual(result, expected)

    @patch('masu.api.status.subprocess.run')
    @patch('masu.api.status.os.environ')
    def test_commit_with_subprocess(self, mock_os, mock_subprocess):
        """Test the commit method via subprocess."""
        expected = 'buildnum'
        run = Mock()
        run.stdout = b'buildnum'
        mock_subprocess.return_value = run
        mock_os.get.return_value = None
        result = ApplicationStatus().commit
        self.assertEqual(result, expected)

    @patch('masu.api.status.platform.uname')
    def test_platform_info(self, mock_platform):
        """Test the platform_info method."""
        platform_record = namedtuple('Platform', ['os', 'version'])
        a_plat = platform_record('Red Hat', '7.4')
        mock_platform.return_value = a_plat
        result = ApplicationStatus().platform_info
        self.assertEqual(result['os'], 'Red Hat')
        self.assertEqual(result['version'], '7.4')

    @patch('masu.api.status.sys.version')
    def test_python_version(self, mock_sys_ver):
        """Test the python_version method."""
        expected = 'Python 3.6'
        mock_sys_ver.replace.return_value = expected
        result = ApplicationStatus().python_version
        self.assertEqual(result, expected)

    @patch('masu.api.status.sys.modules')
    def test_modules(self, mock_modules):
        """Test the modules method."""
        expected = {'module1': 'version1',
                    'module2': 'version2'}
        mod1 = Mock(__version__='version1')
        mod2 = Mock(__version__='version2')
        mock_modules.items.return_value = (('module1', mod1),
                                           ('module2', mod2))
        result = ApplicationStatus().modules
        self.assertEqual(result, expected)

    @patch('masu.api.status.logger.info')
    def test_startup_with_modules(self, mock_logger):
        """Test the startup method with a module list."""
        ApplicationStatus().startup()
        mock_logger.assert_called_with(ANY, ANY)

    @patch('masu.api.status.ApplicationStatus.modules', new_callable=PropertyMock)
    def test_startup_without_modules(self, mock_mods):
        """Test the startup method without a module list."""
        mock_mods.return_value = {}
        expected = 'INFO:masu.api.status:Modules: None'

        with self.assertLogs('masu.api.status', level='INFO') as logger:
            ApplicationStatus().startup()
            self.assertIn(expected, logger.output)
