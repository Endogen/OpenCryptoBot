import json
import logging
import requests


class CryptoPanic(object):

    _base_url = 'https://cryptopanic.com/api/posts/'
    _token = None

    response = None

    def __init__(self, base_url=None, token=None):
        if base_url:
            self._base_url = base_url
        if token:
            self._token = token

    def _request(self, url):
        try:
            self.response = requests.get(url)
            self.response.raise_for_status()
            return json.loads(self.response.content.decode('utf-8'))
        except Exception as e:
            raise e

    def load_key(self, path):
        with open(path, 'r') as f:
            self._token = f.readline().strip()

    def get_posts(self):
        """Posts"""

        url_data = f"?auth_token={self._token}"
        return self._request(f"{self._base_url}{url_data}")

    def get_filtered_news(self, filter):
        """You can use any UI filter using filter=(rising|hot|bullish|bearish|important|saved|lol)"""

        url_data = f"?auth_token={self._token}&filter={filter}"
        return self._request(f"{self._base_url}{url_data}")

    def get_currency_news(self, currencies):
        """Filter by currencies using currencies=SYMBOL1,SYMBOL2 (max 50)"""

        url_data = f"?auth_token={self._token}&currencies={currencies}"
        return self._request(f"{self._base_url}{url_data}")

    def get_region_news(self, regions):
        """Filter by region using regions=REGION_CODE1,REGION_CODE2. Default: en"""
        """Available: en, de, es, fr, it, pt, ru"""

        url_data = f"?auth_token={self._token}&regions={regions}"
        return self._request(f"{self._base_url}{url_data}")

    def get_multiple_filters(self, currencies, filter):
        """You can also combine multiple filters together: currencies and filter"""

        url_data = f"?auth_token={self._token}&currencies={currencies}&filter={filter}"
        return self._request(f"{self._base_url}{url_data}")

    def _handle_error(self, ex):
        logging.error(repr(ex))
        logging.error(f"Request URL: {self.response.url}")
        logging.error(f"Response Status Code: {self.response.status_code}")
        return None
