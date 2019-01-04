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

from dateutil.relativedelta import relativedelta

import random
import string
from unittest import TestCase
from datetime import datetime
from unittest.mock import patch, Mock

import boto3
from botocore.exceptions import ClientError
from faker import Faker

from masu.util.aws import common as utils
from tests.external.downloader.aws import (fake_arn,
                                           fake_aws_account_id)
from masu.external import AWS_REGIONS
from tests.external.downloader.aws.test_aws_report_downloader import FakeSession

# the cn endpoints aren't supported by moto, so filter them out
AWS_REGIONS = list(filter(lambda reg: not reg.startswith('cn-'), AWS_REGIONS))
REGION = random.choice(AWS_REGIONS)

NAME = Faker().word()
BUCKET = Faker().word()
PREFIX = Faker().word()
FORMAT = random.choice(['text', 'csv'])
COMPRESSION = random.choice(['ZIP', 'GZIP'])
REPORT_DEFS = [{'ReportName': NAME,
                'TimeUnit': 'DAILY',
                'Format': FORMAT,
                'Compression': COMPRESSION,
                'S3Bucket': BUCKET,
                'S3Prefix': PREFIX,
                'S3Region': REGION}]
MOCK_BOTO_CLIENT = Mock()
response = {
    'Credentials': {
        'AccessKeyId': 'mock_access_key_id',
        'SecretAccessKey': 'mock_secret_access_key',
        'SessionToken': 'mock_session_token'
    }
}
MOCK_BOTO_CLIENT.assume_role.return_value = response


class TestAWSUtils(TestCase):
    fake = Faker()

    def setUp(self):
        self.account_id = fake_aws_account_id()
        self.arn = fake_arn(account_id=self.account_id,
                            region=REGION,
                            service='iam')

    @patch('masu.util.aws.common.boto3.client', return_value=MOCK_BOTO_CLIENT)
    def test_get_assume_role_session(self, mock_boto_client):
        session = utils.get_assume_role_session(self.arn)
        self.assertIsInstance(session, boto3.Session)

    def test_month_date_range(self):
        today = datetime.now()
        out = utils.month_date_range(today)

        start_month = today.replace(day=1, second=1, microsecond=1)
        end_month = start_month + relativedelta(months=+1)
        timeformat = '%Y%m%d'
        expected_string = '{}-{}'.format(start_month.strftime(timeformat),
                                         end_month.strftime(timeformat))

        self.assertEqual(out, expected_string)

    @patch('masu.util.aws.common.get_cur_report_definitions',
           return_value=REPORT_DEFS)
    def test_cur_report_names_in_bucket(self, fake_report_defs):
        session = Mock()
        report_names = utils.get_cur_report_names_in_bucket(self.account_id,
                                                            BUCKET,
                                                            session)
        self.assertIn(NAME, report_names)

    @patch('masu.util.aws.common.get_cur_report_definitions',
           return_value=REPORT_DEFS)
    def test_cur_report_names_in_bucket_malformed(self, fake_report_defs):
        session = Mock()
        report_names = utils.get_cur_report_names_in_bucket(self.account_id,
                                                            'wrong-bucket',
                                                            session)
        self.assertNotIn(NAME, report_names)

    def test_get_cur_report_definitions(self):
        session = FakeSession()
        defs = utils.get_cur_report_definitions(self.arn, session)
        self.assertEqual(len(defs), 1)

    @patch('masu.util.aws.common.get_assume_role_session',
           return_value=FakeSession)
    def test_get_cur_report_definitions_no_session(self, fake_session):
        defs = utils.get_cur_report_definitions(self.arn)
        self.assertEqual(len(defs), 1)

    def test_get_account_alias_from_role_arn(self):
        mock_account_id = '111111111111'
        role_arn = 'arn:aws:iam::{}:role/CostManagement'.format(mock_account_id)
        mock_alias = 'test-alias'

        session = Mock()
        mock_client = Mock()
        mock_client.list_account_aliases.return_value = {
            'AccountAliases': [mock_alias]
        }
        session.client.return_value = mock_client
        account_id, account_alias = utils.get_account_alias_from_role_arn(role_arn, session)
        self.assertEqual(mock_account_id, account_id)
        self.assertEqual(mock_alias, account_alias)

    @patch('masu.util.aws.common.get_assume_role_session')
    def test_get_account_alias_from_role_arn_no_policy(self, mock_get_role_session):
        mock_session = mock_get_role_session.return_value
        mock_client = mock_session.client
        mock_client.return_value.list_account_aliases.side_effect = ClientError({}, 'Error')

        mock_account_id = '111111111111'
        role_arn = 'arn:aws:iam::{}:role/CostManagement'.format(mock_account_id)

        account_id, account_alias = utils.get_account_alias_from_role_arn(role_arn, mock_session)
        self.assertEqual(mock_account_id, account_id)
        self.assertEqual(mock_account_id, account_alias)

    @patch('masu.util.aws.common.get_assume_role_session')
    def test_get_account_alias_from_role_arn_no_session(self,
                                                        mock_get_role_session):
        mock_session = mock_get_role_session.return_value
        mock_client = mock_session.client
        mock_client.return_value.list_account_aliases.side_effect = ClientError({}, 'Error')

        mock_account_id = '111111111111'
        role_arn = 'arn:aws:iam::{}:role/CostManagement'.format(mock_account_id)

        account_id, account_alias = utils.get_account_alias_from_role_arn(role_arn)
        self.assertEqual(mock_account_id, account_id)
        self.assertEqual(mock_account_id, account_alias)

    def test_get_assembly_id_from_cur_key(self):
        """Test get_assembly_id_from_cur_key is successful."""
        expected_assembly_id = '882083b7-ea62-4aab-aa6a-f0d08d65ee2b'
        input_key = f'/koku/20180701-20180801/{expected_assembly_id}/koku-1.csv.gz'
        assembly_id = utils.get_assembly_id_from_cur_key(input_key)
        self.assertEqual(expected_assembly_id, assembly_id)

    def test_get_local_file_name_with_assembly(self):
        """ Test get_local_file_name is successful with assembly ID."""
        expected_assembly_id = '882083b7-ea62-4aab-aa6a-f0d08d65ee2b'
        input_key = f'/koku/20180701-20180801/{expected_assembly_id}/koku-1.csv.gz'
        expected_local_file = f'{expected_assembly_id}-koku-1.csv.gz'
        local_file = utils.get_local_file_name(input_key)
        self.assertEqual(expected_local_file, local_file)

    def test_get_local_file_name_no_assembly(self):
        """ Test get_local_file_name is successful with no assembly ID."""
        input_key = '/koku/20180701-20180801/koku-Manifest.json'
        expected_local_file = 'koku-Manifest.json'
        local_file = utils.get_local_file_name(input_key)
        self.assertEqual(expected_local_file, local_file)


class AwsArnTest(TestCase):
    """AwnArn class test case."""
    fake = Faker()

    def test_parse_arn_with_region_and_account(self):
        """Assert successful account ID parsing from a well-formed ARN."""
        mock_account_id = fake_aws_account_id()
        mock_arn = fake_arn(account_id=mock_account_id,
                            region='test-region-1')

        arn_object = utils.AwsArn(mock_arn)

        partition = arn_object.partition
        self.assertIsNotNone(partition)

        service = arn_object.service
        self.assertIsNotNone(service)

        region = arn_object.region
        self.assertIsNotNone(region)

        account_id = arn_object.account_id
        self.assertIsNotNone(account_id)

        resource_type = arn_object.resource_type
        self.assertIsNotNone(resource_type)

        resource_separator = arn_object.resource_separator
        self.assertIsNotNone(resource_separator)

        resource = arn_object.resource
        self.assertIsNotNone(resource)

        reconstructed_arn = 'arn:' + \
                            partition + ':' + \
                            service + ':' + \
                            region + ':' + \
                            account_id + ':' + \
                            resource_type + \
                            resource_separator + \
                            resource

        self.assertEqual(mock_account_id, account_id)
        self.assertEqual(mock_arn, reconstructed_arn)

    def test_parse_arn_without_region_or_account(self):
        """Assert successful ARN parsing without a region or an account id."""
        mock_arn = fake_arn()
        arn_object = utils.AwsArn(mock_arn)

        region = arn_object.region
        self.assertEqual(region, None)

        account_id = arn_object.account_id
        self.assertEqual(account_id, None)

    def test_parse_arn_with_slash_separator(self):
        """Assert successful ARN parsing with a slash separator."""
        mock_arn = fake_arn(resource_separator='/')
        arn_object = utils.AwsArn(mock_arn)

        resource_type = arn_object.resource_type
        self.assertIsNotNone(resource_type)

        resource_separator = arn_object.resource_separator
        self.assertEqual(resource_separator, '/')

        resource = arn_object.resource
        self.assertIsNotNone(resource)

    def test_parse_arn_with_custom_resource_type(self):
        """Assert valid ARN when resource type contains extra characters."""
        mock_arn = 'arn:aws:fakeserv:test-reg-1:012345678901:test.res type:foo'
        arn_object = utils.AwsArn(mock_arn)

        resource_type = arn_object.resource_type
        self.assertIsNotNone(resource_type)

        resource = arn_object.resource
        self.assertIsNotNone(resource)

    def test_error_from_invalid_arn(self):
        """Assert error in account ID parsing from a badly-formed ARN."""
        mock_arn = self.fake.text()
        with self.assertRaises(SyntaxError):
            utils.AwsArn(mock_arn)
