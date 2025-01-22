from rest_framework import serializers
from typing import List, Dict, Optional
import json

class AssistantResponseSerializer(serializers.Serializer):
    role = serializers.CharField()
    content = serializers.CharField()

class ConversationHistorySerializer(serializers.Serializer):
    role = serializers.CharField()
    content = serializers.CharField()

class LLMResponseSerializer(serializers.Serializer):
    assistant_response = AssistantResponseSerializer()
    conversation_history = ConversationHistorySerializer(many=True)
    search_results = serializers.JSONField(required=False)

    def to_representation(self, instance):
        """
        Custom representation to handle the nested structure of the response.
        """
        data = {
            "assistant_response": instance[0],
            "conversation_history": instance[1],
        }
        if len(instance) > 2 and instance[2]:
            data["search_results"] = json.loads(instance[2])
        return data