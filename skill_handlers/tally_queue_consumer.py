"""
A module to run as a message consumer

This is a proof of concept at this phase. I'm not sure how to test a lot of
this and I'm unfamiliar with the SQS API. I'll get something working and then
make it more elegant later.

It's an infinite loop that pulls new messages off the SQS queue where drinks
collected from Alexa are stashed. This code pulls messages off that queue and
persists them by calling Tallyable methods.
"""

from datetime import datetime
import boto3
import json
import os
from redis import Redis, RedisError
from tally.tallyable import Tallyable

redis = Redis(host="redis",
              db=0,
              socket_connect_timeout=2,
              socket_timeout=2,
              decode_responses=True,
              )

sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName=os.getenv('TALLY_QUEUE_NAME', 'tallies-errors-dev'))
redis_sqs_message_set = os.getenv("REDIS_SET_SQS_MESSAGE_RECEIVED")


def get_messages_from_queue(fx):
    """
    Get messages off SQS queue and call function with message
    :param fx: a function to call with each message
    :return:
    """

    for msg in queue.receive_messages():
        fx(msg)


def message_already_processed(msg):
    """
    A predicate to determine if message has already have been consumed

    :param msg: SQS Message
    :return: Boolean indicating if message has already been consumed
    """

    is_already_member = redis.sismember(redis_sqs_message_set, msg.message_id)
    if not is_already_member:
        redis.sadd(redis_sqs_message_set, msg.message_id)

    return is_already_member


def process_message(msg):
    """
    msg is expected to be an SQS message

    """

    if message_already_processed(msg):
        print("%s is already processed" % msg.message_id)
    else:
        _tally_message(msg)
    msg.delete()


def _tally_message(msg):
    """Actually persist the message to our data store"""

    msg_contents = json.loads(msg.body)
    print("processing %s" % msg_contents['tally_type'])
    if msg_contents['tally_cnt'] and msg_contents['tally_type']:
        tallyable = Tallyable(redis, msg_contents['tally_type'])

    dttm = datetime.strptime(msg_contents['message_created_dttm'],
                             "%Y-%m-%dT%H:%M:%S")

    for _ in range(int(msg_contents['tally_cnt'])):
        tallyable.add(dttm)
        print(tallyable.get_tallies_for_tallyable())


def main():
    while True:
        get_messages_from_queue(process_message)


if __name__ == "__main__":
    main()