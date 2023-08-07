from bs4 import BeautifulSoup
import urllib.request
import re
from time import sleep


def get_offers():
    source = urllib.request.urlopen('https://www.olx.pl/elektronika/telefony/smartfony-telefony-komorkowe/iphone/?search%5Bfilter_enum_phonemodel%5D%5B0%5D=iphone-14-pro&search%5Bfilter_enum_phonemodel%5D%5B1%5D=iphone-13-pro').read()
    soup = BeautifulSoup(source,'html.parser')
    site = 'https://www.olx.pl'
    offers = [site + tag.get("href") for tag in soup.find_all('a', {"class":"css-rc5s2u"})]
    return offers

def get_price(offer_soup):
    soup = offer_soup
    attr = soup\
        .findAll('h2')
    pattern = r'<h2 class=".*?">(.*?)</h2>'

    for a in attr:
        match = re.search(pattern, str(a))
        if match:
            extracted_text = match.group(1)
            if 'zł' in extracted_text:
                price = extracted_text
    return price

def get_attributes(offer_soup):
    offer_attr = {}

    soup = offer_soup
    attr = soup.findAll('p')

    pattern = r'<p class=".*?">(.*?)</p>'
    pattern_type = r'<span>(.*?)</span>'

    for a in attr:
        match = re.search(pattern, str(a))

        if match:
            extracted_text = match.group(1)
            if ':' in extracted_text and 'Więcej od tego ogłoszeniodawcy' not in extracted_text:
                try:
                    key, value = extracted_text.split(':')
                    offer_attr[key] = value.lstrip()
                except Exception as e:
                    print(e)
                    continue
            match_type = re.search(pattern_type, str(extracted_text))
            if match_type:
                extracted_text_type = match_type.group(1)  
                if extracted_text_type in ['Firmowe', 'Prywatne']:
                    offer_attr['Typ'] = extracted_text_type
    return offer_attr

def get_description(offer_soup):
    soup = offer_soup
    for desc in soup.find_all('div', {"class":"css-bgzo2k er34gjf0"}):
        description = str(desc).replace('<br>','').replace('<br/>','').replace('<div class="css-bgzo2k er34gjf0">','')
    return description

def get_posted_date(offer_soup):
    soup = offer_soup
    for tag in soup.find_all('span', {"class":"css-19yf5ek"}):
        pattern = r'<span class=".*?" data-cy="ad-posted-at">(.*?)</span>'
        match = re.search(pattern, str(tag))
        if match:
            date_posted = match.group(1)
    return date_posted

def get_add_title(offer_soup):
    soup = offer_soup
    for tag in soup.find_all('h1'\
                            , {"class":"css-bg3pmc"}\
                            ):
        pattern = r'<h1 class=".*?" data-cy="ad_title">(.*?)</h1>'
        match = re.search(pattern, str(tag))
        if match:
            add_title = match.group(1)
    return add_title

def main():
    offers = get_offers()
    for offer in offers:
        offer_source = urllib.request.urlopen(offer).read()
        offer_soup = BeautifulSoup(offer_source,'html.parser')
        offer_attr = get_attributes(offer_soup)
        print(offer_attr)
        sleep(5)

main()