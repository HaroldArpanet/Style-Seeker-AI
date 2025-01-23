from meilisearch import Client
from decouple import config
from typing import Optional

class MeiliSearchService:
    def __init__(self, index_name: str) -> None:
        """
        Initialize the MeiliSearchService.

        :param index_name: The name of the MeiliSearch index to interact with.
        """
        self.client = Client(config('MEILISEARCH_HOST'), config('MEILISEARCH_API_KEY'))
        self.index = self.client.index(index_name)

    def search(self, query: str, filters: Optional[dict[str, object]] = None) -> dict[str, object]:
        """
        Perform a search on the MeiliSearch index.

        :param query: The search query string.
        :param filters: Optional dictionary of filters to apply to the search.
        :return: A dictionary containing the search results.
        """
        if filters is None:
            filters = {}
        return self.index.search(query, filters)