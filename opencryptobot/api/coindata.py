import json
import time
import requests


class CoinData(object):

    _url = "https://coindata.co.za/api.php"
    _datetime = 0

    response = None
    res_json = None

    BEST = "BEST"
    WORST = "WORST"

    HOUR = "HOUR"
    DAY = "DAY"

    def __init__(self, url=None):
        if url:
            self._url = url

    def get_movers(self, move, period=HOUR, entries=10, volume=None):
        # Current datetime in seconds
        now = int(time.time())

        # Check if last API call longer then 2 min ago
        if (now - 120) > CoinData._datetime:
            CoinData._datetime = now

            try:
                CoinData.response = requests.get(self._url)
                CoinData.response.raise_for_status()
                CoinData.res_json = json.loads(CoinData.response.content.decode('utf-8'))
            except Exception as e:
                raise e

            if not CoinData.res_json:
                raise ValueError("No response data available")

            # Filter out 'null' values
            CoinData.res_json = [d for d in CoinData.res_json if all(d.values())]

        data = list()

        if volume:
            # Sort data by volume
            temp = sorted(
                CoinData.res_json,
                key=lambda k: float(k["Volume_24h"]), reverse=True)

            for entry in temp:
                if int(float(entry["Volume_24h"])) > volume:
                    data.append(entry)
                else:
                    break
        else:
            data = CoinData.res_json

        if period == self.HOUR:
            # Sort data period - 1 hour
            data = sorted(
                data,
                key=lambda k: float(k["Change_1h"]), reverse=True)
        elif period == self.DAY:
            # Sort data period - 1 day
            data = sorted(
                data,
                key=lambda k: float(k["Change_24h"]), reverse=True)
        else:
            return None

        result = list()

        count = 0
        if move == self.BEST:
            for entry in data:
                if count == entries:
                    break
                result.append(entry)
                count += 1
        elif move == self.WORST:
            for entry in reversed(data):
                if count == entries:
                    break
                result.append(entry)
                count += 1
        else:
            return None

        return result
