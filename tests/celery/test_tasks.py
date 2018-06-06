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
"""Test the celery functions."""

from unittest.mock import Mock

from masu.celery.tasks import test
from tests import MasuTestCase


class TaskTest(MasuTestCase):
    """Test Cases for the Processor functions."""

    def test_test_task(self):
        """Test that we can run the test task."""
        ret = test('foo')
        self.assertIsInstance(ret, Mock)
