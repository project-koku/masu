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

"""Test the common util functions."""

import json
from datetime import datetime
from decimal import Decimal

import masu.util.common as common_utils

from tests import MasuTestCase

class CommonUtilTests(MasuTestCase):

    def test_extract_uuids_from_string(self):
        """Test that a uuid is extracted from a string."""

        assembly_id = '882083b7-ea62-4aab-aa6a-f0d08d65ee2b'
        cur_key = '/koku/20180701-20180801/{}/koku-1.csv.gz'.format(assembly_id)

        uuids = common_utils.extract_uuids_from_string(cur_key)
        self.assertEqual(len(uuids), 1)
        self.assertEqual(uuids.pop(), assembly_id)

    def test_extract_uuids_from_string_capitals(self):
        """Test that a uuid is extracted from a string with capital letters."""

        assembly_id = '882083B7-EA62-4AAB-aA6a-f0d08d65Ee2b'
        cur_key = '/koku/20180701-20180801/{}/koku-1.csv.gz'.format(assembly_id)

        uuids = common_utils.extract_uuids_from_string(cur_key)
        self.assertEqual(len(uuids), 1)
        self.assertEqual(uuids.pop(), assembly_id)

    def test_stringify_json_data_list(self):
        """Test that each element of JSON is returned as a string."""
        data = [
            {
                'datetime': datetime.utcnow(),
                'float': 1.2,
                'int': 1,
                'str': 'string'
            },
            {'Decimal': Decimal('1.2')}
        ]

        with self.assertRaises(TypeError):
            json.dumps(data)

        result = common_utils.stringify_json_data(data)

        self.assertIsInstance(result[0]['datetime'], str)
        self.assertIsInstance(result[0]['float'], str)
        self.assertIsInstance(result[0]['int'], str)
        self.assertIsInstance(result[0]['str'], str)
        self.assertIsInstance(result[1]['Decimal'], str)

    def test_stringify_json_data_dict(self):
        """Test that the dict block is covered."""
        data = {
            'datetime': datetime.utcnow(),
            'float': 1.2,
            'int': 1,
            'str': 'string',
            'Decimal': Decimal('1.2')
        }

        with self.assertRaises(TypeError):
            json.dumps(data)

        result = common_utils.stringify_json_data(data)

        self.assertIsInstance(result['datetime'], str)
        self.assertIsInstance(result['float'], str)
        self.assertIsInstance(result['int'], str)
        self.assertIsInstance(result['str'], str)
        self.assertIsInstance(result['Decimal'], str)
