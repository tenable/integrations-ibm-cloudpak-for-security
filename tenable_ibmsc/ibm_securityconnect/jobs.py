from restfly.endpoint import APIEndpoint

class JobsAPI(APIEndpoint):
    def status(self, id):
        '''
        Retreives the current status of the job

        Args:
            id (str): The UUID of the job to check.

        Returns:
            :obj:`dict`:
                The status of the job.

        Examples:
            >>> ibm.jobs.status(job_id)
        '''
        return self._api.get('jobstatus/{}'.format(id)).json()