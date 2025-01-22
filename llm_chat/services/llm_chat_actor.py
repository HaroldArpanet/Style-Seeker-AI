import json
import requests
import ast
from meilisearch import Client
from search.services.meilisearch_searcher import MeiliSearchService
from search.serializers import ProductSearchSerializer
from typing import Dict, List, Optional, Generator
from openai import OpenAI

class LLMService:
    def __init__(self, api_url: str, api_key: str, system_message: Optional[str] = None):
        """
        Initialize the LLMService with the DeepInfra API URL, API key, and an optional system message.

        :param api_url: The URL of the DeepInfra API.
        :param api_key: The API key for authentication.
        :param system_message: Optional system message to define the LLM's behavior.
        """
        self.api_url = api_url
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        self.system_message = system_message

    def chat_with_llm(
        self,
        messages: List[Dict],
        tools: Optional[List[Dict]] = None,
        stream: bool = True
    ) -> Generator[Dict, None, None]:
        """
        Send a chat request to the LLM and yield chat completion chunks.

        :param messages: List of messages in the conversation.
        :param tools: Optional list of tools (functions) the LLM can call.
        :param stream: Whether to stream the response.
        :return: Generator yielding chat completion chunks.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0",
            "Accept": "text/event-stream",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Referer": "https://deepinfra.com/",
            "Content-Type": "application/json",
            "X-Deepinfra-Source": "web-embed",
            "Authorization": f"Bearer {self.api_key}",
            "Origin": "https://deepinfra.com",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "DNT": "1",
            "Sec-GPC": "1",
            "Priority": "u=0",
        }

        if self.system_message:
            messages.insert(0, {"role": "system", "content": self.system_message})

        payload = {
            "model": "meta-llama/Meta-Llama-3.1-405B-Instruct",
            "messages": messages,
            "stream": stream,
        }

        if tools:
            payload["tools"] = tools

        with requests.post(self.api_url, headers=headers, json=payload, stream=True) as response:
            print(response.text)
            if response.text == '{"detail":{"error":"inference prohibited, please enter a payment method in https://deepinfra.com/dash/settings"}}':
                print("PAYMENT")
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith("data:"):
                        chunk = json.loads(decoded_line[5:])
                        yield chunk

    def handle_function_call(self, function_name: str, function_args: Dict) -> Dict:
        """
        Execute a function requested by the LLM and return the result.

        :param function_name: The name of the function to call.
        :param function_args: The arguments for the function.
        :return: The result of the function call.
        """
        if isinstance(function_args, dict):
            return self.search_clothes(**function_args)
        else:
            raise ValueError(f"Invalid function_args: Expected dict, got {type(function_args)}")

    def search_clothes(self, query: str, filters: Optional[Dict] = None) -> Dict:
        """
        Example function to search for clothes.

        :param query: The search query.
        :param filters: Optional filters to refine the search.
        :return: A dictionary containing search results.
        """
        if filters != None and len(filters) == 0:
            filters = None

        meili_search_service = MeiliSearchService('products')
        search_results = meili_search_service.search(query, filters)
        #search_results = meili_search_service.search(query, {'attributesToSearchOn': ['name']})
        serializer = ProductSearchSerializer(search_results['hits'], many=True)
        return serializer.data

    def process_chat_completion(self, messages: List[Dict], tools: Optional[List[Dict]] = None) -> Dict:
        """
        Process a chat completion, handling function calls if necessary.

        :param messages: List of messages in the conversation.
        :param tools: Optional list of tools (functions) the LLM can call.
        :return: The final response from the LLM.
        """
        assistant_response = {"role": "assistant", "content": ""}
        chat = self.chat_with_llm(messages, tools)
        for chunk in chat:
            if "choices" in chunk:
                choice = chunk["choices"][0]
                delta = choice.get("delta", {})

                if "content" in delta and delta["content"]:
                    assistant_response["content"] += delta["content"]

                if "tool_calls" in delta and delta["tool_calls"]:
                    for tool_call in delta["tool_calls"]:
                        if tool_call["type"] == "function":
                            function_name = tool_call["function"]["name"]
                            function_args = json.loads(tool_call["function"]["arguments"])
                            function_result = self.handle_function_call(function_name, function_args)
                            messages.append({
                                "role": "function",
                                "name": function_name,
                                "content": json.dumps(function_result),
                            })

                if choice.get("finish_reason") == "stop":
                    return [assistant_response, messages, json.dumps(function_result)]

        return [assistant_response, messages, None]