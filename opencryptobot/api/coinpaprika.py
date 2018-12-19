import requests


class CoinPaprika(object):

    _base_url = 'https://api.coinpaprika.com/v1/'
    response = None

    def __init__(self, base_url=None):
        if base_url:
            self._base_url = base_url

    def get_list_coins(self):
        url_data = "coins"
        self.response = requests.get(f"{self._base_url}{url_data}").json()
        return self.response

    def get_coin_by_id(self, coin_id):
        url_data = f"coins/{coin_id}"
        self.response = requests.get(f"{self._base_url}{url_data}").json()
        return self.response

    def get_historical_ohlc(self, coin_id, start, **kwargs):
        url_data = f"coins/{coin_id}/ohlcv/historical?start={start}"

        for key, value in kwargs.items():
            url_data += f"&{key}={value}"

        self.response = requests.get(f"{self._base_url}{url_data}").json()
        return self.response

    def get_global(self):
        url_data = "global"
        self.response = requests.get(f"{self._base_url}{url_data}").json()
        return self.response
