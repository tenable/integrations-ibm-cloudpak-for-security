from tenable.io import TenableIO

from car_framework.context import context

__version__ = '1.0.3'


class AssetServer(object):

    def __init__(self):
        self.tio = TenableIO(context().args.tioAccessKey, context().args.tioSecretKey,
                             vendor='Tenable', product='CloudPak4Security', build=__version__)

    def get_assets(self, observed_since):
        return self.tio.exports.assets(updated_at=observed_since)

    def get_vulnerabilities(self, observed_since):
        return self.tio.exports.vulns(since=observed_since,
                                      severity=['low', 'medium', 'high', 'critical'])
