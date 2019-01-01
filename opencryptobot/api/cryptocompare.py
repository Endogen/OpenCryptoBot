import logging
import requests


class CryptoCompare(object):

    _base_url = 'https://min-api.cryptocompare.com/data/'
    response = None

    def __init__(self, base_url=None):
        if base_url:
            self._base_url = base_url

    def get_historical_ohlcv_daily(self, fsym, tsym, limit):
        try:
            url_data = f"histoday?fsym={fsym}&tsym={tsym}&limit={limit}"
            self.response = requests.get(f"{self._base_url}{url_data}")
            self.response.raise_for_status()
            return self.response.json()
        except Exception as ex:
            return self._handle_error(ex)

    def get_historical_ohlcv_hourly(self, fsym, tsym, limit):
        try:
            url_data = f"histohour?fsym={fsym}&tsym={tsym}&limit={limit}"
            self.response = requests.get(f"{self._base_url}{url_data}")
            self.response.raise_for_status()
            return self.response.json()
        except Exception as ex:
            return self._handle_error(ex)

    def get_historical_ohlcv_minute(self, fsym, tsym, limit):
        try:
            url_data = f"histominute?fsym={fsym}&tsym={tsym}&limit={limit}"
            self.response = requests.get(f"{self._base_url}{url_data}")
            self.response.raise_for_status()
            return self.response.json()
        except Exception as ex:
            return self._handle_error(ex)

    def get_coin_general_info(self, fsyms, tsym):
        try:
            url_data = f"coin/generalinfo?fsyms={fsyms}&tsym={tsym}"
            self.response = requests.get(f"{self._base_url}{url_data}")
            self.response.raise_for_status()
            return self.response.json()
        except Exception as ex:
            return self._handle_error(ex)

    def _handle_error(self, ex):
        logging.error(repr(ex))
        logging.error(f"Request URL: {self.response.url}")
        logging.error(f"Response Status Code: {self.response.status_code}")
        return None
