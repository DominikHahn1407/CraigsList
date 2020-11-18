import re
import requests
from urllib.parse import quote_plus
from django.shortcuts import render
from bs4 import BeautifulSoup

from . import models


BASE_IMAGE_URL = 'https://images.craigslist.org/{}_300x300.jpg'
BASE_CRAIGSLIST_URL = 'https://losangeles.craigslist.org/d/zum-verkauf/search/sss?query={}'


def home(request):
    return render(request, 'my_app/index.html')


def new_search(request):
    search = request.POST.get('search')
    min_price = request.POST.get('min_price')
    max_price = request.POST.get('max_price')
    models.Search.objects.create(search=search)
    final_url = BASE_CRAIGSLIST_URL.format(quote_plus(search))
    response = requests.get(final_url)
    data = response.text
    soup = BeautifulSoup(data, features='html.parser')

    post_listings = soup.find_all('li', {'class': 'result-row'})

    final_postings = []
    post_image_url = ''
    for post in post_listings:
            post_title = post.find(class_='result-title').text
            post_url = post.find('a').get('href')

            if post.find(class_='result-price'):
                post_price = post.find(class_='result-price').text
            else:
                new_response = requests.get(post_url)
                new_data = new_response.text
                new_soup = BeautifulSoup(new_data, features='html.parser')
                post_text = new_soup.find(id='postingbody').text

                r1 = re.findall(r'\$\w+', post_text)
                if r1:
                    post_price = r1[0]
                else:
                    post_price = 'N/A'

            if post.find(class_='result-image').get('data-ids'):
                post_image_ids = post.find(class_='result-image').get('data-ids')
                post_image = post_image_ids.split(',')[0].split(':')[1]
                post_image_url = BASE_IMAGE_URL.format(post_image)
            else:
                post_image_url = 'https://craigslist.org/images/peace.jpg'

            if int(min_price) <= int(float(post_price.replace('$', '').replace(',', '.'))) <= int(max_price):
                final_postings.append((post_title, post_url, post_price, post_image_url))
            else:
                continue

    context = {
        'search': search,
        'final_postings': final_postings
    }
    return render(request, 'my_app/new_search.html', context)
