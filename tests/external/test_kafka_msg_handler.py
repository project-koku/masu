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

"""Test the Kafka msg handler."""

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from unittest.mock import patch
import mock
import os
import json
import tempfile
import shutil
import requests
from requests.exceptions import HTTPError
import requests_mock
from masu.config import Config
import masu.external.kafka_msg_handler as msg_handler
from tests import MasuTestCase


class KafkaMsg:
    def __init__(self, topic, url):
        self.topic = topic
        value_dict = {'url': url}
        value_str = json.dumps(value_dict)
        self.value = value_str.encode('utf-8')

class KafkaMsgHandlerTest(MasuTestCase):
    """Test Cases for the Kafka msg handler."""


    def setUp(self):
        payload_file = open('./tests/data/ocp/payload.tar.gz', 'rb')
        self.tarball_file = payload_file.read()
        payload_file.close()

        self.cluster_id = 'my-ocp-cluster-1'
        self.date_range = '20181001-20181101'

    def test_extract_payload(self):
        """Test to verify extracting payload is successful."""
        payload_url = 'http://insights-upload.com/quarnantine/file_to_validate'
        with requests_mock.mock() as m:
            m.get(payload_url, content=self.tarball_file)

            fake_dir = tempfile.mkdtemp()
            with patch.object(Config, 'INSIGHTS_LOCAL_REPORT_DIR', fake_dir):
                msg_handler.extract_payload(payload_url)
                expected_path = '{}/{}/{}/'.format(Config.INSIGHTS_LOCAL_REPORT_DIR,
                                                self.cluster_id,
                                                self.date_range)
                self.assertTrue(os.path.isdir(expected_path))
                shutil.rmtree(fake_dir)

    def test_extract_payload_bad_url(self):
        """Test to verify extracting payload exceptions are handled."""
        payload_url = 'http://insights-upload.com/quarnantine/file_to_validate'

        with requests_mock.mock() as m:
            m.get(payload_url, exc=HTTPError)

            with self.assertRaises(msg_handler.KafkaMsgHandlerError):
                msg_handler.extract_payload(payload_url)

    def test_extract_payload_unable_to_open(self):
        """Test to verify extracting payload exceptions are handled."""
        payload_url = 'http://insights-upload.com/quarnantine/file_to_validate'

        with requests_mock.mock() as m:
            m.get(payload_url, content=self.tarball_file)
            with mock.patch('masu.external.kafka_msg_handler.open') as mock_oserror:
                mock_oserror.side_effect = PermissionError
                with self.assertRaises(msg_handler.KafkaMsgHandlerError):
                    msg_handler.extract_payload(payload_url)

    def test_extract_payload_wrong_file_type(self):
        """Test to verify extracting payload is successful."""
        payload_url = 'http://insights-upload.com/quarnantine/file_to_validate'

        with requests_mock.mock() as m:
            payload_file = open('./tests/data/test_cur.csv', 'rb')
            csv_file = payload_file.read()
            payload_file.close()

            m.get(payload_url, content=csv_file)

            with self.assertRaises(msg_handler.KafkaMsgHandlerError):
                msg_handler.extract_payload(payload_url)

    def test_handle_messages(self):
        """Test to ensure that kafka messages are handled."""
        hccm_msg = KafkaMsg('hccm', 'http://insights-upload.com/quarnantine/file_to_validate')
        available_msg = KafkaMsg('available', 'http://insights-upload.com/quarnantine/file_to_validate')
        advisor_msg = KafkaMsg('advisor', 'http://insights-upload.com/quarnantine/file_to_validate')

        # Verify that when extract_payload is successful with 'hccm' message that SUCCESS_CONFIRM_STATUS is returned
        with patch('masu.external.kafka_msg_handler.extract_payload', return_value=None):
            self.assertEqual(msg_handler.handle_message(hccm_msg), msg_handler.SUCCESS_CONFIRM_STATUS)

        # Verify that when extract_payload is not successful with 'hccm' message that FAILURE_CONFIRM_STATUS is returned
        with patch('masu.external.kafka_msg_handler.extract_payload', side_effect=msg_handler.KafkaMsgHandlerError):
            self.assertEqual(msg_handler.handle_message(hccm_msg), msg_handler.FAILURE_CONFIRM_STATUS)

        # Verify that when None status is returned for non-hccm messages (we don't confirm these)
        self.assertEqual(msg_handler.handle_message(available_msg), None)
        self.assertEqual(msg_handler.handle_message(advisor_msg), None)
