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

"""Test the remove temp file util function."""

import shutil
import tempfile
import json
from datetime import datetime
from masu.database.report_stats_db_accessor import ReportStatsDBAccessor
import masu.util.remove_temp_files as remove_files

from tests import MasuTestCase

class RemoveTempCurFilesTest(MasuTestCase):

    def test_remove_temp_cur_files(self):
        """Test to remove temporary cost usage files."""
        cur_dir = tempfile.mkdtemp()

        manifest_data = {"assemblyId": "6e019de5-a41d-4cdb-b9a0-99bfba9a9cb5"}
        manifest = '{}/{}'.format(cur_dir, 'koku-Manifest.json')
        with open(manifest, 'w') as outfile:
            json.dump(manifest_data, outfile)

        file_list = [{'file': '6e019de5-a41d-4cdb-b9a0-99bfba9a9cb5-koku-1.csv.gz',
                      'processed_date': datetime(year=2018, month=5, day=3)},
                     {'file': '6e019de5-a41d-4cdb-b9a0-99bfba9a9cb5-koku-2.csv.gz',
                      'processed_date': datetime(year=2018, month=5, day=3)},
                     {'file': '2aeb9169-2526-441c-9eca-d7ed015d52bd-koku-1.csv.gz',
                      'processed_date': datetime(year=2018, month=5, day=2)},
                     {'file': '6c8487e8-c590-4e6a-b2c2-91a2375c0bad-koku-1.csv.gz',
                      'processed_date': datetime(year=2018, month=5, day=1)},
                     {'file': '6c8487e8-c590-4e6a-b2c2-91a2375d0bed-koku-1.csv.gz',
                      'processed_date': None}]
        expected_delete_list = []
        for item in file_list:
            path = '{}/{}'.format(cur_dir, item['file'])
            f = open(path, 'w')
            stats = ReportStatsDBAccessor(item['file'])
            stats.update(last_completed_datetime=item['processed_date'])
            stats.commit()
            stats.close_session()
            f.close()
            if not item['file'].startswith(manifest_data.get('assemblyId')) and item['processed_date']:
                expected_delete_list.append(path)

        removed_files = remove_files.remove_temp_cur_files(cur_dir)
        self.assertEqual(sorted(removed_files), sorted(expected_delete_list))
        shutil.rmtree(cur_dir)
