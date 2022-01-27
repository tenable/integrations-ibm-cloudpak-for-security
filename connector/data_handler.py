import arrow
from datetime import datetime
import string

from car_framework.context import context
from car_framework.data_handler import BaseDataHandler

ACTIVE = True
sevmap = {0: 0.0, 1: 3.0, 2: 5.0, 3: 7.0, 4: 10.0}


def get_report_time():
    delta = datetime.utcnow() - datetime(1970, 1, 1)
    milliseconds = delta.total_seconds() * 1000
    return milliseconds

def ms_to_unix_ts(ms):
    return int(float(ms) / 1000)

def _ts(obj):
    '''
    Using Arrow will return a time in ms

    Args:
        obj: The object to attempt to convert

    Returns:
        int: The UNIX Timestamp in mills.
    '''
    if obj:
        return int(arrow.get(obj).float_timestamp)
    return 0

def _trunc(data, limit):
    return data[:limit] + (data[limit:] and '...')

class DataHandler(BaseDataHandler):

    def __init__(self):
        super().__init__()

    def create_source_report_object(self):
        if not (self.source and self.report and self.source_report):
            # create source, report and source_report entry and it is compuslory for each imports API call
            self.source = {'_key': context().args.source, 'name': context().args.tioAccessKey, 'description': 'Tenable.io imports', 'product_link' : 'https://cloud.tenable.com'}
            self.report = {'_key': str(self.timestamp), 'timestamp' : self.timestamp, 'type': 'Tenable.io', 'description': 'Tenable.io imports'}
            self.source_report = [{'active': True, '_from': 'source/' + self.source['_key'], '_to': 'report/' + self.report['_key'], 'timestamp': self.report['timestamp']}]
        
        return {'source': self.source, 'report': self.report, 'source_report': self.source_report}

    def handle_asset(self, asset): 
        '''
        Transforms a Tenable.io exported asset into the IBM Security
        Connect format.

        Args:
            asset (dict): The Tenable.io vulnerability format
        '''
        # Hostnames could be FQDNs, NetBIOS, or Hostnames, so for simplicity we
        # will smash all of them together into a singular list.
        asset_names = asset['hostnames'] + asset['fqdns'] + asset['netbios_names']
        hostnames = asset['hostnames'] + asset['fqdns']
        ips = asset['ipv4s'] + asset['ipv6s']

        asset_name = asset_names[0] if asset_names else None
        if not asset_name:
            asset_name = ips[0] if ips else None

        last_modified = _ts(asset['updated_at'])

        # handle asset
        self.add_collection('asset', {
            'external_id': asset['id'],
            'name': asset_name,
            ### Extended Fields Specific to Tenable.io
            'operating_systems': ', '.join(asset.get('operating_systems', list())),
            'tenable_asset_uuid': asset['id'],
            'tenable_agent_uuid': asset['agent_uuid'],
        }, 'external_id')
        
        # handle maccaddress
        for macaddress in asset['mac_addresses']:
            self.add_collection('macaddress', {'_key': macaddress}, '_key')

            asset_macaddress = dict()
            asset_macaddress['_from_external_id'] = asset['id']
            asset_macaddress['_to'] = 'macaddress/' + str(macaddress)
            asset_macaddress['last_modified'] = last_modified
            self.add_edge('asset_macaddress', asset_macaddress)

        # handle ipaddress
        for ipaddress in ips:
            self.add_collection('ipaddress', {'_key': ipaddress}, '_key')

            asset_ipaddress = dict()
            asset_ipaddress['_from_external_id'] = asset["id"]
            asset_ipaddress['_to'] = 'ipaddress/' + ipaddress
            asset_ipaddress['last_modified'] = last_modified
            self.add_edge('asset_ipaddress', asset_ipaddress)

        # handle hostnames
        for hostname in hostnames:
            self.add_collection('hostname', {'_key': hostname}, '_key')

            asset_hostname = dict()
            asset_hostname['_from_external_id'] = asset['id']
            asset_hostname['_to'] = 'hostname/' + hostname
            asset_hostname['last_modified'] = last_modified
            self.add_edge('asset_hostname', asset_hostname)

    def handle_vulnerability(self, vuln):
        '''
        Transforms a Tenable.io exported vulnerability into the IBM Security
        Connect format.

        Args:
            vuln (dict): The Tenable.io vulnerability format
        '''
        plugin = vuln['plugin']
        asset = vuln['asset']
        port = vuln['port']
        statusmap = {
            'OPEN': 'ACTIVE',
            'NEW': 'ACTIVE',
            'REOPENED': 'ACTIVE',
            'FIXED': 'INACTIVE'
        }

        self.add_collection('vulnerability', {
            'external_id': str(plugin['id']),
            'external_reference': ''.join([
                'https://cloud.tenable.com',
                '/tio/app.html#/vulnerability-management',
                '/vulnerabilities/by-plugins/vulnerability-details',
                '/{}/overview'.format(plugin['id'])
            ]),
            'name': plugin['name'],
            'description': plugin['description'],
            'disclosed_on': _ts(plugin.get('vuln_publication_date', '')),
            'published_on': _ts(plugin.get('publication_date', '')),
            'updated_at': _ts(plugin.get('modification_date', '')),
            'base_score': plugin.get('cvss_base_score',
                                     sevmap[vuln['severity_id']]),

            ### Extended Fields Specific to Tenable.io

            'links': plugin.get('see_also', list()),
            'cpes': plugin.get('cpe', list()),
            'solution': _trunc(plugin.get('solution', ''), 1024),
            'synopsis': _trunc(plugin.get('synopsis', ''), 1024),
        }, 'external_id')

        self.add_edge('asset_vulnerability', {
            '_from_external_id': '{}'.format(asset['uuid']),
            '_to_external_id': '{}'.format(plugin['id']),
            'last_modified': _ts(vuln['last_found']),
            'active': vuln['state'] != 'FIXED',
            'port': {
                'port_number': int(port['port']),
                'protocol': '',
                'status': statusmap[vuln['state']],
            },

            ### Extended Fields Specific to Tenable.io

            'vuln_output': vuln.get('output', ''),
        })

