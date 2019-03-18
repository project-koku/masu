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

"""Common Test Case class for Masu tests."""

from unittest import TestCase

from masu import create_app


class MasuTestCase(TestCase):
    """Subclass of TestCase that automatically create an app and client."""

    def setUp(self):
        """Create test case setup."""
        self.app = create_app(
            {
                'TESTING': True,
                'SQLALCHEMY_TRACK_MODIFICATIONS': False,
                'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db',
                'REMOVE_EXPIRED_REPORT_DATA_ON_DAY': '1',
                'REMOVE_EXPIRED_REPORT_UTC_TIME': '00:00',
                'LOG_LEVEL': 'INFO'
                #'CELERY_RESULT_BACKEND': 'db+sqlite:///test.db'
            }
        )
        self.client = self.app.test_client()
        self.test_schema = 'acct10001'
        self.ocp_test_provider_uuid = '3c6e687e-1a09-4a05-970c-2ccf44b0952e'
        self.aws_test_provider_uuid = '6e212746-484a-40cd-bba0-09a19d132d64'
