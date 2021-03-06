#!/usr/bin/env python3

import logging
import os

import boto3
from botocore.exceptions import ClientError

import json
import uuid
import datetime
import sys
from argparse import ArgumentParser


def timestamp():
    return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


def send_sqs_message(sqs_queue_url, msg_attributes, msg_body):
    """
    :param sqs_queue_url: String URL of existing SQS queue
    :param msg_body: String message body
    :return: Dictionary containing information about the sent message. If
        error, returns None.
    """

    sqs_client = boto3.client('sqs')
    try:
        logging.info('sending with message attributes: {}'.format(json.dumps(msg_attributes, indent=2)))
        logging.info('sending with body: {}'.format(json.dumps(json.loads(msg_body), indent=2)))
        msg = sqs_client.send_message(QueueUrl=sqs_queue_url,
                                      MessageAttributes=msg_attributes,
                                      MessageBody=msg_body)
    except ClientError as e:
        logging.error(e)
        return None
    return msg


def sample():
    return {
        'cuuid': str(uuid.uuid4()),
        'date': timestamp(),
        'alm': 'github',
        'project': {
            'key': 'janosgyerik_upvotejs',
            'organization_key': 'janosgyerik-github',
        },
        'repository': {
            'full_name': 'janosgyerik/upvotejs',
            'id': '10805910',
        },
        'pull_request': {
            'key': '1',
            'title': 'Foo PR #1',
            'url': 'https://github.com/janosgyerik/upvotejs/pull/1',
            'type': 'internal',
            'base': {
                'branch': 'master',
                'label': 'master',
            },
            'head': {
                'branch': 'feature/foo',
                'label': 'feature/foo',
            },
        },
    }

def main():
    parser = ArgumentParser()
    parser.add_argument("-j", "--json", help="JSON file to send")
    parser.add_argument("-t", "--event-type", help="The event type to use", default="pull-request-opened")
    args = parser.parse_args()

    if args.json:
        with open(args.json) as fh:
            obj = json.loads(fh.read())
    else:
        obj = sample()

    obj['cuuid'] = str(uuid.uuid4())
    msg_body = json.dumps(obj)

    sqs_queue_url = os.environ.get('SQS_QUEUE_URL')
    if not sqs_queue_url:
        print('Error: SQS_QUEUE_URL environment variable not set. Set it to the URL of the queue.')
        sys.exit(1)

    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s: %(asctime)s: %(message)s')

    msg_attributes = {
        'event_type': {
            'StringValue': args.event_type,
            'DataType': 'String',
        },
    }

    msg = send_sqs_message(sqs_queue_url, msg_attributes, msg_body)
    if msg is not None:
        logging.info(f'Sent SQS message ID: {msg["MessageId"]}')


if __name__ == '__main__':
    main()
