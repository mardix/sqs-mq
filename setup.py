"""
# SQS-MQ

A message queue system using AWS SQS

## Features

- Automatically process messages
- Created completed and failed buckets
- Create bucket by pool name
- Process messages by bucket

---

## Install

```
pip install sqs-mq
```

## Create/Connect

```python

mq = SQSMQ(name, 
          aws_access_key_id, 
          aws_secret_access_key, 
          region, 
          visibility_timeout)

```

Alternatively, connect later

```python

mq = SQSMQ(name)

mq.connect(aws_access_key_id, 
          aws_secret_access_key, 
          region)

```


**SQS-MQ** will create 3 buckets of messages:

**QUEUED**: This bucket will contain all the messages to be processed

**COMPLETED**: contains all messages that have have processed successfully

**FAILED**: contains all messages that have failed to process properly, or due to an error.

```python

mq = SQSMQ("myQname", **kwargs)

```

Three buckets will be created: 
`myQname-QUEUED`, `myQname-COMPLETED`, `myQname-FAILED`


---
## Usage 

### Add Task

 ```python

 mq.add(my_function_name, *args, **kwargs)

 ```

### Add Task in different pool

To add a task in a different pool. it will be named: `myQname-QUEUED-FAST`

```python

mq.add(my_fn, *args, **kwargs, pool='FAST')

```

### Add delay

To add a delay

```python

mq.add(my_fn, delay=45)

```

## Run the tasks

### Run all

```python

mq.run()

```

### Run by pool name

```python

mq.run(pool='FAST')

```

---

## COMPLETED and FAILED

Once a tasks have been processed, it will be added in either `COMPLETED` or `FAILED` buckets.

### Run all items in the COMPLETED bucket

```python

def completed_callback(body:dict): 
  data = ...

mq.run_completed(callback=completed_callback)

```

### Run all items in the FAILED bucket

```python

def failed_callback(body:dict): 
  data = ...

mq.run_failed(callback=failed_callback)

```

**Once captured, it will delete the message from the queue**

"""

from setuptools import setup, find_packages

setup(
    name="sqs-mq",
    version="0.1.0",
    license="MIT",
    author="Mardix",
    author_email="mcx2082@gmail.com",
    description="",
    url="https://github.com/mardix/sqs-mq",
    long_description=__doc__,
    py_modules=['sqs_mq'],
    include_package_data=True,
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=[
        "boto",
        "python-slugify"
    ],
    keywords=["aws", "sqs", "mq", "queue", "amazon mq", "celery", "active mq",
              "apollo", "beanstalkd", "resque", "rabbitmq" ,"gearman", "ironmq", "message"],
    platforms='any',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    zip_safe=False
)
