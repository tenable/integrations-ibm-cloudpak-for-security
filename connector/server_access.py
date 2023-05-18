from tenable.io import TenableIO

from car_framework.context import context
from car_framework.server_access import BaseAssetServer
__version__ = '1.0.3'


class AssetServer(BaseAssetServer):

    def __init__(self):
        self.tio = TenableIO(context().args.tioAccessKey, context().args.tioSecretKey,
                             vendor='Tenable', product='CloudPak4Security', build=__version__)

    def test_connection(self):
        try:
            from datetime import datetime
            delta = datetime.utcnow() - datetime(1970, 1, 1)
            self.tio.exports.assets(updated_at=delta.total_seconds())
            code = 0
        except Exception as e:
            context().logger.error(e)
            code = 1
        return code

    def get_assets(self, observed_since):
        return self.tio.exports.assets(updated_at=observed_since)

    def get_vulnerabilities(self, observed_since):
        return self.tio.exports.vulns(since=observed_since,
                                      severity=['low', 'medium', 'high', 'critical'])
