from rest_framework import serializers

class ProductSearchSerializer(serializers.Serializer):
    """
    Serializer for product search results.
    """
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    material = serializers.CharField()
    rating = serializers.FloatField()
    images = serializers.ListField(child=serializers.URLField())
    code = serializers.CharField()
    brand_id = serializers.IntegerField()
    brand_name = serializers.CharField()
    category_id = serializers.IntegerField()
    category_name = serializers.CharField()
    gender_id = serializers.IntegerField()
    gender_name = serializers.CharField()
    shop_id = serializers.IntegerField()
    shop_name = serializers.CharField()
    link = serializers.URLField()
    status = serializers.CharField()
    colors = serializers.ListField(child=serializers.CharField())
    sizes = serializers.ListField(child=serializers.CharField())
    region = serializers.CharField()
    currency = serializers.CharField()
    current_price = serializers.FloatField()
    old_price = serializers.FloatField()
    off_percent = serializers.FloatField()
    update_date = serializers.DateTimeField()