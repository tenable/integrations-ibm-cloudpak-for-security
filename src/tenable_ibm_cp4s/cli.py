#!/usr/bin/env python
'''
MIT License

Copyright (c) 2019 Tenable Network Security, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
import click, logging, time, sys
from tenable.io import TenableIO
from .cloudpak4sec import CloudPak4Security
from .transform import Tio2CP4S
from .__init__ import __version__

@click.command()
@click.option('--tio-access-key',
    envvar='CONFIGURATION_AUTH_TIO_ACCESS_KEY', help='Tenable.io Access Key')
@click.option('--tio-secret-key',
    envvar='CONFIGURATION_AUTH_TIO_SECRET_KEY', help='Tenable.io Secret Key')
@click.option('--batch-size', '-b', envvar='CONFIGURATION_PARAMETER_BATCH_SIZE', default=100,
    type=click.INT, help='Export/Import Batch Sizing')
@click.option('--verbose', '-v', envvar='CONFIGURATION_PARAMETER_VERBOSE', default=0,
    count=True, help='Logging Verbosity')
@click.option('--observed-since', '-s', envvar='CONFIGURATION_PARAMETER_SINCE', default=0,
    type=click.INT, help='The unix timestamp of the age threshold')
@click.option('--run-every', '-r', envvar='RUN_EVERY',
    type=click.INT, help='How many hours between recurring imports')
@click.option('--ibm-access-key', '-a', envvar='CAR_SERVICE_KEY',
    help='The access key for IBMs CAR API.')
@click.option('--ibm-password-key', '-p', envvar='CAR_SERVICE_PASSWORD',
    help='The password key for IBMs CAR API.')
@click.option('--ibm-car-uri', envvar='CAR_SERVICE_URL',
    help='URL of the CAR ingestion service if API key is used for authorization')
@click.option('--car-authtoken', envvar='CAR_SERVICE_AUTHTOKEN',
    help='Auth token for CAR ingestion service')
@click.option('--car-authtoken-url', envvar='CAR_SERVICE_URL_FOR_AUTHTOKEN',
    help='URL of the CAR ingestion service if Auth token is used for authorization')
def cli(tio_access_key, tio_secret_key, batch_size, verbose, observed_since,
        run_every, ibm_password_key, ibm_access_key, ibm_car_uri, car_authtoken, car_authtoken_url):
    '''
    Tenable.io -> IBM CloudPak for Security Transformer & Ingester
    '''

    # Check all paramatere combinations are passed
    if not car_authtoken:
        if not ibm_access_key or not ibm_password_key:
            sys.stderr.write('Either -car-service-token or -car-service-key and -car-service-password arguments are required.')
            sys.exit(2)

    if not ibm_car_uri and not car_authtoken_url:
        sys.stderr.write('Either -car-service-url or -car-service-url-for-token is required.')
        sys.exit(2)

    if ibm_car_uri:
        if not ibm_access_key or not ibm_password_key:
            sys.stderr.write('If -car-service-url is provided then -car-service-key and -car-service-password arguments are required.')
            sys.exit(2)

    if car_authtoken_url:
        if not car_authtoken:
            sys.stderr.write('If -car-service-url-for-token is provided then -car-service-token argument is required.')
            sys.exit(2)

    # Setup the logging verbosity.
    if verbose == 0:
        logging.basicConfig(level=logging.WARNING)
    if verbose == 1:
        logging.basicConfig(level=logging.INFO)
    if verbose > 1:
        logging.basicConfig(level=logging.DEBUG)

    # Initiate the Tenable.io API model, the Ingester model, and start the
    # ingestion and data transformation.
    tio = TenableIO(tio_access_key, tio_secret_key,
        vendor='Tenable', product='CloudPak4Security', build=__version__)

    if car_authtoken:
        base_url = car_authtoken_url
        auth_header = {'Authorization':'car-token ' + car_authtoken}
    else:
        base_url = ibm_car_uri
        auth_header = None

    ibm = CloudPak4Security(ibm_access_key, ibm_password_key, url=base_url, headers=auth_header, ssl_verify=False)
    ingest = Tio2CP4S(tio, ibm)
    ingest.ingest(observed_since, batch_size)

    # If we are expected to continually re-run the transformer, then we will
    # need to track the passage of time and run every X hours, where X is
    # defined by the user.
    if run_every and run_every > 0:
        while True:
            sleeper = run_every * 3600
            last_run = int(time.time())
            logging.info(
                'Sleeping for {}s before next iteration'.format(sleeper))
            time.sleep(sleeper)
            logging.info(
                'Initiating ingest with observed_since={}'.format(last_run))
            ingest.ingest(last_run, batch_size, threads)


if __name__ == "__main__":
    cli()
