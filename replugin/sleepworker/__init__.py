#!/usr/bin/env python
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
Simple sleep worker.
"""

from time import sleep

from reworker.worker import Worker


class SleepWorkerError(Exception):
    """
    Base exception class for SleepWorker errors.
    """
    pass


class SleepWorker(Worker):
    """
    Simple worker which sleeps for a set of seconds and returns.
    """

    def process(self, channel, basic_deliver, properties, body, output):
        """
        Sleeps for a set of seconds and then returns.

        `Params Required`:
            * seconds: The amount of seconds to sleep.
        """
        # Ack the original message
        self.ack(basic_deliver)
        corr_id = str(properties.correlation_id)
        # Notify we are starting
        self.send(
            properties.reply_to, corr_id, {'status': 'started'}, exchange='')

        try:
            try:
                params = body['parameters']
            except KeyError:
                raise SleepWorkerError(
                    'Params dictionary not passed to SleepWorker.'
                    ' Nothing to do!')
            if params['seconds'] not in self._config.keys():
                raise SleepWorkerError(
                    'This worker only handles: %s' % self._config.keys())

            try:
                params['seconds'] = float(params['seconds'])
            except ValueError:
                raise SleepWorkerError('Seconds must be an int or float')

            output.info('Executing sleep(%s) ...' % params['seconds'])

            self.app_logger.info('Sleeping for %s' % params['seconds'])

            # TODO: sleep stuff here

            output.debug('Sleeping for %s seconds' % params['seconds'])

            self.app_logger.info('Success for sleep(%s)' % params['seconds'])
            self.send(
                properties.reply_to,
                corr_id,
                {'status': 'completed', 'data': params['seconds']},
                exchange=''
            )
            # Notify on result. Not required but nice to do.
            self.notify(
                'SleepWorker Executed Successfully',
                'SleepWorker successfully executed sleep(%s). See logs.' % (
                    params['seconds']),
                'completed',
                corr_id)
        except SleepWorkerError, fwe:
            # If a SleepWorkerError happens send a failure, notify and log
            # the info for review.
            self.app_logger.error('Failure: %s' % fwe)

            self.send(
                properties.reply_to,
                corr_id,
                {'status': 'failed'},
                exchange=''
            )
            self.notify(
                'SleepWorker Failed',
                str(fwe),
                'failed',
                corr_id)
            output.error(str(fwe))


if __name__ == '__main__':
    mq_conf = {
        'server': '127.0.0.1',
        'port': 5672,
        'vhost': '/',
        'user': 'guest',
        'password': 'guest',
    }
    worker = SleepWorker(
        mq_conf,
        output_dir='/tmp/logs/')
    worker.run_forever()