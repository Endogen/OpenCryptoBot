import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from telegram import ParseMode
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.decentralizedyet import DecentralizedYet
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Decentralized(OpenCryptoPlugin):

    def get_cmds(self):
        return ["de", "decentralized"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        if not args:
            if update.message:
                update.message.reply_text(
                    text=f"Usage:\n{self.get_usage()}",
                    parse_mode=ParseMode.MARKDOWN)
            return

        coin = args[0].upper()

        if RateLimit.limit_reached(update):
            return

        try:
            data = DecentralizedYet().coins()
        except Exception as e:
            return self.handle_error(e, update)

        if not data:
            update.message.reply_text(
                text=f"{emo.INFO} No data found",
                parse_mode=ParseMode.MARKDOWN)
            return

        msg = str()

        for c in data:
            if coin == c["symbol"]:
                name = c["name"]
                symbol = c["symbol"]
                notes = c["notes"] if "notes" in c else ""
                cons = c["consensus"] if "consensus" in c else ""
                nodes = c["public_nodes"] if "public_nodes" in c else ""
                incen = c["incentivized"] if "incentivized" in c else ""
                clients = c["client_codebases"] if "client_codebases" in c else ""

                msg = f"`Are We Decentralized Yet?`\n{msg}"
                msg += f"`{name} ({symbol})`\n\n"

                if notes:
                    notes = utl.esc_md(f"{notes}\n\n")
                    msg += f"`{notes}`"

                msg += f"`Consensus:    {cons}`\n"
                msg += f"`Public Nodes: {nodes}`\n"
                msg += f"`Incentivized: {incen}`\n"
                msg += f"`Clients:      {clients}`"

                break

        if not msg:
            msg = f"{emo.ERROR} Can't retrieve data for *{coin}*"

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`{self.get_cmds()[0]} <symbol>`"

    def get_description(self):
        return "Show decentralization info"

    def get_category(self):
        return Category.GENERAL
