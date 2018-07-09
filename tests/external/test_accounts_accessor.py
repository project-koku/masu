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

"""Test the CostUsageReportAccount object."""

from masu.external.accounts_accessor import AccountsAccessor, AccountsAccessorError
from masu.external.accounts.cost_usage_report_account import CostUsageReportAccount
from tests import MasuTestCase


class AccountsAccessorTest(MasuTestCase):
    """Test Cases for the AccountsAccessor object."""

    def test_get_accounts(self):
        """Test to get_access_credential"""
        account_objects = AccountsAccessor().get_accounts()

        if len(account_objects) != 1:
            self.fail('unexpected number of accounts')

        self.assertIsInstance(account_objects.pop(), CostUsageReportAccount)

        for account in account_objects:
            self.assertEqual(account.get_access_credential(), 'arn:aws:iam::111111111111:role/CostManagement')
            self.assertEqual(account.get_billing_source(), 'test-bucket')
            self.assertEqual(account.get_customer(), 'Test Customer')
            self.assertEqual(account.get_provider_type(), 'Test Provider')
            self.assertEqual(account.get_schema_name(), 'testcustomer')

    def test_invalid_source_specification(self):
        """Test that error is thrown with invalid account source."""

        with self.assertRaises(AccountsAccessorError):
            AccountsAccessor('bad')
