import argparse, os
from typing import List

from car_framework.context import context
from car_framework.app import BaseApp
from car_framework.extension import SchemaExtension

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

    def get_schema_extension(self):
        return SchemaExtension(
                key = '1f6ab337-b1ac-4558-8dc5-e97b4c666415',
                owner = 'Tenable IO Connector',
                version = '1',
                schema = '''
                {
                    "vertices": [
                        {
                            "name": "vulnerability",
                            "properties": {
                                "links": {
                                    "type": "jsonb"
                                },
                                "cpes": {
                                    "type": "jsonb"
                                },
                                "solution": {
                                    "type": "text"
                                },
                                "synopsis": {
                                    "type": "text"
                                }
                            }
                        }
                    ]
                }
                '''
        )



app = App()
app.setup()
app.run()
