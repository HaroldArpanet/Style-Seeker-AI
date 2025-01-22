from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from search.services.meilisearch_searcher import MeiliSearchService
from search.serializers import ProductSearchSerializer
from search.utils import get_custom_filters

class ProductSearchView(APIView):
    def get(self, request: Request) -> Response:
        """
        Handle GET requests for product search.

        :param request: The Django HTTP request object.
        :return: A DRF Response object containing the search results.
        """
        query = request.GET.get('query', '')
        attributes_to_search_on = get_custom_filters(request)
        if attributes_to_search_on:
            filters = {
                'attributesToSearchOn': attributes_to_search_on,
            }
        else:
            filters = None
        
        search_service = MeiliSearchService('products')
        results = search_service.search(query, filters)
        
        serializer = ProductSearchSerializer(results['hits'], many=True)
        return Response(serializer.data)
    
class DynamicSearchView(APIView):
    def get(self, request: Request, index_name: str) -> Response:
        """
        Handle GET requests for dynamic searching on any MeiliSearch index.

        :param request: The Django HTTP request object.
        :param index_name: The name of the MeiliSearch index to search on.
        :return: A DRF Response object containing the search results.
        """
        query = request.GET.get('query', '')
        filters = {
            key: value.split(',') for key, value in request.GET.items() if key != 'query'
        }
        
        search_service = MeiliSearchService(index_name)
        results = search_service.search(query, filters)
        
        return Response(results)