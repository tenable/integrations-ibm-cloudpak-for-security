from restfly.endpoint import APIEndpoint
import time, arrow, json

class IngestionAPI(APIEndpoint):
    def ingest(self, source, report, wait=False, wait_interval=1, **kwargs):
        '''
        Ingests all of the information in the data paramater directly into the
        asset import endpoint.

        Args:
            source (str):
                The source name.
            report (str):
                The report name.
            wait (bool, optional):
                Should the response be delayed until the import status is known?
                The default if left unspecified is ``False``.
            **kwargs (list):
                The collections or edges to be pushed to the api.  Each item
                must be a list type.

        Returns:
            :obj:`dict`:
                Import Status Document.

        Example:
            >>> sc.ingest.import(assets=[dict(), dict()])
        '''
        ts = int(arrow.utcnow().float_timestamp)
        kwargs['source'] = {
            '_key': 'tenable.io',
            'description': 'Tenable.io platform',
            'product_link': 'https://www.tenable.com/products/tenable-io',
            'timestamp': ts,
        }
        kwargs['report'] = {
            '_key': report,
            'timestamp': ts,
            'type': 'Tenable.io API',
            'description': 'Tenable.io import'
        }
        kwargs['source_report'] = [{
            '_from': 'source/tenable.io',
            '_to': 'report/{}'.format(report),
            'timestamp': ts,
            'active': True
        }]

        job = self._api.post('imports', json=kwargs).json()

        # If we want to wait until the import has returned either a completed
        # or errored state, then we will loop and wait for the job to enter
        # either of those states.
        while wait and job['status'] not in ['COMPLETE', 'ERROR']:
            time.sleep(wait_interval)
            job = self.import_status(job['id'])
        if job.get('code', 200) != 200:
            raise Exception(job)
        return job

    def import_status(self, id):
        '''
        Check the status of an import.

        Args:
            id (str): The identifier for the ingest job.

        Returns:
            :obj:`dict`:
                The status of the specified job.  The status field Should be
                either ``COMPLETE``, ``ERROR``, or ``INPROGRESS``.

        Examples:
            >>> ibm.ingest.import_status(JOB_ID)
        '''
        return self._api.get(
            'importstatus/{}'.format(id)).json()

    def status(self):
        '''
        Retrieves the status of all import jobs.

        Returns:
            :obj:`list`:
                The list of jobs

        Examples:
            >>> for job in ibm.ingest.status():
            ...     print(job)
        '''
        return self._api.get('importstatus').json()