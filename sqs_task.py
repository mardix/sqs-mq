"""
SQS-Task

It's a message queue for job execution using AWS SQS

It put data in 2 queues:
    - QUEUED
    - COMPLETED
    - FAILED

QUEUED: messages contain runnable messages, ie: function to run for task

COMPLETED: contains completed data

FAILED: will contained the finished results which will contain completed
            or failed data


You can prioritize the QUEUED by putting messages in different pool.
ie: you may want to have a fast pool, slow pool, or pool with numbers
when fetching the data, you can specify where to get it exactly



- Example

task_q = TaskQ("myQname", "***", "***")

- To add a task (job). you can add as many task as you want. it will be named: `myQname-QUEUED`
task_q.add(my_function_name, *args, **args)

- To add a task in a different pool. it will be named: `myQname-QUEUED-FAST`
task_q.add(my_fn, pool='FAST')

- To add a delay
task_q.add(my_fn, delay=45)

## Run the tasks

- will run only the QUEUED ones
task_q.run()

- To run a pool,
task_q.run(pool='FAST')


# COMPLETED and FAILED

There are two new queues: COMPLETED, FAILED

- run COMPLETED

def completed_callback(body):
    # body is a dict
    data = ...

task_q.run_completed(callback=completed_callback)


- run FAILED

def failed_callback(body):
    # body is a dict
    data = ...

task_q.run_failed(callback=failed_callback)



*** Once captured, it will delete the message from the queue

"""

import datetime
import time
import logging
import functools
from pickle import dumps, loads
from boto import sqs
from slugify import slugify

QUEUE_QUEUED = "QUEUED"
QUEUE_COMPLETED = "COMPLETED"
QUEUE_FAILED = "FAILED"


def to_slug(name):
    return slugify(name, separator="_")


def queued_name(name=None):
    return "%s-%s" % (QUEUE_QUEUED, to_slug(name).upper()) if name else QUEUE_QUEUED


class TaskQ(object):
    _pool = {}

    def __init__(self,
                 name,
                 aws_access_key_id=None,
                 aws_secret_access_key=None,
                 region='us-east-1',
                 visibility_timeout=None
                 ):
        """
        :param name: the name of the queue. At least the additional queues will be created: $name_QUEUED, $name_COMPLETED, $name_FAILED
        :param aws_access_key_id:
        :param aws_secret_access_key:
        :param region:
        :param visibility_timeout: The default visibility timeout for all messages written in the queue. This can be overridden on a per-message.
        :return:
        """
        self.name = to_slug(name)
        self.visibility_timeout = visibility_timeout

        self.connect(region=region,
                     aws_access_key_id=aws_access_key_id,
                     aws_secret_access_key=aws_secret_access_key)

    def connect(self, region='us-east-1', aws_access_key_id=None,
                aws_secret_access_key=None):
        """
        Create a connection
        :param aws_access_key_id:
        :param aws_secret_access_key:
        :param region:
        :return:
        """
        self.conn = sqs.connect_to_region(region,
                                          aws_access_key_id=aws_access_key_id,
                                          aws_secret_access_key=aws_secret_access_key)

    def add(self, callback, pool=None, delay=None, *args, **kwargs):
        """
        To add a task to the queue
        :param callback: a callback function
        :param pool: number or string to identify this queue. It can be 'slow' | 'fast' or '1' | '2'
        :param delay: Number of seconds (0 - 900) to delay this message from being processed.
        :param args: args to pass back in the callable
        :param kwargs:
        :return: the message id
        """
        m = self._write_message(queued_name(name=pool),
                                delay=delay,
                                data={
                                    'callback': callback,
                                    'args': args,
                                    'kwargs': kwargs
                                })
        return m.id

    def queue(self, key):
        if key not in self._pool:
            name = "%s-%s" % (self.name, key)
            queue = self.conn.get_queue(name)
            if not queue:
                queue = self.conn.create_queue(name,
                                               visibility_timeout=self.visibility_timeout)
            self._pool[key] = queue
        return self._pool.get(key)

    def _write_message(self, key, data, delay=None):
        """
        Write the message to the pool
        :param key: The pool name
        :param data: the data to save
        :param delay: Number of seconds (0 - 900) to delay this message from being processed.
        :return:
        """
        message = sqs.message.Message(body=dumps(data))
        return self.queue(key).write(message, delay_seconds=delay)

    def _read_message(self, message):
        """
        :param message: sqs.message.Message
        :return: dict (from _write_message)
        """
        return loads(message.get_body())

    def _get_messages(self, key, size=5, wait_time=30):
        """
        Retrieve the messages
        :param key: The queue key
        :param size: The maximum number of messages to read from the queue
        :param wait_time: The duration (in seconds) for which the call will wait
            for a message to arrive in the queue before returning.
            If a message is available, the call will return sooner
            than wait_time_seconds.
        :return: list (boto.resultset.ResultSet)
        """
        q = self.queue(key)
        return q.get_messages(num_messages=size, wait_time_seconds=wait_time)

    def process(self, key, callback, size=5, pause=5, once=False, wait_time=20, delete=True):
        """
        To process a pool
        :param key:
        :param callback: A callback function
        :param size:
        :param pause:
        :param once:
        :param wait_time:
        :param delete:
        :return:
        """

        while True:
            for message in self._get_messages(key=key,
                                              size=size,
                                              wait_time=wait_time):
                body = self._read_message(message)
                callback(self, body=body)
                if delete:
                    message.delete()

            if once:
                break
            time.sleep(pause)

    def run(self, pool=None, size=5, delay=5, once=False, wait_time=20, write_failed=True):

        """
        Run the QUEUED worker. If pool is provided, it will use
        :param pool: The name of the pool to get
        :param size: The maximum number of messages to read from the queue
        :param pause: The pause time between each request
        :param once: If true, it will run once
        :param wait_time: The duration (in seconds) for which the call will wait
            for a message to arrive in the queue before returning.
            If a message is available, the call will return sooner
            than wait_time_seconds.
        :param write_failed: To write failed in the failed queue
        :return:
        """

        key = queued_name(name=pool)
        while True:
            for message in self._get_messages(key=key, size=size, wait_time=wait_time):
                fail = False
                data = {
                    "id": message.id,
                    "queue_name": key,
                    "status": "pending",
                    "created_at": datetime.datetime.now()
                }
                try:
                    body = self._read_message(message)
                    data.update({
                        "callback": body.get("callback"),
                        "args": body.get("args"),
                        "kwargs": body.get("kwargs")
                    })

                    callback = body.get("callback")
                    result = callback(*body.get("args"), **body.get("kwargs"))
                    data.update({
                        "status": "completed",
                        "result": result,
                    })
                except Exception as ex:
                    fail = True
                    data.update({
                        "status": "failed",
                        "message": ex.message
                    })
                    logging.error("Failed running task: '%s'" % ex.message)
                finally:
                    if not fail:
                        self._write_message(QUEUE_COMPLETED, data)
                    elif write_failed:
                        self._write_message(QUEUE_FAILED, data)

                message.delete()
            if once:
                break
            time.sleep(delay)

    def run_completed(self, callback, **kw):
        self.process(QUEUE_COMPLETED, callback=callback, **kw)

    def run_failed(self, callback, **kw):
        self.process(QUEUE_FAILED, callback=callback, **kw)

    def purge(self, pool_key):
        """
        Purge message in this queue
        :param pool_key:
        :return:
        """
        q = self._pool.get(pool_key)
        if q:
            q.purge()

    def delete(self, pool_key):
        """
        To delete a queue
        :param pool_key:
        :return:
        """
        q = self._pool.get(pool_key)
        if q:
            q.delete()

    def delete_all(self):
        """
        Delete all queues
        :return:
        """
        for k, q in self._pool.items():
            q.delete()

    def purge_all(self):
        """
        Purge messages from all queues
        :return:
        """
        for k, q in self._pool.items():
            q.purge()

    def task(self, pool=None, delay=None):
        """
        A decorator to `add` function to the queue
        :param pool: The pool to use
        :delay pool: Time to wait for this
        :return:
        """

        def deco(fn):
            @functools.wraps(fn)
            def rator(*args, **kwargs):
                self.add(fn, pool=pool, delay=delay, *args, **kwargs)
            return rator
        return deco
