from restfly.endpoint import APIEndpoint

class CollectionAPI(APIEndpoint):
    def graph(self, collection, key):
        return self._api.get('{}/{}/graph'.format(collection, key)).json()

    def delete_source(self, source):
        '''
        Performs a soft delete to all of the data related to the source
        specified.

        Args:
            source (str): The source key

        Examples:
            >>> ibm.collections.delete_source(source_key)
        '''
        self._api.delete('source/{}'.format(source)).json()

    def delete_collection(self, source, collection):
        '''
        Performs a soft delete all of the collection data for a given source.

        Args:
            source (str): The source key
            collection (str): The name of the collection to delete.

        Examples:
            >>> ibm.collections.delete_collection(source_key, collection_name)
        '''
        self._api.delete('source/{}/{}'.format(source, collection)).json()

    def delete_entry(self, source, collection, key):
        '''
        Performs a soft delete for a specific item and the edges
        associated to it.

        Args:
            source (str): The source key
            collection (str): THe name of the collection
            key (str): The identifier for the item to delete.

        Examples:
            >>> ibm.collections.delete_entry(source_key, collection_name, key)
        '''
        self._api.delete(
            'source/{}/{}/{}'.format(source, collection, key)).json()

    def hard_delete(self, collection, key):
        '''
        Performs a hard delete to the specific item and edges connected to it.

        Args:
            collection (str): The name of the collection
            key (str): The identifier for the item to delete.

        Returns:
            :obj:`bool`:
                Was the deletion successful?

        Examples:
            >>> ibm.collections.hard_delete(collection_name, key)
        '''
        return self._api.delete(
            '{}/{}'.format(collection. key)).json()['isdeleted']

    def search(self, collection, *values):
        '''
        Search the collection specified for the specified values

        Args:
            collection (str): The name of the collection to search
            *values (str): The items to search for.  (Is this logical OR or AND??)

        Returns:
            :obj:`list`:
                Objects that match the search criteria.

        Examples:
            >>> for item in ibm.collections.search('user',
            ...                                    'Jasen_Senger',
            ...                                    'Cicero_Kovacek41'):
            ...     print(item)
        '''
        return self._api.post('search/{}'.format(collection),
            json={'list': list(values)}).json()

    def ipvulns(self, *ips):
        '''
        Retrieves the vulnerability data related to a given set of IP Addresses

        Args:
            *ips (str): An IP address to search against

        Returns:
            :obj:`list`:
                A list of items that match the criteria.

        Examples:
            >>> for item in ibm.collections.ipvulns('10.1.1.10', '124.10.21.56'):
            ...     print(item)
        '''
        return self._api.post('ipvulnerability', json={'list': list(ips)}).json()

    def get(self, collection, key):
        '''
        Retrieves the details of a specific item and edges connected to it.

        Args:
            collection (str): The name of the collection
            key (str): The unique key associated to the item to retrieve.

        Returns:
            :obj:`list`:
                The item and edged associated to the item.

        Examples:
            >>> items = ibm.collections.get('user', 'Cicero_Kovacek41')
        '''
        return self._api.get('{}/{}'.format(collection, key)).json()