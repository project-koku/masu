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
                #'CELERY_RESULT_BACKEND': 'db+sqlite:///test.db'
            }
        )
        self.client = self.app.test_client()
