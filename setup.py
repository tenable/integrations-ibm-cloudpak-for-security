from setuptools import setup, find_packages
import os

long_description = '''
Tenable -> IBM Cloud Connect Bridge
For usage documentation, please refer to the github repository at
https://github.com/tenable/integrations-ibmsc
'''

setup(
    name='tenable-ibmsc',
    version='0.1.0',
    description='',
    author='Tenable, Inc.',
    long_description=long_description,
    author_email='smcgrath@tenable.com',
    url='https://github.com/tenable/integrations-ibmsc',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Information Technology',
        'Topic :: System :: Networking',
        'Topic :: Other/Nonlisted Topic',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='tenable tenable_io',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'pytenable>=0.3.15',
        'restfly>=1.0.2',
        'arrow>=0.13.0',
        'Click>=7.0'
    ],
    entry_points={
        'console_scripts': [
            'tenable-ibmsc=tenable_ibmsc.cli:cli',
        ],
    },
)