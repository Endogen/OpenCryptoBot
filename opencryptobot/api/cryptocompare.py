import json
import requests


class CryptoCompare(object):

    _base_url = 'https://min-api.cryptocompare.com/data/'

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

    def get_historical_ohlcv_daily(self, fsym, tsym, limit):
        url_data = f"histoday?fsym={fsym}&tsym={tsym}&limit={limit}"
        return self._request(f"{self._base_url}{url_data}")

    def get_historical_ohlcv_hourly(self, fsym, tsym, limit):
        url_data = f"histohour?fsym={fsym}&tsym={tsym}&limit={limit}"
        return self._request(f"{self._base_url}{url_data}")

    def get_historical_ohlcv_minute(self, fsym, tsym, limit):
        url_data = f"histominute?fsym={fsym}&tsym={tsym}&limit={limit}"
        return self._request(f"{self._base_url}{url_data}")

    def get_coin_general_info(self, fsyms, tsym):
        url_data = f"coin/generalinfo?fsyms={fsyms}&tsym={tsym}"
        return self._request(f"{self._base_url}{url_data}")
