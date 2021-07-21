from car_framework.full_import import BaseFullImport
from car_framework.context import context
from connector.data_handler import DataHandler




import json

class FullImport(BaseFullImport):
    def __init__(self):
        super().__init__()
        # initialize the data handler.
        # If data source doesn't have external reference property None can be supplied as parameter.
        self.data_handler = DataHandler()

    # Create source, report and source_report entry.
    def create_source_report_object(self):
        return self.data_handler.create_source_report_object()

    # GEt save point from server
    def get_new_model_state_id(self):
        # If server doesn't have save point it can just return current time
        # So that it can be used for next incremental import
        return str(self.data_handler.timestamp)

    # Logic to import collections or edges between two save points; called by import_vertices
    def handle_data(self, data_types, collection):
        if collection:
            for obj in collection:
                for handler in data_types:
                    eval('self.data_handler.handle_%s(obj),' % handler.lower())

    # Import all vertices from data source
    def import_vertices(self):

        self.import_assets()
        self.import_vulnerabilities()

        # Send collection data
        self.data_handler.send_collections(self)

    # Imports edges for all collection
    def import_edges(self):
        self.data_handler.send_edges(self)
        self.data_handler.printData()


    def import_assets(self):
        data = context().asset_server.get_assets(0)
        if data:
            self.handle_data(['asset'], data)
        
    def import_vulnerabilities(self):
        data = context().asset_server.get_vulnerabilities(0)
        if data:
            self.handle_data(['vulnerability'], data)
