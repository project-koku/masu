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

"""Test the AWS S3 utility functions."""

import os.path
import random
import tempfile
from unittest.mock import ANY, Mock, patch, PropertyMock

from faker import Faker

from masu.providers import DATA_DIR
from masu.providers.aws import s3
from tests import MasuTestCase
from tests.providers.aws import SOME_AWS_REGIONS

class AWSS3Test(MasuTestCase):
    """Test Cases for the AWS S3 functions."""

    fake = Faker()

    @patch('masu.providers.aws.s3.os.makedirs')
    @patch('masu.providers.aws.s3.boto3.resource')
    def test_get_file_from_s3(self, mock_s3, mock_os):
        """Test the get_file_from_s3 delivers a file."""
        schema = self.fake.word().lower()
        region = random.choice(SOME_AWS_REGIONS)
        bucket_name = self.fake.word().lower()
        key = self.fake.file_name()

        expected = f'{DATA_DIR}/{schema}/aws/{key}'

        def save_file(directory, file_name):
            with open(f'{directory}/{file_name}', 'w') as f:
                f.write('\n')
            return file_name

        mock_bucket = mock_s3.return_value.Bucket
        mock_os.return_value = None

        with tempfile.TemporaryDirectory() as tmp_dir:
            mock_bucket.download_file.side_effect = save_file(tmp_dir, key)

            result = s3.get_file_from_s3(schema, region, bucket_name, key)

            self.assertEqual(result, expected)
            # See if the file exists in the directory
            self.assertTrue(os.path.isfile(f'{tmp_dir}/{key}'))
