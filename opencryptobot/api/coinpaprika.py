import json
import requests


class CoinPaprika(object):

    _base_url = 'https://api.coinpaprika.com/v1/'

    response = None

    def __init__(self, base_url=None):
        if base_url:
            self._base_url = base_url

    def _request(self, url):
        try:
            self.response = requests.get(url)
            self.response.raise_for_status()
            return json.loads(self.response.content.decode('utf-8'))
        except Exception as e:
            raise e

    def get_list_coins(self):
        url_data = "coins"
        return self._request(f"{self._base_url}{url_data}")

    def get_coin_by_id(self, coin_id):
        url_data = f"coins/{coin_id}"
        return self._request(f"{self._base_url}{url_data}")

    def get_historical_ohlc(self, coin_id, start, **kwargs):
        url_data = f"coins/{coin_id}/ohlcv/historical?start={start}"

        for key, value in kwargs.items():
            url_data += f"&{key}={value}"

        return self._request(f"{self._base_url}{url_data}")

    def get_global(self):
        url_data = "global"
        return self._request(f"{self._base_url}{url_data}")

    def get_people_by_id(self, person_id):
        url_data = f"people/{person_id}"
        return self._request(f"{self._base_url}{url_data}")
