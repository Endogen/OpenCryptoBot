import requests


class CryptoCompare(object):

    _base_url = 'https://min-api.cryptocompare.com/data/'
    response = None

    def __init__(self, base_url=None):
        if base_url:
            self._base_url = base_url

    def historical_ohlcv_hourly(self, fsym, tsym, limit):
        url_data = f"histohour?fsym={fsym}&tsym={tsym}&limit={limit}"
        self.response = requests.get(f"{self._base_url}{url_data}").json()
        return self.response
