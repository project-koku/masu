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

"""Test the NotificationHandler object."""

from unittest.mock import patch
import json
from masu.external.notification_handler import NotificationHandler, NotificationHandlerError
from tests import MasuTestCase


class NotificationHandlerTest(MasuTestCase):
    """Test Cases for the NotificationHandler object."""

    def test_initializer(self):
        """Test to initializer success."""
        headers = [('X-Amz-Sns-Message-Type', 'Notification'),
                   ('X-Amz-Sns-Message-Id', 'da41e39f-ea4d-435a-b922-c6aae3915ebe'),
                   ('X-Amz-Sns-Topic-Arn', 'arn:aws:sns:us-west-2:123456789012:MyTopic'),
                   ('X-Amz-Sns-Subscription-Arn', 'arn:aws:sns:us-west-2:123456789012:MyTopic:2bcfbf39-05c3-41de-beaa-fcfcc21c8f55'),
                   ('Content-Length', 761),
                   ('Content-Type', 'text/plain; charset=UTF-8'),
                   ('Host', 'ec2-50-17-44-49.compute-1.amazonaws.com'),
                   ('Connection', 'Keep-Alive'),
                   ('User-Agent', 'Amazon Simple Notification Service Agent')]

        body_dict = {"Type" : "Notification",
                     "MessageId" : "869ace9b-691a-5148-a22c-9d2e1e46e3de",
                     "TopicArn" : "arn:aws:sns:us-east-1:589179999999:CostUsageNotificationDemo",
                     "Subject" : "Amazon S3 Notification",
                     "Message" : "{\"Records\":[{\"eventVersion\":\"2.0\",\"eventSource\":\"aws:s3\",\"awsRegion\":\"us-east-1\",\"eventTime\":\"2018-07-03T13:07:40.841Z\",\"eventName\":\"ObjectCreated:Put\",\"userIdentity\":{\"principalId\":\"AWS:AIDAI277OR7TSQEWOQ6SU\"},\"requestParameters\":{\"sourceIPAddress\":\"107.15.167.104\"},\"responseElements\":{\"x-amz-request-id\":\"480DC7730E2843BC\",\"x-amz-id-2\":\"FLaf0a25Q+XMAWgZ+PcF/vX0qjTxQLI8NVO1sFUn9FmO9o6RnHaASueXjzYSxk+pS96+3rjr+Rc=\"},\"s3\":{\"s3SchemaVersion\":\"1.0\",\"configurationId\":\"CURUpdateEvent\",\"bucket\":{\"name\":\"bucket-sns-test\",\"ownerIdentity\":{\"principalId\":\"A2V75OLLZ1ABF7\"},\"arn\":\"arn:aws:s3:::bucket-sns-test\"},\"object\":{\"key\":\"/cur/20180701-20180801/58d25daa-bcb7-4d6c-87cb-6d1f719428ef/cur-Manifest.json\",\"size\":4799,\"eTag\":\"dbd34ba7d518a7a28d34fb05d0e4261f\",\"sequencer\":\"005B3B751CC1E30AA9\"}}}]}",
                     "Timestamp" : "2018-07-03T13:07:40.924Z",
                     "SignatureVersion" : "1",
                     "Signature" : "VOHSWykhwa3UJ9o0QpZHQm6VyxYXF2SMypzQW4DT7GveCrByef02+Xb/j+Fjh2D7kAyFgwq30l2HJc1W048GJ26Xju+x5YRt2KciU88Rra/L97HZmT3lUO3CBWv72nc157QgE1pazuHymjvB4ARaw8Ga1QW4brYBKeyjSL3q8RMXpELnapCc0OzWZ7/tn0sYNbEnro7ZVOAo2NdUgBrNedV/Cu6zjJ2o3k+bYvH9sHN9qI8hGteSg2nshBugTg/7873QbeN5LMaUljTEDnIBaIKdxRLdlj3Q2N0KlFHyMsu4TumqBY2xzEoCa5k5hx7J5F1nerZb0BikwGNGOHkDvA==",
                     "SigningCertURL" : "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-eaea6120e66ea12e88dcd8bcbddca752.pem",
                     "UnsubscribeURL" : "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:589179999999:CostUsageNotificationDemo:3affeac1-5249-49a0-876d-a163fb53a004"}
        body = json.dumps(body_dict)

        handler = NotificationHandler(headers, body)
        self.assertIsNotNone(handler._handler)

    def test_initializer_error_setting_handler(self):
        """Test to initializer error setting handler."""
        # Use invalid type
        headers = [('X-Amz-Sns-Message-Type', 'InvalidType'),
                   ('X-Amz-Sns-Message-Id', 'da41e39f-ea4d-435a-b922-c6aae3915ebe'),
                   ('X-Amz-Sns-Topic-Arn', 'arn:aws:sns:us-west-2:123456789012:MyTopic'),
                   ('X-Amz-Sns-Subscription-Arn', 'arn:aws:sns:us-west-2:123456789012:MyTopic:2bcfbf39-05c3-41de-beaa-fcfcc21c8f55'),
                   ('Content-Length', 761),
                   ('Content-Type', 'text/plain; charset=UTF-8'),
                   ('Host', 'ec2-50-17-44-49.compute-1.amazonaws.com'),
                   ('Connection', 'Keep-Alive'),
                   ('User-Agent', 'Amazon Simple Notification Service Agent')]

        body_dict = {"Type" : "InvalidType",
                     "MessageId" : "869ace9b-691a-5148-a22c-9d2e1e46e3de",
                     "TopicArn" : "arn:aws:sns:us-east-1:589179999999:CostUsageNotificationDemo",
                     "Subject" : "Amazon S3 Notification",
                     "Message" : "{\"Records\":[{\"eventVersion\":\"2.0\",\"eventSource\":\"aws:s3\",\"awsRegion\":\"us-east-1\",\"eventTime\":\"2018-07-03T13:07:40.841Z\",\"eventName\":\"ObjectCreated:Put\",\"userIdentity\":{\"principalId\":\"AWS:AIDAI277OR7TSQEWOQ6SU\"},\"requestParameters\":{\"sourceIPAddress\":\"107.15.167.104\"},\"responseElements\":{\"x-amz-request-id\":\"480DC7730E2843BC\",\"x-amz-id-2\":\"FLaf0a25Q+XMAWgZ+PcF/vX0qjTxQLI8NVO1sFUn9FmO9o6RnHaASueXjzYSxk+pS96+3rjr+Rc=\"},\"s3\":{\"s3SchemaVersion\":\"1.0\",\"configurationId\":\"CURUpdateEvent\",\"bucket\":{\"name\":\"bucket-sns-test\",\"ownerIdentity\":{\"principalId\":\"A2V75OLLZ1ABF7\"},\"arn\":\"arn:aws:s3:::bucket-sns-test\"},\"object\":{\"key\":\"/cur/20180701-20180801/58d25daa-bcb7-4d6c-87cb-6d1f719428ef/cur-Manifest.json\",\"size\":4799,\"eTag\":\"dbd34ba7d518a7a28d34fb05d0e4261f\",\"sequencer\":\"005B3B751CC1E30AA9\"}}}]}",
                     "Timestamp" : "2018-07-03T13:07:40.924Z",
                     "SignatureVersion" : "1",
                     "Signature" : "VOHSWykhwa3UJ9o0QpZHQm6VyxYXF2SMypzQW4DT7GveCrByef02+Xb/j+Fjh2D7kAyFgwq30l2HJc1W048GJ26Xju+x5YRt2KciU88Rra/L97HZmT3lUO3CBWv72nc157QgE1pazuHymjvB4ARaw8Ga1QW4brYBKeyjSL3q8RMXpELnapCc0OzWZ7/tn0sYNbEnro7ZVOAo2NdUgBrNedV/Cu6zjJ2o3k+bYvH9sHN9qI8hGteSg2nshBugTg/7873QbeN5LMaUljTEDnIBaIKdxRLdlj3Q2N0KlFHyMsu4TumqBY2xzEoCa5k5hx7J5F1nerZb0BikwGNGOHkDvA==",
                     "SigningCertURL" : "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-eaea6120e66ea12e88dcd8bcbddca752.pem",
                     "UnsubscribeURL" : "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:589179999999:CostUsageNotificationDemo:3affeac1-5249-49a0-876d-a163fb53a004"}
        body = json.dumps(body_dict)

        with self.assertRaises(NotificationHandlerError) as error:
            NotificationHandler(headers, body)
        self.assertTrue('Unexpected message type' in str(error.exception))

    def test_initializer_unsupported_provider(self):
        """Test to initializer unknown provider."""
        headers = [('X-Wizz-Bang-Message-Type', 'Notification'),
                   ('Content-Length', 761),
                   ('Content-Type', 'text/plain; charset=UTF-8'),
                   ('Connection', 'Keep-Alive'),
                   ('User-Agent', 'Amazon Simple Notification Service Agent')]

        body_dict = {"Type" : "Notification",
                     "MessageId" : "869ace9b-691a-5148-a22c-9d2e1e46e3de",
                     "Subject" : "Wizz Bang Notification",
                     "Timestamp" : "2018-07-03T13:07:40.924Z"}
        body = json.dumps(body_dict)

        with self.assertRaises(NotificationHandlerError) as error:
            NotificationHandler(headers, body)
        self.assertTrue('Unsupported cloud provider.' in str(error.exception))

    def test_billing_source_exception(self):
        """Test to initializer success."""
        headers = [('X-Amz-Sns-Message-Type', 'Notification'),
                   ('X-Amz-Sns-Message-Id', 'da41e39f-ea4d-435a-b922-c6aae3915ebe'),
                   ('X-Amz-Sns-Topic-Arn', 'arn:aws:sns:us-west-2:123456789012:MyTopic'),
                   ('X-Amz-Sns-Subscription-Arn', 'arn:aws:sns:us-west-2:123456789012:MyTopic:2bcfbf39-05c3-41de-beaa-fcfcc21c8f55'),
                   ('Content-Length', 761),
                   ('Content-Type', 'text/plain; charset=UTF-8'),
                   ('Host', 'ec2-50-17-44-49.compute-1.amazonaws.com'),
                   ('Connection', 'Keep-Alive'),
                   ('User-Agent', 'Amazon Simple Notification Service Agent')]

        body_dict = {"Type" : "Notification",
                     "MessageId" : "869ace9b-691a-5148-a22c-9d2e1e46e3de",
                     "TopicArn" : "arn:aws:sns:us-east-1:589179999999:CostUsageNotificationDemo",
                     "Subject" : "Amazon S3 Notification",
                     "Message" : "{\"Records\":[{\"extra\": \"message\"}, {\"eventVersion\":\"2.0\",\"eventSource\":\"aws:s3\",\"awsRegion\":\"us-east-1\",\"eventTime\":\"2018-07-04T18:04:41.786Z\",\"eventName\":\"ObjectCreated:Put\",\"userIdentity\":{\"principalId\":\"AWS:AIDAJLSI7DTYBUZAOKHVM\"},\"requestParameters\":{\"sourceIPAddress\":\"10.88.30.162\"},\"responseElements\":{\"x-amz-request-id\":\"DBC59DCBEE8AB006\",\"x-amz-id-2\":\"4MUgFYLBTnbinBcBSax8FIykKKvLinL6IBZYYGNt0267L7/WixNzuupAM1OtpMmua+DoV/guVYU=\"},\"s3\":{\"s3SchemaVersion\":\"1.0\",\"configurationId\":\"CostUsageNotification\",\"bucket\":{\"name\":\"cost-usage-bucket\",\"ownerIdentity\":{\"principalId\":\"A2V75OLLZ1ABF7\"},\"arn\":\"arn:aws:s3:::cost-usage-bucket\"},\"object\":{\"key\":\"/koku/20180701-20180801/koku-Manifest.json\",\"size\":6518,\"eTag\":\"963195a6fa85a9b98a1f93a981a805fd\",\"sequencer\":\"005B3D0C39C106E6AC\"}}}]}",
                     "Timestamp" : "2018-07-03T13:07:40.924Z",
                     "SignatureVersion" : "1",
                     "Signature" : "VOHSWykhwa3UJ9o0QpZHQm6VyxYXF2SMypzQW4DT7GveCrByef02+Xb/j+Fjh2D7kAyFgwq30l2HJc1W048GJ26Xju+x5YRt2KciU88Rra/L97HZmT3lUO3CBWv72nc157QgE1pazuHymjvB4ARaw8Ga1QW4brYBKeyjSL3q8RMXpELnapCc0OzWZ7/tn0sYNbEnro7ZVOAo2NdUgBrNedV/Cu6zjJ2o3k+bYvH9sHN9qI8hGteSg2nshBugTg/7873QbeN5LMaUljTEDnIBaIKdxRLdlj3Q2N0KlFHyMsu4TumqBY2xzEoCa5k5hx7J5F1nerZb0BikwGNGOHkDvA==",
                     "SigningCertURL" : "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-eaea6120e66ea12e88dcd8bcbddca752.pem",
                     "UnsubscribeURL" : "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:589179999999:CostUsageNotificationDemo:3affeac1-5249-49a0-876d-a163fb53a004"}
        body = json.dumps(body_dict)

        handler = NotificationHandler(headers, body)
        with self.assertRaises(NotificationHandlerError):
            handler = NotificationHandler(headers, body)
            handler.billing_source()
