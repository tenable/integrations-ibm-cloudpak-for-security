import argparse, os

from car_framework.context import context
from car_framework.app import BaseApp

from connector.server_access import AssetServer
from connector.full_import import FullImport
from connector.inc_import import IncrementalImport


version = '1.0.1'


class App(BaseApp):
    def __init__(self):
        super().__init__('This script is used for pushing asset data to CP4S CAR ingestion microservice')
        # Add parameters need to connect data source
        self.parser.add_argument('-tio-access-key', dest='tioAccessKey', default=os.getenv('CONFIGURATION_AUTH_TIO_ACCESS_KEY',None), type=str, required=False, help='Tenable.io access key')
        self.parser.add_argument('-tio-secret-key', dest='tioSecretKey', default=os.getenv('CONFIGURATION_AUTH_TIO_SECRET_KEY',None), type=str, required=False, help='Tenable.io secret key')


    def setup(self):
        super().setup()
        context().asset_server = AssetServer()
        context().full_importer = FullImport()
        context().inc_importer = IncrementalImport()


app = App()
app.setup()
app.run()
