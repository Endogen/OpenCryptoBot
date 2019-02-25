import opencryptobot.emoji as emo

from telegram import ParseMode
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.apicache import APICache
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Developer(OpenCryptoPlugin):

    def get_cmds(self):
        return ["dev", "developer"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        if RateLimit.limit_reached(update):
            return

        coin = args[0].upper()
        msg = str()

        try:
            response = APICache.get_cg_coins_list()
        except Exception as e:
            return self.handle_error(e, update)

        for entry in response:
            if entry["symbol"].lower() == coin.lower():
                try:
                    data = CoinGecko().get_coin_by_id(entry["id"])
                except Exception as e:
                    return self.handle_error(e, update)

                dev_data = data["developer_data"]

                for k, v in dev_data.items():
                    msg += f"`{k.title().replace('_', ' ')}: {str(v)}`\n"

                gh_links = data["links"]["repos_url"]["github"]

                if not gh_links:
                    break

                msg += "\n`GitHub links:`\n"

                for link in gh_links:
                    title_index = link.rfind("/")
                    msg += f"[{link[title_index+1:len(link)]}]({link})\n"

                break

        if msg:
            msg = f"`GitHub info for {coin}`\n\n" + msg
        else:
            msg = f"{emo.INFO} No developer data found for *{coin}*"

        update.message.reply_text(
            text=msg.replace("Pull Request", "PR"),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <symbol>`"

    def get_description(self):
        return "Development information"

    def get_category(self):
        return Category.GENERAL
