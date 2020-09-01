from setuptools import setup, find_packages
import os

long_description = '''
Tenable -> IBM Cloud Pak for Security Bridge
For usage documentation, please refer to the github repository at
https://github.com/tenable/integrations-ibm-cloudpak-for-security
'''

setup(
    name='tenable-ibm-cp4s',
    version='1.0.3',
    description='Tenable -> IBM Cloud Pak for Security Bridge',
    author='Tenable, Inc.',
    long_description=long_description,
    author_email='smcgrath@tenable.com',
    url='https://github.com/tenable/integrations-ibm-cloudpak-for-security',
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
    keywords='tenable tenable_io ibm cloudpak cloudpak4security',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'pytenable>=0.3.28',
        'restfly>=1.1.0',
        'arrow>=0.13.0',
        'Click>=7.0'
    ],
    entry_points={
        'console_scripts': [
            'tenable-ibm-cp4s=tenable_ibm_cp4s.cli:cli',
        ],
    },
)