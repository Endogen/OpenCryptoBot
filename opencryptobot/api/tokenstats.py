import requests


class TokenStats(object):

    _url = "https://tokenstats.io/api/v1/"

    response = None

    def __init__(self, url=None):
        if url:
            self._url = url

    def get_roi_for_symbol(self, symbol):
        url_data = f"roi?symbol={symbol}"
        self.response = requests.get(f"{self._url}{url_data}").json()
        return self.response

    def get_tokens(self, limit=999999):
        url_data = f"tokens?limit={limit}"
        self.response = requests.get(f"{self._url}{url_data}").json()
        return self.response
