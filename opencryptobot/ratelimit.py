import time
import logging

from opencryptobot.config import ConfigManager as Cfg


# TODO: How to best send msg to user if limit reached?
class RateLimit:

    _data = dict()

    @staticmethod
    def limit_reached(user_id, command):
        if not user_id or not command:
            return False

        now = int(time.time())

        rate_limit = Cfg.get("rate_limit")
        cmds = rate_limit.split("-")[0]
        time = rate_limit.split("-")[1]

        if command not in RateLimit._data:
            RateLimit._data[command] = dict()
        if user_id not in RateLimit._data[command]:
            RateLimit._data[command][user_id] = [1, now]
            return False

        count = RateLimit._data[command][user_id][0]
        start = RateLimit._data[command][user_id][1]

        if (start + time) > now:
            if count > cmds:
                logging.debug(f"User {user_id} reached rate limit at command '{command}'")
                return True
            else:
                RateLimit._data[command][user_id][0] += 1
                return False
        else:
            RateLimit._data[command][user_id] = [1, now]
            return False
