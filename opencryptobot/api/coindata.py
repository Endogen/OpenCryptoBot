import time
import requests


class CoinData(object):

    _url = "https://coindata.co.za/api.php"

    _response = None
    _datetime = 0

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
                CoinData._response = requests.get(self._url).json()
            except Exception:
                return None

            if not CoinData._response:
                return None

            # Filter out 'null' values
            CoinData._response = [d for d in CoinData._response if all(d.values())]

        data = list()
        temp = list()

        if volume:
            # Sort data by volume
            temp = sorted(
                CoinData._response,
                key=lambda k: float(k["Volume_24h"]), reverse=True)

            for entry in temp:
                if int(float(entry["Volume_24h"])) > volume:
                    data.append(entry)
                else:
                    break
        else:
            data = CoinData._response

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
