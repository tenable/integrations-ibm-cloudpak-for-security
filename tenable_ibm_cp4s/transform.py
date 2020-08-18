import arrow
import logging
from restfly.utils import trunc


class Tio2CP4S:
    _cache = dict()
    _report_id = None

    def __init__(self, tio, ibmsc):
        self._log = logging.getLogger('{}.{}'.format(
            self.__module__, self.__class__.__name__))
        self.ibm = ibmsc
        self.tio = tio

    def _ts(self, obj):
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

    def _add_to_cache(self, collection, item):
        '''
        Adds an item to the cache and will create the collection in the cache if
        one doesn't exist yet. Does not add duplicate items to the cache.
        '''
        if collection not in self._cache:
            self._cache[collection] = dict()
        key = item.get('_key') or item.get('external_id')
        if not key:
            from_key = item.get('_from_external_id') or item.get('_from')
            to_key = item.get('_to_external_id') or item.get('_to')
            key = "{}_{}".format(from_key, to_key)
        self._cache[collection].setdefault(key, item)

    def _drain_cache(self, collection, limit):
        '''
        Checks to see if the cache for a specific collection has reached the
        specified limit.  If so, then upload the entire cache.

        Args:
            collection (str): The name of the collection to validate
            limit (int): The number of items in which to initiate an upload.
        '''
        if len(self._cache.get(collection, {}).keys()) >= limit or limit == 0:
            cache = {collection: list(entries.values())
                     for collection, entries in self._cache.items()}
            self.ibm.ingest.ingest('tenable.io', self._report_id, wait=True, **cache)
            self._cache = dict()

    def _transform_vuln(self, vuln):
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
        sevmap = {0: 0.0, 1: 3.0, 2: 5.0, 3: 7.0, 4: 10.0}

        self._add_to_cache('vulnerability', {
            'external_id': str(plugin['id']),
            'external_reference': ''.join([
                'https://cloud.tenable.com',
                '/tio/app.html#/vulnerability-management',
                '/vulnerabilities/by-plugins/vulnerability-details',
                '/{}/overview'.format(plugin['id'])
            ]),
            'name': plugin['name'],
            'description': plugin['description'],
            'disclosed_on': self._ts(plugin.get('vuln_publication_date', '')),
            'published_on': self._ts(plugin.get('publication_date', '')),
            'updated_at': self._ts(plugin.get('modification_date', '')),
            'base_score': plugin.get('cvss_base_score',
                                     sevmap[vuln['severity_id']]),
            'source': 'tenable.io',

            ### Extended Fields Specific to Tenable.io

            'links': plugin.get('see_also', list()),
            'cpes': plugin.get('cpe', list()),
            'solution': trunc(plugin.get('solution', ''), 1024),
            'synopsis': trunc(plugin.get('synopsis', ''), 1024),
        })

        self._add_to_cache('asset_vulnerability', {
            '_from_external_id': '{}'.format(asset['uuid']),
            '_to_external_id': '{}'.format(plugin['id']),
            'timestamp': self._ts(arrow.utcnow()),
            'last_modified': self._ts(vuln['last_found']),
            'active': vuln['state'] != 'FIXED',
            'report': str(self._report_id),
            'source': 'tenable.io',
            'port': {
                'port_number': int(port['port']),
                'protocol': '',
                'status': statusmap[vuln['state']],
            },

            ### Extended Fields Specific to Tenable.io

            'vuln_output': vuln.get('output', ''),
        })

    def _transform_asset(self, asset):
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

        def edge(to_key):
            return {
                '_from_external_id': asset['id'],
                '_to': to_key,
                'timestamp': self._ts(arrow.utcnow()),
                'source': 'tenable.io',
                'last_modified': self._ts(asset['updated_at']),
                'report': str(self._report_id),
                'active': True,
            }

        asset_name = asset_names[0] if asset_names else None
        if not asset_name:
            asset_name = ips[0] if ips else None

        self._add_to_cache('asset', {
            'external_id': asset['id'],
            'name': asset_name,

            ### Extended Fields Specific to Tenable.io

            'operating_systems': asset.get('operating_systems', list()),
            'tenable_asset_uuid': asset['id'],
            'tenable_agent_uuid': asset['agent_uuid'],
        })

        for macaddress in asset['mac_addresses']:
            self._add_to_cache('macaddress', {'_key': macaddress})
            self._add_to_cache('asset_macaddress',
                edge('macaddress/{}'.format(macaddress)))

        for ipaddress in ips:
            self._add_to_cache('ipaddress', {'_key': ipaddress})
            self._add_to_cache('asset_ipaddress',
                edge('ipaddress/{}'.format(ipaddress)))

        for hostname in hostnames:
            self._add_to_cache('hostname', {'_key': hostname})
            self._add_to_cache('asset_hostname',
                edge('hostname/{}'.format(hostname)))

    def ingest(self, observed_since, batch_size=None):
        '''
        Perform the ingestion

        Args:
            observed_since (int):
                The unix timestamp of the age threshhold.  Only vulnerabilities
                observed since this date will be imported.
            batch_size (int, optional):
                The number of findings to send to Security Hub at a time.  If
                nothing is specified, it will default to 100.
        '''

        # First step is to perform the database initialization to ensure that
        # We actually have a database to talk to.
        self.ibm.databases.initialize()

        # If there was no batch size set, then set the detail to 100.
        if not batch_size:
            batch_size = 100

        # Set the report id to the current timestamp.
        self._report_id = str(self._ts(arrow.utcnow()))

        self._log.info('initiating asset collection ingest & transform')
        assets = self.tio.exports.assets(updated_at=observed_since)
        for asset in assets:
            # transform the asset data and add it to the cache.
            self._transform_asset(asset)
            self._drain_cache('asset', batch_size)

        # Drain whatever is left in the cache.
        self._drain_cache('asset', 0)
        self._log.info('completed asset collection ingest.')

        self._log.info('initiating vulnerability collection ingest & transform')
        vulns = self.tio.exports.vulns(since=observed_since,
            severity=['low', 'medium', 'high', 'critical'])
        for vuln in vulns:
            self._transform_vuln(vuln)
            self._drain_cache('vulnerability', batch_size)

        # Drain whatever is leftover in the cache.
        self._drain_cache('vulnerability', 0)
        self._log.info('Processed {} assets and {} vulns'.format(
            assets.count, vulns.count))
        self._log.info('completed vuln collection ingest.')


# Rewrite to check status and use multiple threads for parallel exec.
