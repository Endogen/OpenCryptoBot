import requests

from bs4 import BeautifulSoup

COIN_PAPRIKA_PARTIAL = "https://coinpaprika.com/coin/"
CMC_URL_PARTIAL = "https://coinmarketcap.com/currencies/"
ALL_CRYPTO_WP_PARTIAL = "https://www.allcryptowhitepapers.com/"


def get_wp_allcryptowhitepaper(name):
    url = f"{ALL_CRYPTO_WP_PARTIAL}{name}-Whitepaper"
    response = requests.get(url)
    response.raise_for_status()

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    for entry_content in soup.find_all(class_="entry-content"):
        for p in entry_content.find_all("p"):
            for a in p.find_all("a"):
                if "".join(a.get_text().split()) == f"{name}Whitepaper":
                    return a["href"]


def get_wp_coinmarketcap(slug):
    url = f"{CMC_URL_PARTIAL}{slug}"
    response = requests.get(url)
    response.raise_for_status()

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    for links in soup.find_all(class_="list-unstyled details-panel-item--links"):
        for li in links.find_all("li"):
            if li.find_all(class_="glyphicons glyphicons-file details-list-item-icon"):
                for a in li.find_all("a"):
                    return a["href"]


def get_wp_coinpaprika(coin_id):
    url = f"{COIN_PAPRIKA_PARTIAL}{coin_id}"
    response = requests.get(url)
    response.raise_for_status()

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    for link in soup.find_all(class_="cp-details__whitepaper-link"):
        return link["href"]
