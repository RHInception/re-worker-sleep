# Copyright (C) 2014 SEE AUTHORS FILE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Unittests.
"""

import pika
import mock

from contextlib import nested

from . import TestCase

from replugin import sleepworker


MQ_CONF = {
    'server': '127.0.0.1',
    'port': 5672,
    'vhost': '/',
    'user': 'guest',
    'password': 'guest',
}


class TestSleepWorker(TestCase):

    def setUp(self):
        """
        Set up some reusable mocks.
        """
        TestCase.setUp(self)

        self.channel = mock.MagicMock('pika.spec.Channel')

        self.channel.basic_consume = mock.Mock('basic_consume')
        self.channel.basic_ack = mock.Mock('basic_ack')
        self.channel.basic_publish = mock.Mock('basic_publish')

        self.basic_deliver = mock.MagicMock()
        self.basic_deliver.delivery_tag = 123

        self.properties = mock.MagicMock(
            'pika.spec.BasicProperties',
            correlation_id=123,
            reply_to='me')

        self.logger = mock.MagicMock('logging.Logger').__call__()
        self.app_logger = mock.MagicMock('logging.Logger').__call__()
        self.connection = mock.MagicMock('pika.SelectConnection')

    def tearDown(self):
        """
        After every test.
        """
        TestCase.tearDown(self)
        self.channel.reset_mock()
        self.channel.basic_consume.reset_mock()
        self.channel.basic_ack.reset_mock()
        self.channel.basic_publish.reset_mock()

        self.basic_deliver.reset_mock()
        self.properties.reset_mock()

        self.logger.reset_mock()
        self.app_logger.reset_mock()
        self.connection.reset_mock()

    def test_sleep(self):
        """
        Verify the right amount of time passes when asked to sleep.
        """
        with nested(
                mock.patch('pika.SelectConnection'),
                mock.patch('replugin.sleepworker.SleepWorker.notify'),
                mock.patch('replugin.sleepworker.SleepWorker.send')):
            worker = sleepworker.SleepWorker(
                MQ_CONF,
                logger=self.app_logger,
                output_dir='/tmp/logs/')

            worker._on_open(self.connection)
            worker._on_channel_open(self.channel)
            body = {
                'parameters': {
                    'seconds': 1,
                },
            }

            # Execute the call
            worker.process(
                self.channel,
                self.basic_deliver,
                self.properties,
                body,
                self.logger)

            assert worker.send.call_count == 2  # start then success
            assert worker.send.call_args[0][2] == {
                'status': 'completed', 'data': 1.0}

            assert worker.notify.call_count == 1
            assert 'SleepWorker Executed Successfully' in (
                worker.notify.call_args[0][0])
            assert worker.notify.call_args[0][2] == 'completed'
            # Log should have no errors
            assert self.logger.error.call_count == 0

    def test_without_parameters(self):
        """
        We should fail if we have no paremters.
        """
        with nested(
                mock.patch('pika.SelectConnection'),
                mock.patch('replugin.sleepworker.SleepWorker.notify'),
                mock.patch('replugin.sleepworker.SleepWorker.send')):
            worker = sleepworker.SleepWorker(
                MQ_CONF,
                logger=self.app_logger,
                output_dir='/tmp/logs/')

            worker._on_open(self.connection)
            worker._on_channel_open(self.channel)
            body = {}

            # Execute the call
            worker.process(
                self.channel,
                self.basic_deliver,
                self.properties,
                body,
                self.logger)

            assert worker.send.call_count == 2  # start then error
            assert worker.send.call_args[0][2] == {
                'status': 'failed'}

            assert worker.notify.call_count == 1
            assert 'Parameters dictionary' in worker.notify.call_args[0][1]
            assert worker.notify.call_args[0][2] == 'failed'
            # Log should have one error
            assert self.logger.error.call_count == 1

    def test_without_parameter_seconds(self):
        """
        We should fail if there is no seconds in the parameters.
        """
        with nested(
                mock.patch('pika.SelectConnection'),
                mock.patch('replugin.sleepworker.SleepWorker.notify'),
                mock.patch('replugin.sleepworker.SleepWorker.send')):
            worker = sleepworker.SleepWorker(
                MQ_CONF,
                logger=self.app_logger,
                output_dir='/tmp/logs/')

            worker._on_open(self.connection)
            worker._on_channel_open(self.channel)
            body = {
                'parameters': {},
            }

            # Execute the call
            worker.process(
                self.channel,
                self.basic_deliver,
                self.properties,
                body,
                self.logger)

            assert worker.send.call_count == 2  # start then error
            assert worker.send.call_args[0][2] == {
                'status': 'failed'}

            assert worker.notify.call_count == 1
            assert 'seconds is a required' in worker.notify.call_args[0][1]
            assert worker.notify.call_args[0][2] == 'failed'
            # Log should have one error
            assert self.logger.error.call_count == 1

    def test_with_bad_seconds(self):
        """
        If seconds isn't an int or float we should fail.
        """
        with nested(
                mock.patch('pika.SelectConnection'),
                mock.patch('replugin.sleepworker.SleepWorker.notify'),
                mock.patch('replugin.sleepworker.SleepWorker.send')):
            worker = sleepworker.SleepWorker(
                MQ_CONF,
                logger=self.app_logger,
                output_dir='/tmp/logs/')

            worker._on_open(self.connection)
            worker._on_channel_open(self.channel)
            body = {
                'parameters': {
                    'seconds': 'NOTINTORFLOAT',
                },
            }

            # Execute the call
            worker.process(
                self.channel,
                self.basic_deliver,
                self.properties,
                body,
                self.logger)

            assert worker.send.call_count == 2  # start then error
            assert worker.send.call_args[0][2] == {
                'status': 'failed'}

            assert worker.notify.call_count == 1
            assert 'seconds must be a' in worker.notify.call_args[0][1]
            assert worker.notify.call_args[0][2] == 'failed'
            # Log should have one error
            assert self.logger.error.call_count == 1
