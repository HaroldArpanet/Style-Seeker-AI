"""
URL configuration for style_seeker_ai project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from data_pipeline.views import TriggerIndexFlowView
from search.views import ProductSearchView, DynamicSearchView
from llm_chat.views import ChatView

urlpatterns = [
    path('api/data_pipeline/v1/import_json_data/', TriggerIndexFlowView.as_view(), name='trigger-index-flow'),
    path('api/search/v1/product_search/search/', ProductSearchView.as_view(), name='product-search'),
    path('api/search/v1/<str:index_name>/search/', DynamicSearchView.as_view(), name='dynamic-search'),
    path('api/llm_chat/v1/chat/', ChatView.as_view(), name='chat'),
    path('', include('client.urls')),
]
