import opencryptobot.utils as utl

from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Events(OpenCryptoPlugin):

    def get_cmds(self):
        return ["ev", "events"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        if RateLimit.limit_reached(update):
            return

        try:
            events = CoinGecko().get_events(**utl.get_keywords(args))
        except Exception as e:
            return self.handle_error(e, update)

        msg = str()
        for i in range(10):
            event = events["data"][i]

            title = event["title"]
            event_type = event["type"]
            description = event["description"]
            organizer = event["organizer"]
            from_date = event["start_date"]
            to_date = event["end_date"]
            address = event["address"]
            city = event["city"]
            country = event["country"]
            website = event["website"]

            msg += f"*{title}\n*" \
                   f"{event_type} by {organizer}\n\n" \
                   f"{description}\n\n" \
                   f"From {from_date} to {to_date}\n\n" \
                   f"*Location*\n{city}\n{address}\n{country}\n\n" \
                   f"Link\n{website}\n\n"

            update.message.reply_text(msg)

    def get_usage(self):
        # TODO: Add all possible keywords
        return f"`/{self.get_cmds()[0]} (country=<country code> type=<type> limit=<# of events>)`"

    def get_description(self):
        return "Show events for a coin"

    def get_category(self):
        return Category.NEWS

