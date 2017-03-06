"""
mysqs.TaskQ a message queue manager for SQS that executes jobs in the background

It put data in 2 queues:
    - queued
    - finished

queued: messages contain runnable messages, ie: function to run for task
finished: will contained the finished results which will contain completed
            or failed data


myQ = TaskQ("myQname", "***", "***")

- To add a task(job)
myQ.add(my_function_name, *args, **args)

- To process jobs

myQ.run()

- To received finished data

def callback(data):
    # do something with data

myQ.run_finished(callback)

Once captured, it will delete the message from the queue

"""

import datetime
import time
import logging
from pickle import dumps, loads
from boto import sqs

QUEUED_POOL = "queued"
FINISHED_POOL = "finished"


class TaskQ(object):
    def __init__(self,
                 name,
                 aws_access_key_id,
                 aws_secret_access_key,
                 region='us-east-1',
                 ttl=7200
                 ):
        """
        :param name: the name of the messages container. From that name it will create queued and finished pools
        :param aws_access_key_id:
        :param aws_secret_access_key:
        :param region:
        :param ttl:
        :return:
        """
        self._pools = [QUEUED_POOL, FINISHED_POOL]
        self.name = name
        self.ttl = ttl
        self.sqs_conn = sqs.connect_to_region(region,
                                              aws_access_key_id=aws_access_key_id,
                                              aws_secret_access_key=aws_secret_access_key)

    def queue(self, pool_key=QUEUED_POOL):
        name = self.name + "-" + pool_key
        queue = self.sqs_conn.get_queue(name)
        if not queue:
            queue = self.sqs_conn.create_queue(name)
        return queue

    def add(self, callable, delay_seconds=None, *args, **kwargs):
        """
        To add executable tasks
        :param callable:
        :param delay_seconds: Change the visibility delay for this message
        :param args:
        :param kwargs:
        :return:
        """
        m = self.write_message(QUEUED_POOL,
                               delay_seconds=delay_seconds,
                               data={
                                   'callable': callable,
                                   'args': args,
                                   'kwargs': kwargs
                               })
        return m.id

    def write_message(self, pool_key, data, delay_seconds=None):
        """
        Write the message to the pool
        :param pool_key: The pool key
        :param data: the data to save
        :param delay_seconds: Change the visibility delay for this message
        :return:
        """
        message = sqs.message.Message(body=dumps(data))
        m = self.queue(pool_key).write(message, delay_seconds=delay_seconds)
        return m

    def fetch(self, pool_key, size=5, wait_time=30):
        """
        Fetch the messages
        :param pool_key:
        :param size:
        :param wait_time:
        :return:
        """
        q = self.queue(pool_key)
        while q.count():
            for message in q.get_messages(num_messages=size,
                                          wait_time_seconds=wait_time):
                yield message

    def run(self, size=5, pause=5, burst=False, wait_time=20):
        """
        Run the task worker
        :param size: Total of tasks to request at a time
        :param pause: The pause time between each request
        :param burst: If true, it will run once
        :param wait_time: wait time between
        :return:
        """
        while True:
            for message in self.fetch(pool_key=QUEUED_POOL,
                                      size=size,
                                      wait_time=wait_time):
                try:
                    body = self.message_data_to_object(message)
                    result = self._run_task_callable(callable=body["callable"],
                                                     args=body["args"],
                                                     kwargs=body["kwargs"])
                    data = {
                        "id": message.id,
                        "status": "completed",
                        "result": result,
                        "created_at": datetime.datetime.now()
                    }
                except Exception as ex:
                    data = {
                        "id": message.id,
                        "status": "failed",
                        "message": ex.message,
                        "created_at": datetime.datetime.now()
                    }

                    logging.error("Failed running task: '%s'" % ex.message)
                finally:
                    self.write_message(FINISHED_POOL, data)
                    message.delete()
            if burst:
                break
            time.sleep(pause)

    def run_finished(self, callback, size=5, pause=5, burst=False,
                     wait_time=30, delete=True):
        """
        RUn finished queued and pass the message callable function
        :param callback: fun : callable function
        :param size:
        :param pause:
        :param burst: if true it will run one
        :param wait_time:
        :param delete: (bool) to delete upon processing
        :return:
        """
        while True:
            for message in self.fetch(pool_key=FINISHED_POOL,
                                      size=size,
                                      wait_time=wait_time):
                content = self.message_data_to_object(message)
                callback(content)
                if delete:
                    message.delete()

            if burst:
                break
            time.sleep(pause)

    def _run_task_callable(self, callable, args, kwargs):
        return callable(*args, **kwargs)

    def message_data_to_object(self, message):
        return loads(message.get_body())

    def delete(self):
        """
        Delete the Q and queue pools
        """
        for key in self._pools:
            self.sqs_conn.delete_queue(self.queue(key))
