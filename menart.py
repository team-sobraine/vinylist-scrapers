import requests
from bs4 import BeautifulSoup
import sys

MENART_SHOP_ID = '63c29ccc3e3f1267bbf97c67'
MAX_PAGE = 262

def get_page(page):
    if (page < 1) or (page > MAX_PAGE):
        print(f'ERROR @ get_url(): page {page} does not exist')
        sys.exit()
    return f'https://www.menartshop.hr/kategorija-proizvoda/glazba/page/{page}/?format-glazba=lp'

def scrape_page(page):
    '''Gets all hrefs from all <a> tags reffering to vinyl pages'''
    hrefs = []
    page_url = get_page(page)
    response = requests.get(page_url)
    if response.status_code != 200:
        print(f'ERROR @ scrape_page(): response.status_code = f{response.status_code}')
        hrefs.append(None)
    else:
        soup = BeautifulSoup(response.content, 'html.parser')
        cards = soup.find_all(class_='type-product')
        for card in cards:
            hrefs.append(card.find('a')['href'])
    return hrefs

def scrape_details(href):
    response = requests.get(href)
    if response.status_code != 200:
        print(f'ERROR @ scrape_details(): response.status_code = f{response.status_code}')
        return None, None, None, None, None, None
    name, author, coverURL, price, barcode, genres = None, None, None, None, None, None
    soup = BeautifulSoup(response.content, 'html.parser')
    name = soup.find(class_='product_title').text
    try:
        author = soup.find(class_='jet-listing-dynamic-terms__link').text
    except AttributeError:
        author = None
    coverURL = soup.find(class_='wp-post-image')['src']
    price = soup.find('p', class_='price').find('bdi').text[0:-2]
    barcode = soup.find(class_='elementor-price-list').find_all('li')[4].find(class_='elementor-price-list-price').text
    a_tags = soup.find(class_='elementor-price-list').find_all('li')[6].find(class_='elementor-price-list-price').find_all('a')
    genres = []
    for tag in a_tags:
        genre = tag.text
        if genre != 'Glazba':
            genres.append(genre)
    return name, author, coverURL, price, barcode, genres


def main(hrefs_file=None, testing=False):
    global MAX_PAGE
    if testing:
        MAX_PAGE = 0
    # get hrefs to all
    if hrefs_file == None:
        hrefs = []
        for i in range(1, MAX_PAGE + 1):
            print(f'SCRAPING PAGE {i}')
            hrefs += scrape_page(i)
        # save to cache file
        with open('hrefs.scraped', 'w') as f:
            f.write(str(hrefs))
    else:
        # read cached hrefs
        with open(hrefs_file, 'r') as f:
            hrefs = f.read()
        hrefs = hrefs[2:-2].split("', '") 

    
    # get info about each vinyl
    vinyls = []
    for i in range(0, len(hrefs)):
        print(f'SCRAPING VINYL {i}')
        vinyl = {
            # ID: autogen by mongo,
            'Name': None,
            'Author': None,
            'CoverURL': None,
            'Price': None,
            'Barcode': None, 
            'Genres': [],
            'SourceURL': hrefs[i],
            'ShopID': MENART_SHOP_ID
        }
        data = scrape_details(hrefs[i])
        vinyl['Name'] = data[0]
        vinyl['Author'] = data[1]
        vinyl['CoverURL'] = data[2]
        vinyl['Price'] = data[3]
        vinyl['Barcode'] = data[4]
        vinyl['Genres'] = data[5]
        vinyls.append(vinyl)
        if testing:
            break
        print(vinyl)
        if (i % 10 == 0):
            with open(f'vinyls{i}.scraped', 'w', encoding="utf-8") as f:
                for vinyl in vinyls:
                    f.write(f"{vinyl['Name']} ||| {vinyl['Author']} ||| {vinyl['CoverURL']} ||| {vinyl['Price']} ||| {vinyl['Barcode']} ||| {vinyl['Genres']} ||| {vinyl['SourceURL']} ||| {vinyl['ShopID']}\n")
    with open(f'vinyls.scraped', 'w', encoding="utf-8") as f:
        for vinyl in vinyls:
            f.write(f"{vinyl['Name']} ||| {vinyl['Author']} ||| {vinyl['CoverURL']} ||| {vinyl['Price']} ||| {vinyl['Barcode']} ||| {vinyl['Genres']} ||| {vinyl['SourceURL']} ||| {vinyl['ShopID']}\n")

if __name__ == '__main__':
    hrefs_file = None
    if len(sys.argv) > 0:
        if '--cached-hrefs' in sys.argv:
            hrefs_file = 'hrefs.scraped'
    main(hrefs_file, testing=False)
