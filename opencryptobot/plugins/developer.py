import opencryptobot.emoji as emo

from telegram import ParseMode
from opencryptobot.api.apicache import APICache
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Developer(OpenCryptoPlugin):

    def get_cmd(self):
        return "dev"

    @OpenCryptoPlugin.send_typing
    @OpenCryptoPlugin.save_data
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        coin = args[0].upper()
        msg = str()

        for entry in APICache.get_cg_coins_list():
            if entry["symbol"].lower() == coin.lower():
                data = CoinGecko().get_coin_by_id(entry["id"])

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
            msg = f"{emo.ERROR} No developer data found for *{coin}*"

        update.message.reply_text(
            text=msg.replace("Pull Request", "PR"),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True)

    def get_usage(self):
        return f"`/{self.get_cmd()} <coin>`"

    def get_description(self):
        return "Development information"

    def get_category(self):
        return Category.GENERAL
