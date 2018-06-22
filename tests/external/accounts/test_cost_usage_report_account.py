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

from masu.external.accounts.cost_usage_report_account import CostUsageReportAccount
from tests import MasuTestCase


class CostUsageReportAccountTest(MasuTestCase):
    """Test Cases for the CostUsageReportAccount object."""

    def setUp(self):
        self.auth_string = 'my_authenticaiton_string'
        self.billing_source = 'my_billing_source'
        self.customer_name = 'the_customer_name'
        self.provider = 'test_provider'
        self.schema_name = 'testschema'

        args = {'authentication': self.auth_string,
                'billing_source': self.billing_source,
                'customer_name': self.customer_name,
                'provider_type': self.provider,
                'schema_name': self.schema_name}
        self.account = CostUsageReportAccount(**args)

    def test_get_access_credentials(self):
        """Test to get_access_credential"""
        self.assertEqual(self.account.get_access_credential(), self.auth_string)

    def test_get_billing_source(self):
        """Test to get_billing_source"""
        self.assertEqual(self.account.get_billing_source(), self.billing_source)

    def test_get_customer_name(self):
        """Test to get_customer_name"""
        self.assertEqual(self.account.get_customer(), self.customer_name)

    def test_get_provider_type(self):
        """Test to get_provider"""
        self.assertEqual(self.account.get_provider_type(), self.provider)

    def test_get_schema_name(self):
        """Test to get_schema_name"""
        self.assertEqual(self.account.get_schema_name(), self.schema_name)
