from restfly.session import APISession
from .databases import DatabaseAPI
from .ingest import IngestionAPI
from .collections import CollectionAPI
from .jobs import JobsAPI
from tenable_ibm_cp4s import __version__

class CloudPak4Security(APISession):
    _vendor = 'Tenable'
    _product = 'CloudPak4Security'
    _build = __version__
    _url = 'https://connect.security.ibm.com/api/car/v2'

    def __init__(self, key, password, **kwargs):
        self._key = key
        self._password = password
        super(CloudPak4Security, self).__init__(**kwargs)

    def _build_session(self, **kwargs):
        super(CloudPak4Security, self)._build_session(**kwargs)
        self._session.auth = (self._key, self._password)

    @property
    def ingest(self):
        return IngestionAPI(self)

    @property
    def databases(self):
        return DatabaseAPI(self)

    @property
    def collections(self):
        return CollectionAPI(self)

    @property
    def jobs(self):
        return JobsAPI(self)
