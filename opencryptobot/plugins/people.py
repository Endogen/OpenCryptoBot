import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from telegram import ParseMode
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.apicache import APICache
from opencryptobot.api.coinpaprika import CoinPaprika
from opencryptobot.plugin import OpenCryptoPlugin, Category


class People(OpenCryptoPlugin):

    def get_cmd(self):
        return "pe"

    def get_cmd_alt(self):
        return ["people"]

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

        if len(args) > 1:
            name = "-".join(args).lower()
        else:
            name = args[0]

        name_clean = name.replace('-', " ").title()
        msg = str()

        d = CoinPaprika().get_people_by_id(name)

        if "description" in d and d["description"]:
            msg = f"`{d['description']}`\n\n"

        if "links" in d and d["links"]:
            for k, v in d["links"].items():
                url = v[0]["url"]
                fol = v[0]["followers"] if "followers" in v[0] else None

                fol_str = f"({fol} Followers)" if fol else ""
                msg += f"`{k.title()} {fol_str}`\n{utl.esc_md(url)}\n"

        if "positions" in d and d["positions"]:
            msg += "\n`Positions:`\n" if msg else "`Positions:`\n"

            for pos in d["positions"]:
                msg += f"`{pos['coin_symbol']} - {pos['position']}`\n"

        if not msg:
            update.message.reply_text(
                text=f"{emo.ERROR} No person with name *'{name_clean}'* found",
                parse_mode=ParseMode.MARKDOWN)
            return

        msg = f"`{name_clean}`\n\n{msg}"

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True)

    def get_usage(self):
        return f"`/{self.get_cmd()} <name of person>`"

    def get_description(self):
        return "Info about person from a team"

    def get_category(self):
        return Category.GENERAL
