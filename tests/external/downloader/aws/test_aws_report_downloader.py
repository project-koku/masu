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

import json
import os.path
import random
import shutil
import tempfile
import uuid
from datetime import datetime
from unittest.mock import ANY, Mock, patch, PropertyMock

import boto3
from botocore.exceptions import ClientError
from dateutil.relativedelta import relativedelta
from faker import Faker
from moto import mock_s3

from masu.config import Config
from masu.database.report_stats_db_accessor import ReportStatsDBAccessor
from masu.exceptions import MasuProviderError
from masu.external.downloader.aws.aws_report_downloader import (AWSReportDownloader,
                                                                AWSReportDownloaderError)
from masu.external.downloader.aws import utils
from masu.external import AWS_REGIONS
from tests import MasuTestCase
from tests.external.downloader.aws import fake_arn

DATA_DIR = Config.TMP_DIR
FAKE = Faker()
CUSTOMER_NAME = FAKE.word()
REPORT = FAKE.word()
BUCKET = FAKE.word()
PREFIX = FAKE.word()

# the cn endpoints aren't supported by moto, so filter them out
AWS_REGIONS = list(filter(lambda reg: not reg.startswith('cn-'), AWS_REGIONS))
REGION = random.choice(AWS_REGIONS)

class FakeSession():
    """
    Fake Boto Session object.

    This is here because Moto doesn't mock out the 'cur' endpoint yet. As soon
    as Moto supports 'cur', this can be removed.
    """

    @staticmethod
    def client(service):
        fake_report = {'ReportDefinitions': [{
            'ReportName': REPORT,
            'TimeUnit': random.choice(['HOURLY','DAILY']),
            'Format': random.choice(['text', 'csv']),
            'Compression': random.choice(['ZIP','GZIP']),
            'S3Bucket': BUCKET,
            'S3Prefix': PREFIX,
            'S3Region': REGION,
        }]}

        # only mock the 'cur' boto client.
        if 'cur' in service:
            return Mock(**{'describe_report_definitions.return_value': fake_report})

        # pass-through requests for the 's3' boto client.
        with mock_s3():
            return boto3.client(service)

class FakeSessionNoReport():
    """
    Fake Boto Session object with no reports in the S3 bucket.

    This is here because Moto doesn't mock out the 'cur' endpoint yet. As soon
    as Moto supports 'cur', this can be removed.
    """

    @staticmethod
    def client(service):
        fake_report = {'ReportDefinitions': []}

        # only mock the 'cur' boto client.
        if 'cur' in service:
            return Mock(**{'describe_report_definitions.return_value': fake_report})

        # pass-through requests for the 's3' boto client.
        with mock_s3():
            return boto3.client(service)

class AWSReportDownloaderTest(MasuTestCase):
    """Test Cases for the AWS S3 functions."""

    fake = Faker()

    @patch('masu.external.downloader.aws.utils.get_assume_role_session',
           return_value=FakeSession)
    def setUp(self, fake_session):
        os.makedirs(DATA_DIR, exist_ok=True)

        self.fake_customer_name = CUSTOMER_NAME
        self.fake_report_name = REPORT
        self.fake_bucket_name = BUCKET
        self.fake_bucket_prefix = PREFIX
        self.selected_region = REGION

        auth_credential = fake_arn(service='iam', generate_account_id=True)

        self.report_downloader = AWSReportDownloader(**{'customer_name': self.fake_customer_name,
                                                        'auth_credential': auth_credential,
                                                        'bucket': self.fake_bucket_name,
                                                        'report_name': self.fake_report_name})

    def tearDown(self):
        shutil.rmtree(DATA_DIR, ignore_errors=True)

    @mock_s3
    def test_download_bucket(self):
        fake_report_date = datetime.today().replace(day=1)
        fake_report_end_date = fake_report_date + relativedelta(months=+1)
        report_range = '{}-{}'.format(fake_report_date.strftime('%Y%m%d'),
                                      fake_report_end_date.strftime('%Y%m%d'))

        # Moto setup
        conn = boto3.resource('s3', region_name=self.selected_region)
        conn.create_bucket(Bucket=self.fake_bucket_name)

        # push mocked csvs into Moto env
        fake_csv_files = []
        fake_csv_files_with_key = {}
        for x in range(0, random.randint(2, 10)):
            csv_filename = '{}.csv'.format('-'.join(self.fake.words(random.randint(2, 5))))
            fake_csv_files.append(csv_filename)

            # mocked report file definition
            fake_report_file = '{}/{}/{}/{}/{}'.format(
                self.fake_bucket_prefix,
                self.fake_report_name,
                report_range,
                uuid.uuid4(),
                csv_filename)
            fake_csv_files_with_key[csv_filename] = fake_report_file
            fake_csv_body = ','.join(self.fake.words(random.randint(5, 10)))
            conn.Object(self.fake_bucket_name,
                        fake_report_file).put(Body=fake_csv_body)
            key = conn.Object(self.fake_bucket_name, fake_report_file).get()
            self.assertEqual(fake_csv_body, str(key['Body'].read(), 'utf-8'))

        # mocked Manifest definition
        fake_object = '{}/{}/{}/{}-Manifest.json'.format(
            self.fake_bucket_prefix,
            self.fake_report_name,
            report_range,
            self.fake_report_name)
        fake_object_body = {'reportKeys': fake_csv_files}

        # push mocked manifest into Moto env
        conn.Object(self.fake_bucket_name,
                    fake_object).put(Body=json.dumps(fake_object_body))
        key = conn.Object(self.fake_bucket_name, fake_object).get()
        self.assertEqual(fake_object_body, json.load(key['Body']))

        # actual test
        out = self.report_downloader.download_bucket()
        expected_files = []
        for csv_filename in fake_csv_files:
            report_key = fake_csv_files_with_key.get(csv_filename)
            expected_assembly_id = utils.get_assembly_id_from_cur_key(report_key)
            expected_csv = '{}/{}/aws/{}-{}'.format(DATA_DIR,
                                                 self.fake_customer_name,
                                                 expected_assembly_id,
                                                 csv_filename)
            expected_files.append(expected_csv)
        expected_manifest = '{}/{}/aws/{}-Manifest.json'.format(DATA_DIR,
                                                                self.fake_customer_name,
                                                                self.fake_report_name)
        expected_files.append(expected_manifest)
        self.assertEqual(sorted(out), sorted(expected_files))


    @mock_s3
    def test_download_current_report(self):
        fake_report_date = datetime.today().replace(day=1)
        fake_report_end_date = fake_report_date + relativedelta(months=+1)
        report_range = '{}-{}'.format(fake_report_date.strftime('%Y%m%d'),
                                      fake_report_end_date.strftime('%Y%m%d'))

        # Moto setup
        conn = boto3.resource('s3', region_name=self.selected_region)
        conn.create_bucket(Bucket=self.fake_bucket_name)

        # push mocked csvs into Moto env
        fake_csv_files = {}
        for x in range(0, random.randint(2, 10)):
            csv_filename = '{}.csv'.format('-'.join(self.fake.words(random.randint(2, 5))))

            # mocked report file definition
            fake_report_file = '{}/{}/{}/{}/{}'.format(
                self.fake_bucket_prefix,
                self.fake_report_name,
                report_range,
                uuid.uuid4(),
                csv_filename)
            fake_csv_files[csv_filename] = fake_report_file

            fake_csv_body = ','.join(self.fake.words(random.randint(5, 10)))
            conn.Object(self.fake_bucket_name,
                        fake_report_file).put(Body=fake_csv_body)
            key = conn.Object(self.fake_bucket_name, fake_report_file).get()
            self.assertEqual(fake_csv_body, str(key['Body'].read(), 'utf-8'))

        # mocked Manifest definition
        selected_csv = random.choice(list(fake_csv_files.keys()))
        fake_object = '{}/{}/{}/{}-Manifest.json'.format(
            self.fake_bucket_prefix,
            self.fake_report_name,
            report_range,
            self.fake_report_name)
        fake_object_body = {'reportKeys': [fake_csv_files[selected_csv]]}

        # push mocked manifest into Moto env
        conn.Object(self.fake_bucket_name,
                    fake_object).put(Body=json.dumps(fake_object_body))
        key = conn.Object(self.fake_bucket_name, fake_object).get()
        self.assertEqual(fake_object_body, json.load(key['Body']))

        # actual test
        out = self.report_downloader.download_current_report()
        files_list = []
        for cur_dict in out:
            files_list.append(cur_dict['file'])
            self.assertIsNotNone(cur_dict['compression'])

        report_key = fake_object_body.get('reportKeys').pop()
        expected_assembly_id = utils.get_assembly_id_from_cur_key(report_key)
        expected_csv = '{}/{}/aws/{}-{}'.format(DATA_DIR,
                                             self.fake_customer_name,
                                             expected_assembly_id,
                                             selected_csv)
        self.assertEqual(files_list, [expected_csv])

        # Verify etag is stored
        for cur_dict in out:
            cur_file = cur_dict['file']
            file_name = cur_file.split('/')[-1]
            stats_recorder = ReportStatsDBAccessor(file_name)
            self.assertIsNotNone(stats_recorder.get_etag())

            # Cleanup
            stats_recorder.remove()
            stats_recorder.commit()

            stats_recorder2 = ReportStatsDBAccessor(file_name)
            self.assertIsNone(stats_recorder2.get_etag())


    @mock_s3
    def test_download_file(self):
        fake_object = self.fake.word().lower()
        conn = boto3.resource('s3', region_name=self.selected_region)
        conn.create_bucket(Bucket=self.fake_bucket_name)
        conn.Object(self.fake_bucket_name, fake_object).put(Body='test')

        out, _ = self.report_downloader.download_file(fake_object)
        self.assertEqual(out, DATA_DIR+'/'+self.fake_customer_name+'/aws/'+fake_object)

    @mock_s3
    def test_download_file_missing_key(self):
        fake_object = self.fake.word().lower()
        conn = boto3.resource('s3', region_name=self.selected_region)
        conn.create_bucket(Bucket=self.fake_bucket_name)
        conn.Object(self.fake_bucket_name, fake_object).put(Body='test')

        missing_key = 'missing' + fake_object
        with self.assertRaises(AWSReportDownloaderError) as error:
            self.report_downloader.download_file(missing_key)
        expected_err = 'Unable to find {} in S3 Bucket: {}'.format(missing_key, self.fake_bucket_name)
        self.assertEqual(expected_err, str(error.exception))

    @mock_s3
    def test_download_file_other_error(self):
        fake_object = self.fake.word().lower()
        # No S3 bucket created
        with self.assertRaises(AWSReportDownloaderError) as error:
            self.report_downloader.download_file(fake_object)
        self.assertTrue('NoSuchBucket' in str(error.exception))

    @mock_s3
    def test_download_report(self):
        fake_report_date = self.fake.date_time().replace(day=1)
        fake_report_end_date = fake_report_date + relativedelta(months=+1)
        report_range = '{}-{}'.format(fake_report_date.strftime('%Y%m%d'),
                                      fake_report_end_date.strftime('%Y%m%d'))

        # mocked report file definition
        fake_report_file = '{}/{}/{}/{}/{}.csv'.format(
            self.fake_bucket_prefix,
            self.fake_report_name,
            report_range,
            uuid.uuid4(),
            'mocked-report-file')

        # mocked Manifest definition
        fake_object = '{}/{}/{}/{}-Manifest.json'.format(
            self.fake_bucket_prefix,
            self.fake_report_name,
            report_range,
            self.fake_report_name)
        fake_object_body = {'reportKeys':[fake_report_file]}

        # Moto setup
        conn = boto3.resource('s3', region_name=self.selected_region)
        conn.create_bucket(Bucket=self.fake_bucket_name)

        # push mocked manifest into Moto env
        conn.Object(self.fake_bucket_name,
                    fake_object).put(Body=json.dumps(fake_object_body))
        key = conn.Object(self.fake_bucket_name, fake_object).get()
        self.assertEqual(fake_object_body, json.load(key['Body']))

        # push mocked csv into Moto env
        fake_csv_body = ','.join(self.fake.words(random.randint(5, 10)))
        conn.Object(self.fake_bucket_name,
                    fake_report_file).put(Body=fake_csv_body)
        key = conn.Object(self.fake_bucket_name, fake_report_file).get()
        self.assertEqual(fake_csv_body, str(key['Body'].read(), 'utf-8'))

        # actual test
        out = self.report_downloader.download_report(fake_report_date)
        files_list = []
        for cur_dict in out:
            files_list.append(cur_dict['file'])
            self.assertIsNotNone(cur_dict['compression'])

        report_key = fake_object_body.get('reportKeys').pop()
        expected_assembly_id = utils.get_assembly_id_from_cur_key(report_key)

        expected_path_base = '{}/{}/{}/{}-{}'
        expected_path = expected_path_base.format(DATA_DIR,
                                                  self.fake_customer_name,
                                                  'aws',
                                                  expected_assembly_id,
                                                  'mocked-report-file.csv')
        self.assertEqual(files_list, [expected_path])

        # Attempt to download again
        out = self.report_downloader.download_report(fake_report_date)
        files_list = []
        for cur_dict in out:
            files_list.append(cur_dict['file'])
            self.assertIsNotNone(cur_dict['compression'])

        self.assertEqual(files_list, [expected_path])

    @mock_s3
    @patch('masu.external.downloader.aws.utils.get_assume_role_session',
           return_value=FakeSession)
    def test_missing_report_name(self, fake_session):
        """Test downloading a report with an invalid report name."""
        auth_credential = fake_arn(service='iam', generate_account_id=True)

        with self.assertRaises(MasuProviderError):
            AWSReportDownloader(self.fake_customer_name,
                                auth_credential,
                                's3_bucket',
                                'wrongreport')


    @mock_s3
    @patch('masu.external.downloader.aws.utils.get_assume_role_session',
           return_value=FakeSession)
    def test_download_default_report(self, fake_session):
        fake_report_date = self.fake.date_time().replace(day=1)
        fake_report_end_date = fake_report_date + relativedelta(months=+1)
        report_range = '{}-{}'.format(fake_report_date.strftime('%Y%m%d'),
                                      fake_report_end_date.strftime('%Y%m%d'))

        # mocked report file definition
        fake_report_file = '{}/{}/{}/{}/{}.csv'.format(
            self.fake_bucket_prefix,
            self.fake_report_name,
            report_range,
            uuid.uuid4(),
            'mocked-report-file')

        # mocked Manifest definition
        fake_object = '{}/{}/{}/{}-Manifest.json'.format(
            self.fake_bucket_prefix,
            self.fake_report_name,
            report_range,
            self.fake_report_name)
        fake_object_body = {'reportKeys':[fake_report_file]}

        # Moto setup
        conn = boto3.resource('s3', region_name=self.selected_region)
        conn.create_bucket(Bucket=self.fake_bucket_name)

        # push mocked manifest into Moto env
        conn.Object(self.fake_bucket_name,
                    fake_object).put(Body=json.dumps(fake_object_body))
        key = conn.Object(self.fake_bucket_name, fake_object).get()
        self.assertEqual(fake_object_body, json.load(key['Body']))

        # push mocked csv into Moto env
        fake_csv_body = ','.join(self.fake.words(random.randint(5, 10)))
        conn.Object(self.fake_bucket_name,
                    fake_report_file).put(Body=fake_csv_body)
        key = conn.Object(self.fake_bucket_name, fake_report_file).get()
        self.assertEqual(fake_csv_body, str(key['Body'].read(), 'utf-8'))

        # actual test
        auth_credential = fake_arn(service='iam', generate_account_id=True)
        downloader = AWSReportDownloader(self.fake_customer_name,
                                         auth_credential,
                                         self.fake_bucket_name)
        self.assertEqual(downloader.report_name, self.fake_report_name)

    @mock_s3
    @patch('masu.external.downloader.aws.utils.get_assume_role_session',
           return_value=FakeSessionNoReport)
    @patch('masu.external.downloader.aws.utils.get_cur_report_definitions',
           return_value=[])
    def test_download_default_report_no_report_found(self, fake_session, fake_report_list):
        auth_credential = fake_arn(service='iam', generate_account_id=True)

        with self.assertRaises(MasuProviderError):
            AWSReportDownloader(self.fake_customer_name,
                                auth_credential,
                                self.fake_bucket_name)
