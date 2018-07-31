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

"""Test the expired_endpoint endpoint view."""

from unittest.mock import patch
from masu.config import Config
from masu.external.accounts_accessor import (AccountsAccessor, AccountsAccessorError)
from masu.processor.expired_data_remover import ExpiredDataRemover
from celery.result import AsyncResult
from tests import MasuTestCase


class ExpiredDataTest(MasuTestCase):
    """Test Cases for the expired_data endpoint."""

    @patch.object(AccountsAccessor, 'get_accounts')
    @patch.object(ExpiredDataRemover, 'remove')
    def test_get_expired_data(self, mock_remover, mock_accessor):
        """Test the download endpoint."""
        expected_account_payer_id = '999999999'
        expected_billing_period_start = '2018-05-01 00:00:00+00:00'
        mock_accessor.return_value = [{'access_credential': 'arn:aws:iam::111111111111:role/CostManagement',
                                       'billing_source': 'test-bucket',
                                       'customer_name': 'Test Customer',
                                       'provider_type': 'AWS',
                                       'schema_name': 'testcustomer'}]
        mock_remover.return_value = [{'account_payer_id': expected_account_payer_id,
                                      'billing_period_start': expected_billing_period_start}]

        response = self.client.get('/api/v1/expired_data/')
        body = response.json

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')

        self.assertIn('Expired Data', body)

        self.assertIn(expected_account_payer_id, body.get('Expired Data'))
        self.assertIn(expected_billing_period_start, body.get('Expired Data'))

    @patch.object(Config, 'DEBUG')
    @patch.object(AccountsAccessor, 'get_accounts')
    @patch.object(ExpiredDataRemover, 'remove')
    def test_delete_expired_data(self, mock_remover, mock_accessor, mock_debug):
        """Test the download endpoint."""
        expected_account_payer_id = '999999999'
        expected_billing_period_start = '2018-05-01 00:00:00+00:00'
        mock_accessor.return_value = [{'access_credential': 'arn:aws:iam::111111111111:role/CostManagement',
                                       'billing_source': 'test-bucket',
                                       'customer_name': 'Test Customer',
                                       'provider_type': 'AWS',
                                       'schema_name': 'testcustomer'}]
        mock_remover.return_value = [{'account_payer_id': expected_account_payer_id,
                                      'billing_period_start': expected_billing_period_start}]
        mock_debug = True

        response = self.client.delete('/api/v1/expired_data/')
        body = response.json

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')

        self.assertIn('Removed Data', body)

        self.assertIn(expected_account_payer_id, body.get('Removed Data'))
        self.assertIn(expected_billing_period_start, body.get('Removed Data'))

    @patch.object(AccountsAccessor, 'get_accounts')
    @patch.object(ExpiredDataRemover, 'remove')
    def test_get_expired_data_error(self, mock_remover, mock_accessor):
        """Test the download endpoint."""
        expected_account_payer_id = '999999999'
        expected_billing_period_start = '2018-05-01 00:00:00+00:00'
        mock_accessor.side_effect = AccountsAccessorError('test error')
        mock_remover.return_value = [{'account_payer_id': expected_account_payer_id,
                                      'billing_period_start': expected_billing_period_start}]

        response = self.client.get('/api/v1/expired_data/')
        body = response.json

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')

        self.assertIn('Expired Data', body)
        self.assertIn('[]', body.get('Expired Data'))
