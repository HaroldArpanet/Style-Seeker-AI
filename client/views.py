from django.shortcuts import render
from django.conf import settings

def main_page(request):
    context = {
        'server_address': settings.SERVER_ADDRESS,
    }
    return render(request, 'main_page.html', context)
