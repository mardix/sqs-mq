"""
# SQS-MQ
"""

from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="sqs-mq",
    version="0.1.0",
    license="MIT",
    author="Mardix",
    author_email="mcx2082@gmail.com",
    description="A message queue system using AWS SQS",
    url="https://github.com/mardix/sqs-mq",
    long_description=long_description,
    long_description_content_type="text/markdown",
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
