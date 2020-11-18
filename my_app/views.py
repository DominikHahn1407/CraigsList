import requests
from django.shortcuts import render

from bs4 import BeautifulSoup


def home(request):
    return render(request, 'base.html')


def new_search(request):
    search = request.POST.get('search')
    context = {
        'search': search
    }
    return render(request, 'my_app/new_search.html', context)
