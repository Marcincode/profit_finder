"""
Scrap data script

Extracts data from site to stage files in csv format
Using column names in pl as origin site and extracted attributes are in polish
"""
from bs4 import BeautifulSoup
import urllib.request
import re
from time import sleep
import pandas as pd
import datetime

# This html tag may change, check and edit in case of problems with get_price() function
price_header = "h3"

# Compose search url from site , category and filter conditions
site = "https://www.olx.pl"
category = "/elektronika/telefony/smartfony-telefony-komorkowe/iphone/"
filter_condition_url = "?search%5Bfilter_enum_phonemodel%5D%5B0%5D=iphone-14-pro&search%5Bfilter_enum_phonemodel%5D%5B1%5D=iphone-13-pro"
search_url = site + category + filter_condition_url

# =============================================================================
# Add customized functions here. apply_transformation is required
# =============================================================================


def get_offers(search_url):
    """
    Get list of offers from provided search URL

    Parameters
    ----------
    search_url: string
        URL address to search in for latest offers

    Returns
    -------
    list
        List of latest offers

    """
    source = urllib.request.urlopen(search_url).read()
    soup = BeautifulSoup(source, "html.parser")
    offers = [
        site + tag.get("href") for tag in soup.find_all("a", {"class": "css-rc5s2u"})
    ]
    return offers


def get_attributes(offer_soup):
    """
    Get set of attributes for offer provided in soup format

    Parameters
    ----------
    offer_soup: BeautifulSoup
        Soup of offer

    Returns
    -------
    set
        Set of offer attributes

    """
    offer_attr = {}

    soup = offer_soup
    attr = soup.findAll("p")

    pattern = r'<p class=".*?">(.*?)</p>'
    pattern_type = r"<span>(.*?)</span>"

    for a in attr:
        match = re.search(pattern, str(a))

        if match:
            extracted_text = match.group(1)
            if (
                ":" in extracted_text
                and "Więcej od tego ogłoszeniodawcy" not in extracted_text
            ):
                try:
                    key, value = extracted_text.split(":")
                    offer_attr[key] = value.lstrip()
                except Exception as e:
                    print(e)
                    continue
            match_type = re.search(pattern_type, str(extracted_text))
            if match_type:
                extracted_text_type = match_type.group(1)
                if extracted_text_type in ["Firmowe", "Prywatne"]:
                    offer_attr["Typ"] = extracted_text_type
    return offer_attr


def get_price(offer_soup):
    """
    Get offer price from offer soup

    Parameters
    ----------
    offer_soup: BeautifulSoup
        Soup of offer

    Returns
    -------
    string
        Price of offer

    """
    soup = offer_soup
    attr = soup.findAll(price_header)
    pattern = rf'<{price_header} class=".*?">(.*?)</{price_header}>'

    for a in attr:
        match = re.search(pattern, str(a))
        if match:
            extracted_text = match.group(1)
            if "zł" in extracted_text:
                price = extracted_text
    return price


### Function not used as it doesn't bring value ###
# def get_description(offer_soup):
#     soup = offer_soup
#     for desc in soup.find_all("div", {"class": "css-bgzo2k er34gjf0"}):
#         description = (
#             str(desc)
#             .replace("<br>", "")
#             .replace("<br/>", "")
#             .replace('<div class="css-bgzo2k er34gjf0">', "")
#         )
#     return description


def get_posted_date(offer_soup):
    """
    Get offer post date from offer soup

    Parameters
    ----------
    offer_soup: BeautifulSoup
        Soup of offer

    Returns
    -------
    string
        Posted date of offer

    """
    soup = offer_soup
    for tag in soup.find_all("span", {"class": "css-19yf5ek"}):
        pattern = r'<span class=".*?" data-cy="ad-posted-at">(.*?)</span>'
        match = re.search(pattern, str(tag))
        if match:
            date_posted = match.group(1)
    return date_posted


def get_ad_title(offer_soup):
    """
    Get offer title from offer soup

    Parameters
    ----------
    offer_soup: BeautifulSoup
        Soup of offer

    Returns
    -------
    string
        Title of offer

    """
    for tag in offer_soup.find_all("h1", {"class": "css-bg3pmc"}):
        pattern = r'<h1 class=".*?" data-cy="ad_title">(.*?)</h1>'
        match = re.search(pattern, str(tag))
        if match:
            ad_title = match.group(1)
    return ad_title


def collect_ad_data(offer_soup):
    """
    Collect all offer data to single dictionary

    Parameters
    ----------
    offer_soup: BeautifulSoup
        Soup of offer

    Returns
    -------
    dict
        Dictionary of collected offer data

    """
    offer_attr = get_attributes(offer_soup)
    offer_attr["Cena"] = get_price(offer_soup)
    # offer_attr['Opis'] = get_description(offer_soup)
    offer_attr["Data opublikowania ogłoszenia"] = get_posted_date(offer_soup)
    offer_attr["Tytuł"] = get_ad_title(offer_soup)
    return offer_attr


def dict_to_df_merge(df, dictionary):
    """
    Transform dictionary to dataframe and merge with provided existing df

    Parameters
    ----------
    df: dataframe
        Empty df with headers or df with data from other offer
    dictionary: dict
        Dictionary with data from current offer

    Returns
    -------
    df
        Merged dataframe

    """
    df_toMerge = pd.DataFrame(dictionary, index=[1])
    df = pd.concat([df, df_toMerge], axis=0, ignore_index=True)

    return df


def main():
    """
    Go through offers collected in get_offers function and get data from each offer
    Save colected offers as csv file in data/stage directory with timestamp in the file name

    """
    columns = [
        "Tytuł",
        "Model telefonu",
        "Wbudowana pamięć",
        "Stan",
        "Cena",
        "Typ",
        "Kolor",
        "Data opublikowania ogłoszenia",
        "URL",
    ]
    df = pd.DataFrame(columns=columns)

    offers = get_offers(search_url)

    for offer in offers:
        try:
            offer_source = urllib.request.urlopen(offer).read()
            offer_soup = BeautifulSoup(offer_source, "html.parser")
            offer_attr = collect_ad_data(offer_soup)
            offer_attr["URL"] = offer
            df = dict_to_df_merge(df, offer_attr)

        except Exception as e:
            print(f"Error in offer URL: {offer} \n Error message: {e}")
            continue
        print(f"Collected data for offer: {offer}")
        sleep(2)

    now = datetime.datetime.now().strftime("%Y%m%d%H%M")
    file_title = f"data/stage/olx_iphone_{now}.csv"
    df.to_csv(file_title)
    print(f"Extracted {len(df)} rows")


if __name__ == "__main__":
    main()
