import opencryptobot.utils as utl

from telegram import ParseMode
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Events(OpenCryptoPlugin):

    def get_cmds(self):
        return ["ev", "events"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        kw = utl.get_kw(args)

        limit = kw.get("limit", 5)
        kw.pop("limit", None)

        if RateLimit.limit_reached(update):
            return

        try:
            events = CoinGecko().get_events(**kw)
        except Exception as e:
            return self.handle_error(e, update)

        for i in range(int(limit)):
            if len(events["data"]) <= i:
                break

            event = events["data"][i]

            title = event["title"]
            event_type = event["type"]
            description = event["description"]
            organizer = event["organizer"]
            from_date = event["start_date"]
            to_date = event["end_date"]
            address = event["address"].strip()
            city = event["city"].strip()
            country = event["country"].strip()
            website = event["website"]

            org = f" by {organizer}" if organizer else ""

            msg = f"[{title}]({website})\n" \
                  f"{event_type}{org}\n\n" \
                  f"{utl.esc_md(description)}\n\n" \
                  f"*Date*\nStart {from_date}\nEnd   {to_date}\n\n" \
                  f"*Location*\n{address}\n{city}\n{country}\n\n"

            update.message.reply_text(text=msg, parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} (limit=<# of events>) (country_code=DE|US|...) " \
               f"(type=Event|Conference|Meetup) (from_date=<date>) (to_date=<date>)`"

    def get_description(self):
        return "Show crypto events"

    def get_category(self):
        return Category.NEWS

