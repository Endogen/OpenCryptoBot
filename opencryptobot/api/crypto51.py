import json
import requests


class Crypto51(object):

    _base_url = 'https://www.crypto51.app/coins.json'

    response = None

    def coins(self):
        try:
            self.response = requests.get(self._base_url)
            self.response.raise_for_status()
            return json.loads(self.response.content.decode('utf-8'))
        except Exception as e:
            raise e
