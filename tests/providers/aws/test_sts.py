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

import random
import string
from unittest import TestCase

import boto3
from faker import Faker
from moto import mock_sts

from masu.providers.aws.sts import get_assume_role_session

class TestSTS(TestCase):
    fake = Faker()

    @mock_sts
    def test_get_assume_role_session(self):
        account = ''.join(random.choices(string.digits, k=12))
        arn = 'arn:aws:iam::{}:{}/{}'.format(account,
                                             self.fake.word(),
                                             self.fake.word())

        session = get_assume_role_session(arn)
        self.assertIsInstance(session, boto3.Session)
