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

"""Test the OCP util."""

from masu.util.ocp import common as utils
from masu.exceptions import MasuProviderError
from masu.database import OCP_REPORT_TABLE_MAP
from masu.database.ocp_report_db_accessor import OCPReportDBAccessor
from masu.database.provider_db_accessor import ProviderDBAccessor
from masu.database.reporting_common_db_accessor import ReportingCommonDBAccessor
from tests.database.helpers import ReportObjectCreator
from masu.exceptions import (MasuConfigurationError, MasuProviderError)

from tests import MasuTestCase

class OCPUtilTests(MasuTestCase):
    """Test the OCP utility functions."""

    def setUp(self):
        super().setUp()
        self.common_accessor = ReportingCommonDBAccessor()
        self.column_map = self.common_accessor.column_map
        self.accessor = OCPReportDBAccessor(
            schema=self.test_schema,
            column_map=self.column_map
        )
        self.provider_accessor = ProviderDBAccessor(
            provider_uuid=self.ocp_test_provider_uuid
        )
        self.report_schema = self.accessor.report_schema
        self.creator = ReportObjectCreator(
            self.accessor,
            self.column_map,
            self.report_schema.column_types
        )
        self.all_tables = list(OCP_REPORT_TABLE_MAP.values())

        self.provider_id = self.provider_accessor.get_provider().id
        reporting_period = self.creator.create_ocp_report_period(provider_id=self.provider_id)
        report = self.creator.create_ocp_report(reporting_period, reporting_period.report_period_start)
        self.creator.create_ocp_usage_line_item(
            reporting_period,
            report
        )
        self.creator.create_ocp_storage_line_item(
            reporting_period,
            report
        )

    def tearDown(self):
        """Return the database to a pre-test state."""
        self.accessor._session.rollback()
        for table_name in self.all_tables:
            tables = self.accessor._get_db_obj_query(table_name).all()
            for table in tables:
                self.accessor._session.delete(table)
        self.accessor.commit()
        self.accessor.close_session()
        self.provider_accessor.close_session()
        self.common_accessor.close_session()

    def test_get_cluster_id_from_provider(self):
        """Test that the cluster ID is returned from OCP provider."""
        cluster_id = utils.get_cluster_id_from_provider(self.ocp_test_provider_uuid, self.test_schema)
        self.assertIsNotNone(cluster_id)

    def test_get_cluster_id_from_non_ocp_provider(self):
        """Test that Exception is raised for getting cluster ID on non-OCP provider."""
        with self.assertRaises(MasuProviderError):
            utils.get_cluster_id_from_provider(self.aws_test_provider_uuid, self.test_schema)

    def test_get_multiple_clusters_one_ocp_provider(self):
        """Test that Exception is raised for multiple cluster IDs on a single OCP provider."""
        self.creator.create_ocp_report_period(provider_id=self.provider_id)
        with self.assertRaises(MasuConfigurationError):
            utils.get_cluster_id_from_provider(self.ocp_test_provider_uuid, self.test_schema)
