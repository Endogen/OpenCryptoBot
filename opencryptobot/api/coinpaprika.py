import requests


class CoinPaprika(object):

    _base_url = 'https://api.coinpaprika.com/v1/coins/'
    response = None

    def __init__(self, base_url=None):
        if base_url:
            self._base_url = base_url

    def list_coins(self):
        self.response = requests.get(self._base_url).json()
        return self.response
