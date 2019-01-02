import json
import logging
import requests


class TokenStats(object):

    _base_url = "https://tokenstats.io/api/v1/"

    response = None

    def __init__(self, url=None):
        if url:
            self._base_url = url

    def _request(self, url):
        try:
            self.response = requests.get(url)
            self.response.raise_for_status()
            return json.loads(self.response.content.decode('utf-8'))
        except Exception as e:
            return self._handle_error(e)

    def get_roi_for_symbol(self, symbol):
        url_data = f"roi?symbol={symbol}"
        return self._request(f"{self._base_url}{url_data}")

    def get_tokens(self, limit=999999):
        url_data = f"tokens?limit={limit}"
        return self._request(f"{self._base_url}{url_data}")

    def _handle_error(self, ex):
        logging.error(repr(ex))
        logging.error(f"Request URL: {self.response.url}")
        logging.error(f"Response Status Code: {self.response.status_code}")
        return None
