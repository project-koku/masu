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
from dateutil.relativedelta import relativedelta
from faker import Faker
from moto import mock_s3

from masu.processor.exceptions import MasuConfigurationError
from masu.processor.providers.aws.report_downloader import AWSReportDownloader
from masu.providers import DATA_DIR
from tests import MasuTestCase
from tests.providers.aws import SOME_AWS_REGIONS

FAKE = Faker()
SCHEMA = FAKE.word()
REPORT = FAKE.word()
BUCKET = FAKE.word()
PREFIX = FAKE.word()
REGION = random.choice(SOME_AWS_REGIONS)

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


class AWSReportDownloaderTest(MasuTestCase):
    """Test Cases for the AWS S3 functions."""

    fake = Faker()

    @patch('masu.processor.providers.aws.report_downloader.get_assume_role_session',
           return_value=FakeSession)
    def setUp(self, fake_session):
        os.makedirs(DATA_DIR, exist_ok=True)

        self.fake_schema_name = SCHEMA
        self.fake_report_name = REPORT
        self.fake_bucket_name = BUCKET
        self.fake_bucket_prefix = PREFIX
        self.selected_region = REGION

        self.mock_customer = Mock(**{
            'get_schema_name.return_value': self.fake_schema_name})

        self.mock_provider = Mock(**{
            'get_provider_resource_name.return_value': self.fake.word().lower(),
            'get_report_name.return_value': self.fake_report_name})

        self.mock_report_stats = Mock()

        self.report_downloader = AWSReportDownloader(**{'customer': self.mock_customer,
                                                        'provider': self.mock_provider,
                                                        'report_stats': self.mock_report_stats})

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
            expected_csv = '{}/{}/aws/{}'.format(DATA_DIR,
                                                 self.fake_schema_name,
                                                 csv_filename)
            expected_files.append(expected_csv)
        expected_manifest = '{}/{}/aws/{}-Manifest.json'.format(DATA_DIR,
                                                                self.fake_schema_name,
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
        expected_csv = '{}/{}/aws/{}'.format(DATA_DIR,
                                             self.fake_schema_name,
                                             selected_csv)
        self.assertEqual(out, [expected_csv])

    @mock_s3
    def test_download_file(self):
        fake_object = self.fake.word().lower()
        conn = boto3.resource('s3', region_name=self.selected_region)
        conn.create_bucket(Bucket=self.fake_bucket_name)
        conn.Object(self.fake_bucket_name, fake_object).put(Body='test')

        out = self.report_downloader.download_file(fake_object)
        self.assertEqual(out, DATA_DIR+'/'+self.fake_schema_name+'/aws/'+fake_object)

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
        expected_path = DATA_DIR+'/'+self.fake_schema_name+'/aws/mocked-report-file.csv'
        self.assertEqual(out, [expected_path])
