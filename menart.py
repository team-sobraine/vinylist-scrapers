import requests
from bs4 import BeautifulSoup
import os
import time

IMAGE_URL_BASE = 'https://www.menartshop.hr'

def scrape(url_base, pages):
    catalog = []
    for i in range(1, pages+1):
        print(f"ON PAGE {i}")
        # TESTING ONLY
        #
        # FILE = 'site.html'
        # if os.path.exists(FILE):
        #     with open(FILE, 'r') as f:
        #         site = f.read()
        # else:
        #     r = requests.get(url_base)
        #     with open(FILE, 'w') as f:
        #         site = str(r.content, 'UTF-8')
        #         f.write(site)
        
        # PRODUCTION ONLY
        #
        r = requests.get(url_base+str(i))
        site = str(r.content, 'UTF-8')

        soup = BeautifulSoup(site, 'html.parser')
        elements = soup.find_all(class_='webshopNewItem')

        for element in elements:
            image_css = element.find(class_='imgWrapper anim03').get('style')
            image_url = IMAGE_URL_BASE + image_css[image_css.find('(')+1:image_css.find(')')]
            title = element.find(class_='title').contents[0]
            price1 = element.find(class_='primary-currency').contents[0][:-3]
            price2 = element.find(class_='secondary-currency').contents[0][1:-1][:-4]
            catalog.append([image_url, title, price1, price2])
        #time.sleep(5)

    return catalog