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

from masu.config import Config
from masu.database.report_manifest_db_accessor import ReportManifestDBAccessor
from masu.database.report_stats_db_accessor import ReportStatsDBAccessor
from masu.exceptions import MasuProviderError
from masu.external.downloader.aws.aws_report_downloader import (AWSReportDownloader,
                                                                AWSReportDownloaderError,
                                                                AWSReportDownloaderNoFileError)
from masu.external.report_downloader import ReportDownloader
from masu.util.aws import common as utils
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


def mock_kwargs_error(**kwargs):
    """Mock side effect method for raising an AWSReportDownloaderError."""
    raise AWSReportDownloaderError()


def mock_download_file_error(manifest):
    """Mock side effect for raising an AWSReportDownloaderNoFileError."""
    raise AWSReportDownloaderNoFileError()


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
            'TimeUnit': random.choice(['HOURLY', 'DAILY']),
            'Format': random.choice(['text', 'csv']),
            'Compression': random.choice(['ZIP', 'GZIP']),
            'S3Bucket': BUCKET,
            'S3Prefix': PREFIX,
            'S3Region': REGION,
        }]}

        if 'cur' in service:
            return Mock(**{'describe_report_definitions.return_value': fake_report})
        else:
            return Mock()


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
        else:
            return Mock()


class FakeSessionDownloadError():
    """
    Fake Boto Session object.

    This is here because Moto doesn't mock out the 'cur' endpoint yet. As soon
    as Moto supports 'cur', this can be removed.
    """

    @staticmethod
    def client(service):
        fake_report = {'ReportDefinitions': [{
            'ReportName': REPORT,
            'TimeUnit': random.choice(['HOURLY', 'DAILY']),
            'Format': random.choice(['text', 'csv']),
            'Compression': random.choice(['ZIP', 'GZIP']),
            'S3Bucket': BUCKET,
            'S3Prefix': PREFIX,
            'S3Region': REGION,
        }]}

        if 'cur' in service:
            return Mock(**{'describe_report_definitions.return_value': fake_report})
        elif 's3' in service:
            return Mock(**{'get_object.side_effect': mock_kwargs_error})
        else:
            return Mock()


class AWSReportDownloaderTest(MasuTestCase):
    """Test Cases for the AWS S3 functions."""

    fake = Faker()

    @classmethod
    def setUpClass(cls):
        cls.fake_customer_name = CUSTOMER_NAME
        cls.fake_report_name = REPORT
        cls.fake_bucket_prefix = PREFIX
        cls.fake_bucket_name = BUCKET
        cls.selected_region = REGION
        cls.auth_credential = fake_arn(service='iam', generate_account_id=True)

        cls.manifest_accessor = ReportManifestDBAccessor()

    @classmethod
    def tearDownClass(cls):
        cls.manifest_accessor.close_session()

    @patch('masu.util.aws.common.get_assume_role_session',
           return_value=FakeSession)
    def setUp(self, fake_session):
        os.makedirs(DATA_DIR, exist_ok=True)

        self.report_downloader = ReportDownloader(self.fake_customer_name,
                                                  self.auth_credential,
                                                  self.fake_bucket_name,
                                                  'AWS',
                                                  1)
        self.aws_report_downloader = AWSReportDownloader(**{'customer_name': self.fake_customer_name,
                                                            'auth_credential': self.auth_credential,
                                                            'bucket': self.fake_bucket_name,
                                                            'report_name': self.fake_report_name,
                                                            'provider_id': 1})

    def tearDown(self):
        shutil.rmtree(DATA_DIR, ignore_errors=True)

        manifests = self.manifest_accessor._get_db_obj_query().all()
        for manifest in manifests:
            self.manifest_accessor.delete(manifest)
        self.manifest_accessor.commit()

    @patch('masu.external.downloader.aws.aws_report_downloader.boto3.resource')
    @patch('masu.external.downloader.aws.aws_report_downloader.AWSReportDownloader.download_file',
           return_value=('mock_file_name', None,))
    def test_download_bucket(self, mock_boto_resource, mock_download_file):
        """Test download bucket method."""
        mock_resource = Mock()
        mock_bucket = Mock()
        mock_bucket.objects.all.return_value = []
        mock_resource.Bucket.return_value = mock_bucket
        mock_boto_resource = mock_resource
        out = self.aws_report_downloader.download_bucket()
        expected_files = [] 
        self.assertEqual(out, expected_files)

    @patch('masu.external.downloader.aws.aws_report_downloader.AWSReportDownloader.download_file',
           side_effect=mock_download_file_error)
    def test_download_report_missing_manifest(self, mock_download_file):
        fake_report_date = self.fake.date_time().replace(day=1)
        out = self.report_downloader.download_report(fake_report_date)
        self.assertEqual(out, [])

    @patch('masu.external.report_downloader.ReportStatsDBAccessor')
    @patch('masu.util.aws.common.get_assume_role_session',
           return_value=FakeSessionDownloadError)
    def test_download_report_missing_bucket(self, mock_stats, fake_session):
        mock_stats.return_value.__enter__ = Mock()
        fake_report_date = self.fake.date_time().replace(day=1)
        fake_report_date_str = fake_report_date.strftime('%Y%m%dT000000.000Z')
        expected_assembly_id = '882083b7-ea62-4aab-aa6a-f0d08d65ee2b'
        input_key = f'/koku/20180701-20180801/{expected_assembly_id}/koku-1.csv.gz'
        mock_manifest = {
            'assemblyId': expected_assembly_id,
            'billingPeriod': {
                'start': fake_report_date_str
            },
            'reportKeys': [input_key]
        }
        with patch.object(AWSReportDownloader, '_get_manifest', return_value=mock_manifest):
            with self.assertRaises(AWSReportDownloaderError):
                report_downloader = ReportDownloader(self.fake_customer_name,
                                                     self.auth_credential,
                                                     self.fake_bucket_name,
                                                     'AWS',
                                                     2)
                AWSReportDownloader(**{'customer_name': self.fake_customer_name,
                                       'auth_credential': self.auth_credential,
                                       'bucket': self.fake_bucket_name,
                                       'report_name': self.fake_report_name,
                                       'provider_id': 2})
                report_downloader.download_report(fake_report_date)

    @patch('masu.util.aws.common.get_assume_role_session',
           return_value=FakeSession)
    def test_missing_report_name(self, fake_session):
        """Test downloading a report with an invalid report name."""
        auth_credential = fake_arn(service='iam', generate_account_id=True)

        with self.assertRaises(MasuProviderError):
            AWSReportDownloader(self.fake_customer_name,
                                auth_credential,
                                's3_bucket',
                                'wrongreport')

    @patch('masu.util.aws.common.get_assume_role_session',
           return_value=FakeSession)
    def test_download_default_report(self, fake_session):
        # actual test
        auth_credential = fake_arn(service='iam', generate_account_id=True)
        downloader = AWSReportDownloader(self.fake_customer_name,
                                         auth_credential,
                                         self.fake_bucket_name)
        self.assertEqual(downloader.report_name, self.fake_report_name)

    @patch('masu.util.aws.common.get_assume_role_session',
           return_value=FakeSessionNoReport)
    @patch('masu.util.aws.common.get_cur_report_definitions',
           return_value=[])
    def test_download_default_report_no_report_found(self, fake_session, fake_report_list):
        auth_credential = fake_arn(service='iam', generate_account_id=True)

        with self.assertRaises(MasuProviderError):
            AWSReportDownloader(self.fake_customer_name,
                                auth_credential,
                                self.fake_bucket_name)
