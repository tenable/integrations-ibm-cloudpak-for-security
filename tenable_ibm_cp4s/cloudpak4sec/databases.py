from restfly.endpoint import APIEndpoint
from restfly.errors import *
import time


class DatabaseAPI(APIEndpoint):
    def _wait_for_job(self, jid):
        '''
        Waits for the specified job id to return in a non-progress state.
        '''
        job = self._api.jobs.status(jid)
        while job['status'] not in ['COMPLETE', 'ERROR']:
            time.sleep(10)
            job = self._api.jobs.status(jid)
        return job

    def status(self):
        '''
        Retrieves the status of the databases.

        Returns:
            :obj:`dict`:
                The status dictionary.  If the databases are not created, then
                None is returned.

        Examples:
            >>> ibm.databases.status()
        '''
        try:
            return self._api.get('databases').json()['databases'][0]
        except (BadRequestError, ServerError) as err:
            return None

    def update(self, data):
        '''
        Perform various update operations on the databases.

        Args:
            data (dict):
                The data structure to push to the update endpoint.

        Examples:
            >>> ibm.databases.update({'something': 'data'})
        '''
        jid = self._api.patch('databases', json=data).json()['job_id']
        self._wait_for_job(jid)

    def create(self):
        '''
        Creates the Databases

        Returns:
            :obj:`list`:
                The list of associated jobs related to the db creation.

        Examples:
            >>> ibm.databases.create()
        '''
        jid = self._api.post('databases', json={}).json()['job_id']
        self._wait_for_job(jid)

    def delete(self):
        '''
        Deletes the database

        Examples:
            >>> ibm.databases.delete()
        '''
        self._api.delete('databases')


    def initialize(self):
        '''
        Initialization process for the databases.  This process is a blocking
        call that will attempt to check to see if the databases are in a state
        for ingestion & searching.  If they are not, then we will inform CAR to
        create the necessary databases and validate that there are no missing
        collections & indexes.  If there are, we will attempt to update the
        databases with the necessary information.

        Examples:
            >>> ibm.databases.initialize()
        '''
        # Check for the database to see if it has been created.  If it hasn't,
        # then we will want to run the create call and wait for the databases
        # status to return the necessary information.
        status = self.status()
        if not status:
            self.create()
            status = self.status()


        while len(status.get('missing_collections', [])) > 0:
            # As there appear to be missing collections in the database, we will
            # want to inform the database API that it should create those
            # collections.  We'll give approximately 2 seconds a collection
            # (double the example in the API docs) and then re-attempt.
            self._log.info('Informing SecurityConnect that collections are missing')
            self.update(status.get('missing_collections'))
            status = self.status()

        while len(status.get('collections_without_indexes')) > 0:
            # As there appear to be missing indexes in the database, we will
            # want to inform the database API that it should create those
            # collection indexes.  We'll give approximately 2 seconds a
            # collection (double the example in the API docs) and then
            # re-attempt.
            self._log.info('Informing SecurityConnect that indexes are missing')
            self.update({'collections_without_indexes': status.get(
                    'collections_without_indexes')})
            status = self.status()

        while not status.get('is_ready'):
            # if after all of this, the database still doesn't report as ready,
            # then we will need to just wait here until informed that we can
            # proceed.
            time.sleep(10)
            status = self.status()