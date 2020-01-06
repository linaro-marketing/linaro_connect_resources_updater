# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    install_requires=required,
    name='connect_json_updater',
    version='0.1.0',
    description='This module handles the updating of the resources.json file used by the connect.linaro.org static website.',
    long_description=readme,
    author='Kyle Kirkby',
    author_email='kyle.kirkby@linaro.org',
    url='https://github.com/linaro-marketing/linaro_connect_resources_updater',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
