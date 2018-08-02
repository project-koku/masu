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


from celery import Celery
from celery.app.task import Task

from masu import create_app
from masu.celery import celery, update_celery_config
from masu.config import Config
from tests import MasuTestCase


class CeleryTest(MasuTestCase):
    """Test Cases for the Celery functions."""

    def test_make_celery(self):
        """Test that we can get a Celery object."""
        self.assertIsInstance(celery, Celery)

    def test_update_celery_config(self):
        """Test that the app config updates our celery instance."""
        test_celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)
        test_app = create_app(
            {
                'TESTING': True,
                'SQLALCHEMY_TRACK_MODIFICATIONS': False,
                'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db',
                'SCHEDULE_REPORT_CHECKS': True,
                'REMOVE_EXPIRED_REPORT_DATA_ON_DAY': '1'
            }
        )

        self.assertIsNone(test_celery.conf.task_routes)
        self.assertEqual(test_celery.conf.imports, ())
        self.assertEqual(test_celery.conf.beat_schedule, {})
        self.assertEqual(repr(test_celery.Task), repr(Task))

        update_celery_config(test_celery, test_app)

        self.assertIsNotNone(test_celery.conf.task_routes)
        self.assertNotEqual(test_celery.conf.imports, ())
        self.assertNotEqual(test_celery.conf.beat_schedule, {})
        self.assertNotEqual(repr(test_celery.Task), repr(Task))
