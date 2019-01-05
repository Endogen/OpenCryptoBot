import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from telegram import ParseMode
from opencryptobot.api.apicache import APICache
from opencryptobot.api.coinpaprika import CoinPaprika
from opencryptobot.plugin import OpenCryptoPlugin, Category


class People(OpenCryptoPlugin):

    def get_cmd(self):
        return "pe"

    @OpenCryptoPlugin.send_typing
    @OpenCryptoPlugin.save_data
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        if len(args) > 1:
            update.message.reply_text(
                text=f"{emo.ERROR} Only one argument allowed",
                parse_mode=ParseMode.MARKDOWN)
            return

        msg = str()
        keyword = "details"
        kw_dict = utl.get_keywords(args)

        if kw_dict:
            if keyword in kw_dict:
                d = CoinPaprika().get_people_by_id(kw_dict[keyword])

                if "description" in d and d["description"]:
                    msg = f"`{d['description']}`\n\n"

                if "links" in d and d["links"]:
                    for k, v in d["links"].items():
                        url = v[0]["url"]
                        fol = v[0]["followers"] if "followers" in v[0] else None

                        fol_str = f"({fol} Followers)" if fol else ""
                        msg += f"`{k.title()} {fol_str}`\n{url}\n"

                if "positions" in d and d["positions"]:
                    msg += "\n`Positions:`\n" if msg else "`Positions:`\n"

                    for pos in d["positions"]:
                        msg += f"`{pos['coin_symbol']} - {pos['position']}`\n"

                if not msg:
                    update.message.reply_text(
                        text=f"{emo.ERROR} No details for *'{kw_dict[keyword]}'*",
                        parse_mode=ParseMode.MARKDOWN)
                    return

                name = kw_dict[keyword].replace('-', " ").title()
                msg = f"`{name}`\n\n{msg}"
            else:
                update.message.reply_text(
                    text=f"{emo.ERROR} Only keyword *'{keyword}'* is allowed",
                    parse_mode=ParseMode.MARKDOWN)
                return
        else:
            coin = args[0].upper()

            for c in APICache.get_cp_coin_list():
                if c["symbol"] == coin:
                    for p in CoinPaprika().get_coin_by_id(c["id"])["team"]:
                        details = f"/pe details={p['id']}"
                        msg += f"{p['name']}\n{p['position']}\n{details}\n\n"
                    break

            if not msg:
                update.message.reply_text(
                    text=f"{emo.ERROR} No team data for *{coin}*",
                    parse_mode=ParseMode.MARKDOWN)
                return

            msg = f"`Team behind {coin}\n\n{msg}`"

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True)

    def get_usage(self):
        return f"`/{self.get_cmd()} <coin>`"

    def get_description(self):
        return "Info about team behind a coin"

    def get_category(self):
        return Category.GENERAL
