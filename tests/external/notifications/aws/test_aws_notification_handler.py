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
"""Test the AWS notifiation (SNS) handler."""

import boto3
from moto import mock_sns
from unittest.mock import patch
import json
from masu.external.notifications.aws.aws_notification_handler import AWSNotificationHandler, AWSNotificationHandlerError
from masu.external.notifications.notification_interface import NotificationInterfaceFilter

from tests import MasuTestCase

class AWSNotificationHandlerTest(MasuTestCase):
    """Test Cases for AWSNotificationHandler."""

    @mock_sns
    def test_confirm_subscription(self):
        # Setup
        conn = boto3.client('sns', region_name='us-east-1')
        response = conn.create_topic(Name='CostUsageNotificationDemo')
        headers = [('X-Amz-Sns-Message-Type', 'SubscriptionConfirmation'),
                   ('X-Amz-Sns-Message-Id', '010b7c42-3f24-4865-83b1-13120d79466b'),
                   ('X-Amz-Sns-Subscription-Arn', 'arn:aws:sns:us-east-1:123456789012:MyTopic:2bcfbf39-05c3-41de-beaa-fcfcc21c8f55'),
                   ('Content-Length', 1637),
                   ('Content-Type', 'text/plain; charset=UTF-8'),
                   ('Host', 'masu.net:6868'),
                   ('Connection', 'Keep-Alive'),
                   ('User-Agent', 'Amazon Simple Notification Service Agent'),
                   ('Accept-Encoding', 'gzip,deflate')]
        headers.append(('X-Amz-Sns-Topic-Arn', response['TopicArn']))

        body_dict = {"Type" : "SubscriptionConfirmation",
                     "MessageId" : "010b7c42-3f24-4865-83b1-13120d79466b",
                     "Token" : "2336412f37fb687f5d51e6e241da92fd72d769c811cb257f2ca8bbb9e329dd2eb427b0935ce7fe84f91e14e5994d2d9039b3aade5b4f16dd5ab3979b05751962ceed2c7e193e7b7797630c31eec29477949064522feb104a311b44e1268ba7bdfdc06d7e6f39174dbb69326a379d06cbbc96adcdc24939e36892e024aa0e96d2",
                     "TopicArn" : response['TopicArn'],
                     "Message" : "You have chosen to subscribe to the topic arn:aws:sns:us-east-1:589179999999:CostUsageNotificationDemo.\nTo confirm the subscriptionDataBuilder, visit the SubscribeURL included in this message.",
                     "SubscribeURL" : "https://sns.us-east-1.amazonaws.com/?Action=ConfirmSubscription&TopicArn=arn:aws:sns:us-east-1:589179999999:CostUsageNotificationDemo&Token=2336412f37fb687f5d51e6e241da92fd72d769c811cb257f2ca8bbb9e329dd2eb427b0935ce7fe84f91e14e5994d2d9039b3aade5b4f16dd5ab3979b05751962ceed2c7e193e7b7797630c31eec29477949064522feb104a311b44e1268ba7bdfdc06d7e6f39174dbb69326a379d06cbbc96adcdc24939e36892e024aa0e96d2",
                     "Timestamp" : "2018-07-05T12:29:27.641Z",
                     "SignatureVersion" : "1",
                     "Signature" : "L8VmRMT55sv326Rt1HBawA8hPKR0plaBfvI8hlZNm2nhaMkVzvFkvKiMZucfQ7bYWaYqVF+xzvqkaRnMw8/uC4QcrM5DK5HcXYfAJCeI8t32jTg3Kcdn3SGBiyxcBWYt8qSXL7403ho4vIVpCHRuX6K2ZydS7sxx6umr/nanaOUGnkDeC91GFoUMslNw7yITc0YunPwg8GcvKgLhsQr2d7C5I3zDprA+Ds29voLN6v66hH0uR0LEfDq9Ky0Dgii4UebYUgKBCWSy5ETsRHqug5tPNzv9afexjdXrjEUYbvYZO+RRDPztwGjyHw6CL35B85FLZ7UDPLeRysZq47gb+Q==",
                     "SigningCertURL" : "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-eaea6120e66ea12e88dcd8bcbddca752.pem"}
        body = json.dumps(body_dict)
        try:
            AWSNotificationHandler(headers, body, validation=False)
        except Exception:
            self.fail('Unexpected exception')

    @mock_sns
    def test_confirm_subscription_not_successful(self):
        # Setup
        conn = boto3.client('sns', region_name='us-east-1')
        response = conn.create_topic(Name='CostUsageNotificationDemo')
        corrupted_arn_name = 'Mangle{}'.format(response['TopicArn'])
        headers = [('X-Amz-Sns-Message-Type', 'SubscriptionConfirmation'),
                   ('X-Amz-Sns-Message-Id', '010b7c42-3f24-4865-83b1-13120d79466b'),
                   ('X-Amz-Sns-Subscription-Arn', 'arn:aws:sns:us-east-1:123456789012:MyTopic:2bcfbf39-05c3-41de-beaa-fcfcc21c8f55'),
                   ('Content-Length', 1637),
                   ('Content-Type', 'text/plain; charset=UTF-8'),
                   ('Host', 'masu.net:6868'),
                   ('Connection', 'Keep-Alive'),
                   ('User-Agent', 'Amazon Simple Notification Service Agent'),
                   ('Accept-Encoding', 'gzip,deflate')]
        headers.append(('X-Amz-Sns-Topic-Arn', corrupted_arn_name))

        body_dict = {"Type" : "SubscriptionConfirmation",
                     "MessageId" : "010b7c42-3f24-4865-83b1-13120d79466b",
                     "Token" : "2336412f37fb687f5d51e6e241da92fd72d769c811cb257f2ca8bbb9e329dd2eb427b0935ce7fe84f91e14e5994d2d9039b3aade5b4f16dd5ab3979b05751962ceed2c7e193e7b7797630c31eec29477949064522feb104a311b44e1268ba7bdfdc06d7e6f39174dbb69326a379d06cbbc96adcdc24939e36892e024aa0e96d2",
                     "TopicArn" : corrupted_arn_name,
                     "Message" : "You have chosen to subscribe to the topic arn:aws:sns:us-east-1:589179999999:CostUsageNotificationDemo.\nTo confirm the subscriptionDataBuilder, visit the SubscribeURL included in this message.",
                     "SubscribeURL" : "https://sns.us-east-1.amazonaws.com/?Action=ConfirmSubscription&TopicArn=arn:aws:sns:us-east-1:589179999999:CostUsageNotificationDemo&Token=2336412f37fb687f5d51e6e241da92fd72d769c811cb257f2ca8bbb9e329dd2eb427b0935ce7fe84f91e14e5994d2d9039b3aade5b4f16dd5ab3979b05751962ceed2c7e193e7b7797630c31eec29477949064522feb104a311b44e1268ba7bdfdc06d7e6f39174dbb69326a379d06cbbc96adcdc24939e36892e024aa0e96d2",
                     "Timestamp" : "2018-07-05T12:29:27.641Z",
                     "SignatureVersion" : "1",
                     "Signature" : "L8VmRMT55sv326Rt1HBawA8hPKR0plaBfvI8hlZNm2nhaMkVzvFkvKiMZucfQ7bYWaYqVF+xzvqkaRnMw8/uC4QcrM5DK5HcXYfAJCeI8t32jTg3Kcdn3SGBiyxcBWYt8qSXL7403ho4vIVpCHRuX6K2ZydS7sxx6umr/nanaOUGnkDeC91GFoUMslNw7yITc0YunPwg8GcvKgLhsQr2d7C5I3zDprA+Ds29voLN6v66hH0uR0LEfDq9Ky0Dgii4UebYUgKBCWSy5ETsRHqug5tPNzv9afexjdXrjEUYbvYZO+RRDPztwGjyHw6CL35B85FLZ7UDPLeRysZq47gb+Q==",
                     "SigningCertURL" : "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-eaea6120e66ea12e88dcd8bcbddca752.pem"}
        body = json.dumps(body_dict)
        with self.assertRaises(AWSNotificationHandlerError):
            AWSNotificationHandler(headers, body, validation=False)

    def test_get_billing_source_non_top_level_manifest(self):
        headers = [('X-Amz-Sns-Message-Type', 'Notification'),
                   ('X-Amz-Sns-Message-Id', 'da41e39f-ea4d-435a-b922-c6aae3915ebe'),
                   ('X-Amz-Sns-Topic-Arn', 'arn:aws:sns:us-east-1:123456789012:MyTopic'),
                   ('X-Amz-Sns-Subscription-Arn', 'arn:aws:sns:us-east-1:123456789012:MyTopic:2bcfbf39-05c3-41de-beaa-fcfcc21c8f55'),
                   ('Content-Length', 761),
                   ('Content-Type', 'text/plain; charset=UTF-8'),
                   ('Host', 'ec2-50-17-44-49.compute-1.amazonaws.com'),
                   ('Connection', 'Keep-Alive'),
                   ('User-Agent', 'Amazon Simple Notification Service Agent')]

        body_dict = {"Type" : "Notification",
                     "MessageId" : "869ace9b-691a-5148-a22c-9d2e1e46e3de",
                     "TopicArn" : "arn:aws:sns:us-east-1:589179999999:CostUsageNotificationDemo",
                     "Subject" : "Amazon S3 Notification",
                     "Message" : "{\"Records\":[{\"eventVersion\":\"2.0\",\"eventSource\":\"aws:s3\",\"awsRegion\":\"us-east-1\",\"eventTime\":\"2018-07-03T13:07:40.841Z\",\"eventName\":\"ObjectCreated:Put\",\"userIdentity\":{\"principalId\":\"AWS:AIDAI277OR7TSQEWOQ6SU\"},\"requestParameters\":{\"sourceIPAddress\":\"107.15.167.104\"},\"responseElements\":{\"x-amz-request-id\":\"480DC7730E2843BC\",\"x-amz-id-2\":\"FLaf0a25Q+XMAWgZ+PcF/vX0qjTxQLI8NVO1sFUn9FmO9o6RnHaASueXjzYSxk+pS96+3rjr+Rc=\"},\"s3\":{\"s3SchemaVersion\":\"1.0\",\"configurationId\":\"CURUpdateEvent\",\"bucket\":{\"name\":\"bucket-sns-test\",\"ownerIdentity\":{\"principalId\":\"A2V75OLLZ1ABF7\"},\"arn\":\"arn:aws:s3:::bucket-sns-test\"},\"object\":{\"key\":\"/cur/20180701-20180801/58d25dAA-bcb7-4d6C-87CB-6d1f719428EF/cur-Manifest.json\",\"size\":4799,\"eTag\":\"dbd34ba7d518a7a28d34fb05d0e4261f\",\"sequencer\":\"005B3B751CC1E30AA9\"}}}]}",
                     "Timestamp" : "2018-07-03T13:07:40.924Z",
                     "SignatureVersion" : "1",
                     "Signature" : "VOHSWykhwa3UJ9o0QpZHQm6VyxYXF2SMypzQW4DT7GveCrByef02+Xb/j+Fjh2D7kAyFgwq30l2HJc1W048GJ26Xju+x5YRt2KciU88Rra/L97HZmT3lUO3CBWv72nc157QgE1pazuHymjvB4ARaw8Ga1QW4brYBKeyjSL3q8RMXpELnapCc0OzWZ7/tn0sYNbEnro7ZVOAo2NdUgBrNedV/Cu6zjJ2o3k+bYvH9sHN9qI8hGteSg2nshBugTg/7873QbeN5LMaUljTEDnIBaIKdxRLdlj3Q2N0KlFHyMsu4TumqBY2xzEoCa5k5hx7J5F1nerZb0BikwGNGOHkDvA==",
                     "SigningCertURL" : "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-eaea6120e66ea12e88dcd8bcbddca752.pem",
                     "UnsubscribeURL" : "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:589179999999:CostUsageNotificationDemo:3affeac1-5249-49a0-876d-a163fb53a004"}
        body = json.dumps(body_dict)
        handler = AWSNotificationHandler(headers, body)
        with self.assertRaises(NotificationInterfaceFilter):
            handler.get_billing_source()

    def test_get_billing_source_top_level_manifest(self):
        headers = [('X-Amz-Sns-Message-Type', 'Notification'),
                   ('X-Amz-Sns-Message-Id', 'da41e39f-ea4d-435a-b922-c6aae3915ebe'),
                   ('X-Amz-Sns-Topic-Arn', 'arn:aws:sns:us-east-1:123456789012:MyTopic'),
                   ('X-Amz-Sns-Subscription-Arn', 'arn:aws:sns:us-east-1:123456789012:MyTopic:2bcfbf39-05c3-41de-beaa-fcfcc21c8f55'),
                   ('Content-Length', 761),
                   ('Content-Type', 'text/plain; charset=UTF-8'),
                   ('Host', 'ec2-50-17-44-49.compute-1.amazonaws.com'),
                   ('Connection', 'Keep-Alive'),
                   ('User-Agent', 'Amazon Simple Notification Service Agent')]

        body_dict = {"Type" : "Notification",
                     "MessageId" : "879e9da4-a9ca-5eec-a13b-ce13a7b32b43",
                     "TopicArn" : "arn:aws:sns:us-east-1:589179999999:CostUsageReportUpdateTopic",
                     "Subject" : "Amazon S3 Notification",
                     "Message" : "{\"Records\":[{\"eventVersion\":\"2.0\",\"eventSource\":\"aws:s3\",\"awsRegion\":\"us-east-1\",\"eventTime\":\"2018-07-04T18:04:41.786Z\",\"eventName\":\"ObjectCreated:Put\",\"userIdentity\":{\"principalId\":\"AWS:AIDAJLSI7DTYBUZAOKHVM\"},\"requestParameters\":{\"sourceIPAddress\":\"10.88.30.162\"},\"responseElements\":{\"x-amz-request-id\":\"DBC59DCBEE8AB006\",\"x-amz-id-2\":\"4MUgFYLBTnbinBcBSax8FIykKKvLinL6IBZYYGNt0267L7/WixNzuupAM1OtpMmua+DoV/guVYU=\"},\"s3\":{\"s3SchemaVersion\":\"1.0\",\"configurationId\":\"CostUsageNotification\",\"bucket\":{\"name\":\"cost-usage-bucket\",\"ownerIdentity\":{\"principalId\":\"A2V75OLLZ1ABF7\"},\"arn\":\"arn:aws:s3:::cost-usage-bucket\"},\"object\":{\"key\":\"/koku/20180701-20180801/koku-Manifest.json\",\"size\":6518,\"eTag\":\"963195a6fa85a9b98a1f93a981a805fd\",\"sequencer\":\"005B3D0C39C106E6AC\"}}}]}",
                     "Timestamp" : "2018-07-04T18:04:41.820Z",
                     "SignatureVersion" : "1",
                     "Signature" : "mDniwbH0VTvDtm4VaZf66Ox3joxBv92lJb4KXEqq1AeVKTfpyCuB5XROU7iw4v2AD97DPr/C9tHIOuuMaDANJxVLor7TfJB7xCA9PYg3963NqCE1uvl5fv7NYhCpl4bhGwKwKBIYvOvWbVxcAQilRWZHDmLAqEmWfzCIPtACWc9xAt0rbL2Zk0TqAhU87QU3dAX63bV6HdNOHMCp1xS5bNVWWWJ09vsUNwSVS4zQ/bAxymffoAMyIEBKlCU8le4khjGlmSIX6S6vsl0rVd9e8hInSmAHN4mcBE7SUz/TrlmwwejP6ysEdHRnHfU41/axMxBZyfH654A2Kne6Vs01mg==",
                     "SigningCertURL" : "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-eaea6120e66ea12e88dcd8bcbddca752.pem",
                     "UnsubscribeURL" : "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:589179999999:CostUsageReportUpdateTopic:7d549a1b-502f-47f7-9469-9ed18671e76a"}
        body = json.dumps(body_dict)
        handler = AWSNotificationHandler(headers, body)
        s3_bucket = handler.get_billing_source()
        self.assertEqual(s3_bucket, 'cost-usage-bucket')

    def test_get_billing_source_non_manifest_file(self):
        headers = [('X-Amz-Sns-Message-Type', 'Notification'),
                   ('X-Amz-Sns-Message-Id', 'da41e39f-ea4d-435a-b922-c6aae3915ebe'),
                   ('X-Amz-Sns-Topic-Arn', 'arn:aws:sns:us-east-1:123456789012:MyTopic'),
                   ('X-Amz-Sns-Subscription-Arn', 'arn:aws:sns:us-east-1:123456789012:MyTopic:2bcfbf39-05c3-41de-beaa-fcfcc21c8f55'),
                   ('Content-Length', 761),
                   ('Content-Type', 'text/plain; charset=UTF-8'),
                   ('Host', 'ec2-50-17-44-49.compute-1.amazonaws.com'),
                   ('Connection', 'Keep-Alive'),
                   ('User-Agent', 'Amazon Simple Notification Service Agent')]

        body_dict = {"Type" : "Notification",
                     "MessageId" : "4d9d04a3-113f-5532-8352-57141f47f5c4",
                     "TopicArn" : "arn:aws:sns:us-east-1:589179999999:CostUsageReportUpdateTopic",
                     "Subject" : "Amazon S3 Notification",
                     "Message" : "{\"Records\":[{\"eventVersion\":\"2.0\",\"eventSource\":\"aws:s3\",\"awsRegion\":\"us-east-1\",\"eventTime\":\"2018-07-04T18:04:39.895Z\",\"eventName\":\"ObjectCreated:Put\",\"userIdentity\":{\"principalId\":\"AWS:AIDAJLSI7DTYBUZAOKHVM\"},\"requestParameters\":{\"sourceIPAddress\":\"10.85.145.33\"},\"responseElements\":{\"x-amz-request-id\":\"82DD93AB926CD233\",\"x-amz-id-2\":\"gdJjPizP/oLKRROOFBUDxgxanwSM9f6PQyvzP0MaJlhBZ9LCB+7sj6z70GIuAoKT5zfx4soso4U=\"},\"s3\":{\"s3SchemaVersion\":\"1.0\",\"configurationId\":\"CostUsageNotification\",\"bucket\":{\"name\":\"cost-usage-bucket\",\"ownerIdentity\":{\"principalId\":\"A2V75OLLZ1ABF7\"},\"arn\":\"arn:aws:s3:::cost-usage-bucket\"},\"object\":{\"key\":\"/koku/20180701-20180801/bb976103-7c20-4053-852c-ad0c4b778dd0/koku-1.csv.gz\",\"size\":53641,\"eTag\":\"57b759ec6f3bf98bafa3991f5b9bac15\",\"sequencer\":\"005B3D0C37CE41DED4\"}}}]}",
                     "Timestamp" : "2018-07-04T18:04:40.036Z",
                     "SignatureVersion" : "1",
                     "Signature" : "gMXR9TvaiZjpuslyjnfj9PdOyOg78qqrz4pyt7Ct7i+EWkNbo1ePKoszJv2Wx0k7joX+irfLiCiROt8lr3TuVEA9ht/lG1hQAUW6T+BAikB6IF5c9uR1PtiP+Kn+qG9FyDbtSdr3Qn0i3PwI9vOIrqXNf5aEm1mJKqdwdWvkQ+pYHr1RYn4a5T6rrUuRicfzhD6qlbq8jfgzhHPLUcn4wQZ9Sdq7buuY8I3jCo/p+CGhkg70HaF64dyuzSZQU7DEaumBuMvasTI50w3PgymF4CM3wBGrzqEc+FFoEAgUjJTO2ri//KfBzhMhUkxhkIzzh5rGgrHfVGpV7gyFJ9vGWw==",
                     "SigningCertURL" : "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-eaea6120e66ea12e88dcd8bcbddca752.pem",
                     "UnsubscribeURL" : "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:589179999999:CostUsageReportUpdateTopic:7d549a1b-502f-47f7-9469-9ed18671e76a"}
        body = json.dumps(body_dict)
        handler = AWSNotificationHandler(headers, body)
        with self.assertRaises(NotificationInterfaceFilter):
            handler.get_billing_source()

    def test_get_billing_source_empty_body(self):
        headers = [('X-Amz-Sns-Message-Type', 'Notification')]
        body = u''
        handler = AWSNotificationHandler(headers, body)
        s3_bucket_name = handler.get_billing_source()
        self.assertEqual(s3_bucket_name, None)

    def test_get_billing_source_wrong_message_type(self):
        headers = [('X-Amz-Sns-Message-Type', 'RandomType')]
        body = u''
        with self.assertRaises(AWSNotificationHandlerError):
            AWSNotificationHandler(headers, body)

    def test_get_billing_source_unexpected_message_format(self):
        headers = [('X-Amz-Sns-Message-Type', 'Notification'),
                   ('X-Amz-Sns-Message-Id', 'da41e39f-ea4d-435a-b922-c6aae3915ebe'),
                   ('X-Amz-Sns-Topic-Arn', 'arn:aws:sns:us-east-1:123456789012:MyTopic'),
                   ('X-Amz-Sns-Subscription-Arn', 'arn:aws:sns:us-east-1:123456789012:MyTopic:2bcfbf39-05c3-41de-beaa-fcfcc21c8f55'),
                   ('Content-Length', 761),
                   ('Content-Type', 'text/plain; charset=UTF-8'),
                   ('Host', 'ec2-50-17-44-49.compute-1.amazonaws.com'),
                   ('Connection', 'Keep-Alive'),
                   ('User-Agent', 'Amazon Simple Notification Service Agent')]

        body_dict = {"Type" : "Notification",
                     "MessageId" : "879e9da4-a9ca-5eec-a13b-ce13a7b32b43",
                     "TopicArn" : "arn:aws:sns:us-east-1:589179999999:CostUsageReportUpdateTopic",
                     "Subject" : "Amazon S3 Notification",
                     "Message" : "{\"Records\":[{\"extra\": \"message\"}, {\"eventVersion\":\"2.0\",\"eventSource\":\"aws:s3\",\"awsRegion\":\"us-east-1\",\"eventTime\":\"2018-07-04T18:04:41.786Z\",\"eventName\":\"ObjectCreated:Put\",\"userIdentity\":{\"principalId\":\"AWS:AIDAJLSI7DTYBUZAOKHVM\"},\"requestParameters\":{\"sourceIPAddress\":\"10.88.30.162\"},\"responseElements\":{\"x-amz-request-id\":\"DBC59DCBEE8AB006\",\"x-amz-id-2\":\"4MUgFYLBTnbinBcBSax8FIykKKvLinL6IBZYYGNt0267L7/WixNzuupAM1OtpMmua+DoV/guVYU=\"},\"s3\":{\"s3SchemaVersion\":\"1.0\",\"configurationId\":\"CostUsageNotification\",\"bucket\":{\"name\":\"cost-usage-bucket\",\"ownerIdentity\":{\"principalId\":\"A2V75OLLZ1ABF7\"},\"arn\":\"arn:aws:s3:::cost-usage-bucket\"},\"object\":{\"key\":\"/koku/20180701-20180801/koku-Manifest.json\",\"size\":6518,\"eTag\":\"963195a6fa85a9b98a1f93a981a805fd\",\"sequencer\":\"005B3D0C39C106E6AC\"}}}]}",
                     "Timestamp" : "2018-07-04T18:04:41.820Z",
                     "SignatureVersion" : "1",
                     "Signature" : "mDniwbH0VTvDtm4VaZf66Ox3joxBv92lJb4KXEqq1AeVKTfpyCuB5XROU7iw4v2AD97DPr/C9tHIOuuMaDANJxVLor7TfJB7xCA9PYg3963NqCE1uvl5fv7NYhCpl4bhGwKwKBIYvOvWbVxcAQilRWZHDmLAqEmWfzCIPtACWc9xAt0rbL2Zk0TqAhU87QU3dAX63bV6HdNOHMCp1xS5bNVWWWJ09vsUNwSVS4zQ/bAxymffoAMyIEBKlCU8le4khjGlmSIX6S6vsl0rVd9e8hInSmAHN4mcBE7SUz/TrlmwwejP6ysEdHRnHfU41/axMxBZyfH654A2Kne6Vs01mg==",
                     "SigningCertURL" : "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-eaea6120e66ea12e88dcd8bcbddca752.pem",
                     "UnsubscribeURL" : "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:589179999999:CostUsageReportUpdateTopic:7d549a1b-502f-47f7-9469-9ed18671e76a"}
        body = json.dumps(body_dict)

        handler = AWSNotificationHandler(headers, body)
        with self.assertRaises(AWSNotificationHandlerError):
            handler = AWSNotificationHandler(headers, body, validation=False)
            handler.get_billing_source()

    def test_missing_message_type(self):
        headers = [('X-Amz-Sns-Topic-Arn', 'arn:aws:sns:us-east-1:589173575009:CostUsageNotificationDemo'),
                   ('X-Amz-Sns-Message-Id', '010b7c42-3f24-4865-83b1-13120d79466b'),
                   ('X-Amz-Sns-Subscription-Arn', 'arn:aws:sns:us-east-1:123456789012:MyTopic:2bcfbf39-05c3-41de-beaa-fcfcc21c8f55'),
                   ('Content-Length', 1637),
                   ('Content-Type', 'text/plain; charset=UTF-8'),
                   ('Host', 'masu.net:6868'),
                   ('Connection', 'Keep-Alive'),
                   ('User-Agent', 'Amazon Simple Notification Service Agent'),
                   ('Accept-Encoding', 'gzip,deflate')]

        body_dict = {"Type" : "SubscriptionConfirmation",
                     "MessageId" : "010b7c42-3f24-4865-83b1-13120d79466b",
                     "Token" : "2336412f37fb687f5d51e6e241da92fd72d769c811cb257f2ca8bbb9e329dd2eb427b0935ce7fe84f91e14e5994d2d9039b3aade5b4f16dd5ab3979b05751962ceed2c7e193e7b7797630c31eec29477949064522feb104a311b44e1268ba7bdfdc06d7e6f39174dbb69326a379d06cbbc96adcdc24939e36892e024aa0e96d2",
                     "TopicArn" : 'TopicARN',
                     "Message" : "You have chosen to subscribe to the topic arn:aws:sns:us-east-1:589179999999:CostUsageNotificationDemo.\nTo confirm the subscriptionDataBuilder, visit the SubscribeURL included in this message.",
                     "SubscribeURL" : "https://sns.us-east-1.amazonaws.com/?Action=ConfirmSubscription&TopicArn=arn:aws:sns:us-east-1:589179999999:CostUsageNotificationDemo&Token=2336412f37fb687f5d51e6e241da92fd72d769c811cb257f2ca8bbb9e329dd2eb427b0935ce7fe84f91e14e5994d2d9039b3aade5b4f16dd5ab3979b05751962ceed2c7e193e7b7797630c31eec29477949064522feb104a311b44e1268ba7bdfdc06d7e6f39174dbb69326a379d06cbbc96adcdc24939e36892e024aa0e96d2",
                     "Timestamp" : "2018-07-05T12:29:27.641Z",
                     "SignatureVersion" : "1",
                     "Signature" : "L8VmRMT55sv326Rt1HBawA8hPKR0plaBfvI8hlZNm2nhaMkVzvFkvKiMZucfQ7bYWaYqVF+xzvqkaRnMw8/uC4QcrM5DK5HcXYfAJCeI8t32jTg3Kcdn3SGBiyxcBWYt8qSXL7403ho4vIVpCHRuX6K2ZydS7sxx6umr/nanaOUGnkDeC91GFoUMslNw7yITc0YunPwg8GcvKgLhsQr2d7C5I3zDprA+Ds29voLN6v66hH0uR0LEfDq9Ky0Dgii4UebYUgKBCWSy5ETsRHqug5tPNzv9afexjdXrjEUYbvYZO+RRDPztwGjyHw6CL35B85FLZ7UDPLeRysZq47gb+Q==",
                     "SigningCertURL" : "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-eaea6120e66ea12e88dcd8bcbddca752.pem"}
        body = json.dumps(body_dict)
        with self.assertRaises(AWSNotificationHandlerError):
            AWSNotificationHandler(headers, body, validation=False)

    def test_get_region_invalid_arn(self):
        # Removed a ':' in Topic ARN
        headers = [('X-Amz-Sns-Message-Type', 'SubscriptionConfirmation'),
                   ('X-Amz-Sns-Message-Id', '010b7c42-3f24-4865-83b1-13120d79466b'),
                   ('X-Amz-Sns-Topic-Arn', 'arnaws:sns:us-east-1:123456789012:MyTopic'),
                   ('Content-Length', 1637),
                   ('Content-Type', 'text/plain; charset=UTF-8'),
                   ('Host', 'masu.net:6868'),
                   ('Connection', 'Keep-Alive'),
                   ('User-Agent', 'Amazon Simple Notification Service Agent'),
                   ('Accept-Encoding', 'gzip,deflate')]

        body_dict = {"Type" : "SubscriptionConfirmation",
                     "MessageId" : "010b7c42-3f24-4865-83b1-13120d79466b",
                     "Token" : "2336412f37fb687f5d51e6e241da92fd72d769c811cb257f2ca8bbb9e329dd2eb427b0935ce7fe84f91e14e5994d2d9039b3aade5b4f16dd5ab3979b05751962ceed2c7e193e7b7797630c31eec29477949064522feb104a311b44e1268ba7bdfdc06d7e6f39174dbb69326a379d06cbbc96adcdc24939e36892e024aa0e96d2",
                     "TopicArn" : "arn:aws:sns:us-east-1:123456789012:MyTopic",
                     "Message" : "You have chosen to subscribe to the topic arn:aws:sns:us-east-1:589179999999:CostUsageNotificationDemo.\nTo confirm the subscriptionDataBuilder, visit the SubscribeURL included in this message.",
                     "SubscribeURL" : "https://sns.us-east-1.amazonaws.com/?Action=ConfirmSubscription&TopicArn=arn:aws:sns:us-east-1:589179999999:CostUsageNotificationDemo&Token=2336412f37fb687f5d51e6e241da92fd72d769c811cb257f2ca8bbb9e329dd2eb427b0935ce7fe84f91e14e5994d2d9039b3aade5b4f16dd5ab3979b05751962ceed2c7e193e7b7797630c31eec29477949064522feb104a311b44e1268ba7bdfdc06d7e6f39174dbb69326a379d06cbbc96adcdc24939e36892e024aa0e96d2",
                     "Timestamp" : "2018-07-05T12:29:27.641Z",
                     "SignatureVersion" : "1",
                     "Signature" : "L8VmRMT55sv326Rt1HBawA8hPKR0plaBfvI8hlZNm2nhaMkVzvFkvKiMZucfQ7bYWaYqVF+xzvqkaRnMw8/uC4QcrM5DK5HcXYfAJCeI8t32jTg3Kcdn3SGBiyxcBWYt8qSXL7403ho4vIVpCHRuX6K2ZydS7sxx6umr/nanaOUGnkDeC91GFoUMslNw7yITc0YunPwg8GcvKgLhsQr2d7C5I3zDprA+Ds29voLN6v66hH0uR0LEfDq9Ky0Dgii4UebYUgKBCWSy5ETsRHqug5tPNzv9afexjdXrjEUYbvYZO+RRDPztwGjyHw6CL35B85FLZ7UDPLeRysZq47gb+Q==",
                     "SigningCertURL" : "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-eaea6120e66ea12e88dcd8bcbddca752.pem"}
        body = json.dumps(body_dict)
        with self.assertRaises(AWSNotificationHandlerError) as error:
            AWSNotificationHandler(headers, body, validation=False)
        self.assertTrue('Unexpected region name' in str(error.exception))

    def test_get_region_invalid_arn_2(self):
        # Removed all ':' in Subscription ARN
        headers = [('X-Amz-Sns-Message-Type', 'SubscriptionConfirmation'),
                   ('X-Amz-Sns-Message-Id', '010b7c42-3f24-4865-83b1-13120d79466b'),
                   ('X-Amz-Sns-Topic-Arn', 'arnawssnsus-east-1123456789012MyTopic'),
                   ('Content-Length', 1637),
                   ('Content-Type', 'text/plain; charset=UTF-8'),
                   ('Host', 'masu.net:6868'),
                   ('Connection', 'Keep-Alive'),
                   ('User-Agent', 'Amazon Simple Notification Service Agent'),
                   ('Accept-Encoding', 'gzip,deflate')]

        body_dict = {"Type" : "SubscriptionConfirmation",
                     "MessageId" : "010b7c42-3f24-4865-83b1-13120d79466b",
                     "Token" : "2336412f37fb687f5d51e6e241da92fd72d769c811cb257f2ca8bbb9e329dd2eb427b0935ce7fe84f91e14e5994d2d9039b3aade5b4f16dd5ab3979b05751962ceed2c7e193e7b7797630c31eec29477949064522feb104a311b44e1268ba7bdfdc06d7e6f39174dbb69326a379d06cbbc96adcdc24939e36892e024aa0e96d2",
                     "TopicArn" : "arn:aws:sns:us-east-1:123456789012:MyTopic",
                     "Message" : "You have chosen to subscribe to the topic arn:aws:sns:us-east-1:589179999999:CostUsageNotificationDemo.\nTo confirm the subscriptionDataBuilder, visit the SubscribeURL included in this message.",
                     "SubscribeURL" : "https://sns.us-east-1.amazonaws.com/?Action=ConfirmSubscription&TopicArn=arn:aws:sns:us-east-1:589179999999:CostUsageNotificationDemo&Token=2336412f37fb687f5d51e6e241da92fd72d769c811cb257f2ca8bbb9e329dd2eb427b0935ce7fe84f91e14e5994d2d9039b3aade5b4f16dd5ab3979b05751962ceed2c7e193e7b7797630c31eec29477949064522feb104a311b44e1268ba7bdfdc06d7e6f39174dbb69326a379d06cbbc96adcdc24939e36892e024aa0e96d2",
                     "Timestamp" : "2018-07-05T12:29:27.641Z",
                     "SignatureVersion" : "1",
                     "Signature" : "L8VmRMT55sv326Rt1HBawA8hPKR0plaBfvI8hlZNm2nhaMkVzvFkvKiMZucfQ7bYWaYqVF+xzvqkaRnMw8/uC4QcrM5DK5HcXYfAJCeI8t32jTg3Kcdn3SGBiyxcBWYt8qSXL7403ho4vIVpCHRuX6K2ZydS7sxx6umr/nanaOUGnkDeC91GFoUMslNw7yITc0YunPwg8GcvKgLhsQr2d7C5I3zDprA+Ds29voLN6v66hH0uR0LEfDq9Ky0Dgii4UebYUgKBCWSy5ETsRHqug5tPNzv9afexjdXrjEUYbvYZO+RRDPztwGjyHw6CL35B85FLZ7UDPLeRysZq47gb+Q==",
                     "SigningCertURL" : "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-eaea6120e66ea12e88dcd8bcbddca752.pem"}
        body = json.dumps(body_dict)
        with self.assertRaises(AWSNotificationHandlerError) as error:
            AWSNotificationHandler(headers, body, validation=False)
        self.assertTrue('Unexpected Subscription ARN format' in str(error.exception))

    @mock_sns
    def test_get_region_unknown_region(self):
        headers = [('X-Amz-Sns-Message-Type', 'SubscriptionConfirmation'),
                   ('X-Amz-Sns-Message-Id', '010b7c42-3f24-4865-83b1-13120d79466b'),
                   ('X-Amz-Sns-Topic-Arn', 'arn:aws:sns:mars-east-1:123456789012:MyTopic'),
                   ('Content-Length', 1637),
                   ('Content-Type', 'text/plain; charset=UTF-8'),
                   ('Host', 'masu.net:6868'),
                   ('Connection', 'Keep-Alive'),
                   ('User-Agent', 'Amazon Simple Notification Service Agent'),
                   ('Accept-Encoding', 'gzip,deflate')]

        body_dict = {"Type" : "SubscriptionConfirmation",
                     "MessageId" : "010b7c42-3f24-4865-83b1-13120d79466b",
                     "Token" : "2336412f37fb687f5d51e6e241da92fd72d769c811cb257f2ca8bbb9e329dd2eb427b0935ce7fe84f91e14e5994d2d9039b3aade5b4f16dd5ab3979b05751962ceed2c7e193e7b7797630c31eec29477949064522feb104a311b44e1268ba7bdfdc06d7e6f39174dbb69326a379d06cbbc96adcdc24939e36892e024aa0e96d2",
                     "TopicArn" : "arn:aws:sns:us-east-1:123456789012:MyTopic",
                     "Message" : "You have chosen to subscribe to the topic arn:aws:sns:us-east-1:589179999999:CostUsageNotificationDemo.\nTo confirm the subscriptionDataBuilder, visit the SubscribeURL included in this message.",
                     "SubscribeURL" : "https://sns.us-east-1.amazonaws.com/?Action=ConfirmSubscription&TopicArn=arn:aws:sns:us-east-1:589179999999:CostUsageNotificationDemo&Token=2336412f37fb687f5d51e6e241da92fd72d769c811cb257f2ca8bbb9e329dd2eb427b0935ce7fe84f91e14e5994d2d9039b3aade5b4f16dd5ab3979b05751962ceed2c7e193e7b7797630c31eec29477949064522feb104a311b44e1268ba7bdfdc06d7e6f39174dbb69326a379d06cbbc96adcdc24939e36892e024aa0e96d2",
                     "Timestamp" : "2018-07-05T12:29:27.641Z",
                     "SignatureVersion" : "1",
                     "Signature" : "L8VmRMT55sv326Rt1HBawA8hPKR0plaBfvI8hlZNm2nhaMkVzvFkvKiMZucfQ7bYWaYqVF+xzvqkaRnMw8/uC4QcrM5DK5HcXYfAJCeI8t32jTg3Kcdn3SGBiyxcBWYt8qSXL7403ho4vIVpCHRuX6K2ZydS7sxx6umr/nanaOUGnkDeC91GFoUMslNw7yITc0YunPwg8GcvKgLhsQr2d7C5I3zDprA+Ds29voLN6v66hH0uR0LEfDq9Ky0Dgii4UebYUgKBCWSy5ETsRHqug5tPNzv9afexjdXrjEUYbvYZO+RRDPztwGjyHw6CL35B85FLZ7UDPLeRysZq47gb+Q==",
                     "SigningCertURL" : "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-eaea6120e66ea12e88dcd8bcbddca752.pem"}
        body = json.dumps(body_dict)
        with self.assertRaises(AWSNotificationHandlerError) as error:
            AWSNotificationHandler(headers, body, validation=False)
        self.assertTrue('Unexpected region name.' in str(error.exception))

    @mock_sns
    def test_get_region_missing_header(self):
        # Missing X-Amz-Sns-Topic-Arn
        headers = [('X-Amz-Sns-Message-Type', 'SubscriptionConfirmation'),
                   ('X-Amz-Sns-Message-Id', '010b7c42-3f24-4865-83b1-13120d79466b'),
                   ('Content-Length', 1637),
                   ('Content-Type', 'text/plain; charset=UTF-8'),
                   ('Host', 'masu.net:6868'),
                   ('Connection', 'Keep-Alive'),
                   ('User-Agent', 'Amazon Simple Notification Service Agent'),
                   ('Accept-Encoding', 'gzip,deflate')]

        body_dict = {"Type" : "SubscriptionConfirmation",
                     "MessageId" : "010b7c42-3f24-4865-83b1-13120d79466b",
                     "Token" : "2336412f37fb687f5d51e6e241da92fd72d769c811cb257f2ca8bbb9e329dd2eb427b0935ce7fe84f91e14e5994d2d9039b3aade5b4f16dd5ab3979b05751962ceed2c7e193e7b7797630c31eec29477949064522feb104a311b44e1268ba7bdfdc06d7e6f39174dbb69326a379d06cbbc96adcdc24939e36892e024aa0e96d2",
                     "TopicArn" : "arn:aws:sns:us-east-1:123456789012:MyTopic",
                     "Message" : "You have chosen to subscribe to the topic arn:aws:sns:us-east-1:589179999999:CostUsageNotificationDemo.\nTo confirm the subscriptionDataBuilder, visit the SubscribeURL included in this message.",
                     "SubscribeURL" : "https://sns.us-east-1.amazonaws.com/?Action=ConfirmSubscription&TopicArn=arn:aws:sns:us-east-1:589179999999:CostUsageNotificationDemo&Token=2336412f37fb687f5d51e6e241da92fd72d769c811cb257f2ca8bbb9e329dd2eb427b0935ce7fe84f91e14e5994d2d9039b3aade5b4f16dd5ab3979b05751962ceed2c7e193e7b7797630c31eec29477949064522feb104a311b44e1268ba7bdfdc06d7e6f39174dbb69326a379d06cbbc96adcdc24939e36892e024aa0e96d2",
                     "Timestamp" : "2018-07-05T12:29:27.641Z",
                     "SignatureVersion" : "1",
                     "Signature" : "L8VmRMT55sv326Rt1HBawA8hPKR0plaBfvI8hlZNm2nhaMkVzvFkvKiMZucfQ7bYWaYqVF+xzvqkaRnMw8/uC4QcrM5DK5HcXYfAJCeI8t32jTg3Kcdn3SGBiyxcBWYt8qSXL7403ho4vIVpCHRuX6K2ZydS7sxx6umr/nanaOUGnkDeC91GFoUMslNw7yITc0YunPwg8GcvKgLhsQr2d7C5I3zDprA+Ds29voLN6v66hH0uR0LEfDq9Ky0Dgii4UebYUgKBCWSy5ETsRHqug5tPNzv9afexjdXrjEUYbvYZO+RRDPztwGjyHw6CL35B85FLZ7UDPLeRysZq47gb+Q==",
                     "SigningCertURL" : "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-eaea6120e66ea12e88dcd8bcbddca752.pem"}
        body = json.dumps(body_dict)
        with self.assertRaises(AWSNotificationHandlerError) as error:
            AWSNotificationHandler(headers, body, validation=False)
        self.assertTrue('Missing Subscription ARN' in str(error.exception))
