import logging
import opencryptobot.emoji as emo

from opencryptobot.config import ConfigManager as Cfg


class RateLimit:

    _data = dict()

    @staticmethod
    def limit_reached(update):
        if Cfg.get("rate_limit", "enabled"):
            if update.message:
                uid = update.message.from_user.id
                cmd = update.message.text.split(" ")[0]
            elif update.inline_query:
                uid = update.effective_user.id
                cmd = update.inline_query.query[:-1].split(" ")[0]
            else:
                uid = cmd = None

            if not Cfg.get("rate_limit", "incl_cmd"):
                cmd = None

            rate = Cfg.get("rate_limit", "requests")
            time = Cfg.get("rate_limit", "timespan")

            if RateLimit.reached(uid, rate, time, command=cmd):
                msg = f"{emo.NO_ENTRY} Rate limit ({rate} requests in " \
                      f"{time} seconds) exceeded. Wait a few seconds..."

                update.message.reply_text(msg)
                return True
            return False
        else:
            return False

    @staticmethod
    def reached(user_id, rate, t, command=None):
        if not user_id:
            return False

        import time
        now = int(time.time())

        if command:
            # Rate limit per user & command
            if command not in RateLimit._data:
                RateLimit._data[command] = dict()
            if user_id not in RateLimit._data[command]:
                RateLimit._data[command][user_id] = [1, now]
                return False

            count = RateLimit._data[command][user_id][0]
            start = RateLimit._data[command][user_id][1]

            if (start + int(t)) > now:
                if count == int(rate):
                    logging.debug(f"User {user_id} reached rate "
                                  f"limit at command '{command}'")
                    return True
                else:
                    RateLimit._data[command][user_id][0] += 1
                    return False
            else:
                RateLimit._data[command][user_id] = [1, now]
                return False
        else:
            # Rate limit per user
            if user_id not in RateLimit._data:
                RateLimit._data[user_id] = [1, now]
                return False

            count = RateLimit._data[user_id][0]
            start = RateLimit._data[user_id][1]

            if (start + int(t)) > now:
                if count == int(rate):
                    logging.debug(f"User {user_id} reached rate limit")
                    return True
                else:
                    RateLimit._data[user_id][0] += 1
                    return False
            else:
                RateLimit._data[user_id] = [1, now]
                return False

