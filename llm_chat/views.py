from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
import json
from decouple import config
from llm_chat.serializers import LLMResponseSerializer
from llm_chat.services.llm_chat_actor import LLMService

class ChatView(APIView):
    system_message = """
    You are a helpful and friendly clothing seller assistant. Your job is to help clients find the clothes they are looking for. 
    You should talk to clients like a human and assist them in finding the best clothes based on their preferences. 
    If the client wants to search for specific clothes, you can use the provided functions in tools to search for clothes (Use this tools always and make a function call). 
    Respect to the rules i say and in tools function Respect to structre of arg for function calling. Choose a correct path to answer to client.
    For filter colors and gender and other things you must use function structre in tools remember for example for search in color like red you must write red keyword inquery parameter.
    """
    llm_service = LLMService(
        api_url="https://api.deepinfra.com/v1/openai/chat/completions",
        api_key=config('DEEPINFRA_API_KEY'),
        system_message=system_message
    )

    tools = [{
        "type": "function",
        "function": {
            "name": "search_clothes",
            "description": "Search for clothes based on a query and optional filters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "filters": {
                        "type": "object",
                        "properties": {
                            "attributesToSearchOn": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": [
                                        "id", "name", "description", "material", "rating", "code", 
                                        "brand_id", "brand_name", "category_id", "category_name", 
                                        "gender_id", "gender_name", "shop_id", "shop_name", "link", 
                                        "status", "colors", "sizes", "region", "currency", 
                                        "current_price", "old_price", "off_percent", "update_date"
                                    ]
                                }
                            }
                        },
                        "additionalProperties": False
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            },
            "strict": True
        }
    }]

    def post(self, request: Request) -> Response:
        """
        Handle POST requests to chat with the LLM.

        :param request: The Django HTTP request object.
        :return: A DRF Response object containing the LLM's response.
        """
        try:
            data = json.loads(request.body)
            messages = data.get('messages')

            if not messages:
                return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)

            response = self.llm_service.process_chat_completion(messages, self.tools)

            serializer = LLMResponseSerializer(response)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON payload"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)