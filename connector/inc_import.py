from car_framework.inc_import import BaseIncrementalImport
from car_framework.context import context
from connector.data_handler import DataHandler, ms_to_unix_ts


class IncrementalImport(BaseIncrementalImport):
    def __init__(self):
        super().__init__()
        # initialize the data handler.
        # If data source doesn't have external reference property None can be supplied as parameter.
        self.data_handler = DataHandler()
        self.create_source_report_object()

    # Pulls the save point for last import
    def get_new_model_state_id(self):
        return str(self.data_handler.timestamp)

    # Create source, report and source_report entry.
    def create_source_report_object(self):
        return self.data_handler.create_source_report_object()

    # Save last and new save points to gather data from 
    def get_data_for_delta(self, last_model_state_id, new_model_state_id):
        context().new_model_state_id = new_model_state_id
        context().last_model_state_id = last_model_state_id

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
        data = context().asset_server.get_assets(ms_to_unix_ts(context().last_model_state_id))
        if data:
            self.handle_data(['asset'], data)
        
    def import_vulnerabilities(self):
        data = context().asset_server.get_vulnerabilities(ms_to_unix_ts(context().last_model_state_id))
        if data:
            self.handle_data(['vulnerability'], data)

    def delete_vertices(self):
        pass