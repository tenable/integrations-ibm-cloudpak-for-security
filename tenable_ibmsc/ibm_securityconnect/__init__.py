from restfly.session import APISession
from .databases import DatabaseAPI
from .ingest import IngestionAPI
from .collections import CollectionAPI
from .jobs import JobsAPI

class SecurityConnect(APISession):
    _lib_identity = 'pyIBMSecurityConnect'
    _url = 'https://app.demo.isc.ibmcloudsecurity.com/api/car/v2'

    def __init__(self, key, password):
        self._key = key
        self._password = password
        APISession.__init__(self)

    def _build_session(self, session=None):
        APISession._build_session(self, session)
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
