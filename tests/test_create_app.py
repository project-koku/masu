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

"""Test the app factory for Masu."""

import errno
import logging

from unittest import TestCase
from unittest.mock import patch, PropertyMock

from flask import Flask
from masu import create_app


@patch('masu.api.status.celery_app', autospec=True)
class CreateAppTest(TestCase):
    """Test Cases for create_app app factory."""

    @patch('masu.api.status.ApplicationStatus.celery_status',
           new_callable=PropertyMock)
    def test_create_app(self, mock_status, mock_celery):
        """Assert testing is false without passing test config."""
        self.assertFalse(create_app().testing)

    def test_create_test_app(self, mock_celery):
        """Assert that testing is true with test config."""
        self.assertTrue(
            create_app(
                {
                    'TESTING': True,
                    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
                    'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
                }
            ).testing
        )

    @patch('masu.os.makedirs')
    def test_create_app_dirs_exist(self, mock_mkdir, mock_celery):
        """Test handling of os exception."""
        err = OSError('test error', errno.EEXIST)
        mock_mkdir.side_effect = err

        app = create_app(test_config=dict())
        self.assertIsInstance(app, Flask)

    @patch('masu.os.makedirs')
    def test_create_app_oserror(self, mock_mkdir, mock_celery):
        """Test handling of os exception."""
        logging.disable(logging.NOTSET)

        err = OSError('test error')
        mock_mkdir.side_effect = err

        expected = 'WARNING:masu:test error'
        with self.assertLogs('masu', level='WARNING') as logger:
            app = create_app(test_config=dict())
            self.assertIn(expected, logger.output)
