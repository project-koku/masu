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

"""Test the DateAccessor object."""

from datetime import datetime
from unittest.mock import patch
from masu.config import Config
from masu.external.date_accessor import DateAccessor, DateAccessorError
from tests import MasuTestCase

import pytz


class DateAccessorTest(MasuTestCase):
    """Test Cases for the DateAccessor object."""

    @classmethod
    def setUpClass(cls):
        super(DateAccessorTest, cls).setUpClass()
        cls.initial_debug = Config.DEBUG
        cls.initial_override = Config.MASU_DATE_OVERRIDE

    @classmethod
    def tearDownClass(cls):
        super(DateAccessorTest, cls).tearDownClass()
        Config.DEBUG = cls.initial_debug
        Config.MASU_DATE_OVERRIDE = cls.initial_override

    def setUp(self):
        DateAccessor.mock_date_time = None

    def test_today_override(self):
        """Test today() with override."""
        Config.DEBUG = True
        Config.MASU_DATE_OVERRIDE = '2018-01-01 15:47:33'

        accessor = DateAccessor()

        today = accessor.today()
        self.assertEqual(today.year, 2018)
        self.assertEqual(today.month, 1)
        self.assertEqual(today.day, 1)

    def test_today_override_debug_false(self):
        """Test today() with override when debug is false."""
        Config.DEBUG = False
        Config.MASU_DATE_OVERRIDE = '2018-01-01 15:47:33'

        accessor = DateAccessor()

        today = accessor.today()
        expected_date = datetime.today()
        self.assertEqual(today.year, expected_date.year)
        self.assertEqual(today.month, expected_date.month)
        self.assertEqual(today.day, expected_date.day)

    def test_today_override_override_not_set(self):
        """Test today() with override set when debug is true."""
        Config.DEBUG = True
        Config.MASU_DATE_OVERRIDE = None

        accessor = DateAccessor()
        today = accessor.today()

        expected_date = datetime.today()
        self.assertEqual(today.year, expected_date.year)
        self.assertEqual(today.month, expected_date.month)
        self.assertEqual(today.day, expected_date.day)

    def test_today_override_override_not_set_debug_false(self):
        """Test today() with override not set when debug is false."""
        Config.DEBUG = False
        Config.MASU_DATE_OVERRIDE = None

        accessor = DateAccessor()
        today = accessor.today()

        expected_date = datetime.today()
        self.assertEqual(today.year, expected_date.year)
        self.assertEqual(today.month, expected_date.month)
        self.assertEqual(today.day, expected_date.day)

    def test_today_with_timezone_string(self):
        """Test that a timezone string works as expected."""
        string_tz = 'UTC'

        current_utc_time = datetime.utcnow()

        accessor = DateAccessor()
        result_time = accessor.today_with_timezone(string_tz)

        self.assertEqual(current_utc_time.date(), result_time.date())
        self.assertEqual(current_utc_time.hour, result_time.hour)
        self.assertEqual(current_utc_time.minute, result_time.minute)

    def test_today_with_timezone_object(self):
        """Test that a timezone string works as expected."""
        string_tz = 'US/Eastern'

        timezone = pytz.timezone(string_tz)

        current_eastern_time = datetime.now(timezone)

        accessor = DateAccessor()
        result_time = accessor.today_with_timezone(timezone)

        self.assertEqual(current_eastern_time.date(), result_time.date())
        self.assertEqual(current_eastern_time.hour, result_time.hour)
        self.assertEqual(current_eastern_time.minute, result_time.minute)

    def test_today_with_timezone_error_raised(self):
        """Test that an error is raised with an invalid timezone."""

        string_tz = 'Moon/Mare Tranquillitatis'
        accessor = DateAccessor()

        with self.assertRaises(DateAccessorError):
            accessor.today_with_timezone(string_tz)
