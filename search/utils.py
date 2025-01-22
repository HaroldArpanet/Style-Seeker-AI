from rest_framework.request import Request

def get_custom_filters(request: Request) -> list[str]:
    """
    Extract custom filters from the request query parameters.

    :param request: The Django HTTP request object.
    :return: A dictionary of filters extracted from the request.
    """
    filter_keys = [
        'id', 'name', 'description', 'material', 'rating', 'code', 'brand_id', 'brand_name',
        'category_id', 'category_name', 'gender_id', 'gender_name', 'shop_id', 'shop_name',
        'link', 'status', 'colors', 'sizes', 'region', 'currency', 'current_price',
        'old_price', 'off_percent', 'update_date'
    ]
    filters = []
    for key in filter_keys:
        value = request.GET.get(key)
        if value:
            filters.append(key)
    return filters if len(filters) != 0 else False