# coding=utf-8
from setuptools import setup, find_packages


def parse_requirements(filename='requirements.txt'):
    """ load requirements from a pip requirements file. (replacing from pip.req import parse_requirements)"""
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


setup(
    name='airtest-selenium',
    version='1.0.3',
    keywords="selenium, automation test, web ui automation",
    description='Selenium with airtest test framework.',
    long_description='Selenium with airtest test framework. 2018 present by NetEase Games',
    packages=find_packages(),
    include_package_data=True,
    install_requires=parse_requirements(),
    license='Apache License 2.0',

    author='Netease Games',
    author_email='zxfn4514@corp.netease.com, gzliuxin@corp.netease.com',
    url='https://github.com/AirtestProject/airtest-selenium',
)
