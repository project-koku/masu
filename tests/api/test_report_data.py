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

"""Test the report_data endpoint view."""

import datetime
from unittest.mock import patch
from urllib.parse import urlencode

from celery.result import AsyncResult

from tests import MasuTestCase


class ReportDataTests(MasuTestCase):
    """Test Cases for the report_data endpoint."""

    @patch('masu.api.report_data.update_summary_tables')
    def test_get_report_data(self, mock_update):
        """Test the GET report_data endpoint."""
        start_date = datetime.date.today()
        params = {'schema': 'acct10001org20002', 'start_date': start_date}
        query_string = urlencode(params)
        expected_key = 'Report Data Task ID'

        # self.client.get()
        response = self.client.get('/api/v1/report_data/',
                                   query_string=query_string)
        body = response.json

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertIn(expected_key, body)
        mock_update.delay.assert_called_with(
            params['schema'],
            str(params['start_date'])
        )

    @patch('masu.api.report_data.update_summary_tables')
    def test_get_report_data_schema_missing(self, mock_update):
        """Test GET report_data endpoint returns a 400 for missing schema."""
        start_date = datetime.date.today()
        params = {'start_date': start_date}
        query_string = urlencode(params)
        expected_key = 'Error'
        expected_message = 'schema is a required parameter.'

        # self.client.get()
        response = self.client.get('/api/v1/report_data/',
                                   query_string=query_string)
        body = response.json

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertIn(expected_key, body)
        self.assertEqual(body[expected_key], expected_message)

    @patch('masu.api.report_data.update_summary_tables')
    def test_get_report_data_date_missing(self, mock_update):
        """Test GET report_data endpoint returns a 400 for missing date."""
        params = {'schema': 'acct10001org20002'}
        query_string = urlencode(params)
        expected_key = 'Error'
        expected_message = 'start_date is a required parameter.'

        # self.client.get()
        response = self.client.get('/api/v1/report_data/',
                                   query_string=query_string)
        body = response.json

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertIn(expected_key, body)
        self.assertEqual(body[expected_key], expected_message)

    @patch('masu.api.report_data.update_summary_tables')
    def test_get_report_data_with_end_date(self, mock_update):
        """Test GET report_data endpoint with end date."""
        start_date = datetime.date.today()
        end_date = start_date + datetime.timedelta(days=1)
        params = {
            'schema': 'acct10001org20002',
            'start_date': start_date,
            'end_date': end_date
        }
        query_string = urlencode(params)
        expected_key = 'Report Data Task ID'

        # self.client.get()
        response = self.client.get('/api/v1/report_data/',
                                   query_string=query_string)
        body = response.json

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertIn(expected_key, body)
        mock_update.delay.assert_called_with(
            params['schema'],
            str(params['start_date']),
            str(params['end_date'])
        )
