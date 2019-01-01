import logging
import requests


class TokenStats(object):

    _url = "https://tokenstats.io/api/v1/"

    response = None

    def __init__(self, url=None):
        if url:
            self._url = url

    def get_roi_for_symbol(self, symbol):
        try:
            url_data = f"roi?symbol={symbol}"
            self.response = requests.get(f"{self._url}{url_data}")
            self.response.raise_for_status()
            return self.response.json()
        except Exception as ex:
            return self._handle_error(ex)

    def get_tokens(self, limit=999999):
        try:
            url_data = f"tokens?limit={limit}"
            self.response = requests.get(f"{self._url}{url_data}")
            self.response.raise_for_status()
            return self.response.json()
        except Exception as ex:
            return self._handle_error(ex)

    def _handle_error(self, ex):
        logging.error(repr(ex))
        logging.error(f"Request URL: {self.response.url}")
        logging.error(f"Response Status Code: {self.response.status_code}")
        return None
