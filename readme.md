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

## Create

```
mq = SQSMQ(name, 
          aws_access_key_id, 
          aws_secret_access_key, 
          region, visibility_timeout
          )
```

**SQS-MQ** will create 3 buckets of messages:

**QUEUED**: This bucket will contain all the messages to be processed

**COMPLETED**: contains all messages that have have processed successfully

**FAILED**: contains all messages that have failed to process properly, or due to an error.

```
mq = SQSMQ("myQname", **kwargs)
```

Three buckets will be created: 
`myQname-QUEUED`, `myQname-COMPLETED`, `myQname-FAILED`


---
## Usage 

### Add Task


 ```
 mq.add(my_function_name, *args, **kwargs)
 ```

### Add Task in different pool

To add a task in a different pool. it will be named: `myQname-QUEUED-FAST`

```
mq.add(my_fn, *args, **kwargs, pool='FAST')
```

### Add delay

To add a delay

```
mq.add(my_fn, delay=45)
```

## Run the tasks

### Run all

```
mq.run()
```

### Run by pool name
```
mq.run(pool='FAST')
```

---

## COMPLETED and FAILED

Once a tasks have been processed, it will be added in either `COMPLETED` or `FAILED` buckets.

### Run all items in the COMPLETED bucket

```
def completed_callback(body:dict): 
  data = ...

mq.run_completed(callback=completed_callback)
```

### Run all items in the FAILED bucket

```
def failed_callback(body:dict): 
  data = ...

mq.run_failed(callback=failed_callback)
```

**Once captured, it will delete the message from the queue**
