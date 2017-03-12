"""
SQS-Task

It's a message queue for job execution using AWS SQS

"""

from setuptools import setup, find_packages

setup(
    name="sqs-task",
    version="0.1.0",
    license="MIT",
    author="Mardix",
    author_email="mardix@pylot.io",
    description="",
    url="https://github.com/mardix/sqs-task",
    long_description=__doc__,
    py_modules=['sqs_task'],
    include_package_data=True,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=[
        "boto",
        "python-slugify"
    ],
    keywords=['aws'],
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

