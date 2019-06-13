import os
import json
import logging
import opencryptobot.emoji as emo
import opencryptobot.utils as utl
import opencryptobot.constants as con

from telegram import ParseMode
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.cryptocompare import CryptoCompare
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Wallets(OpenCryptoPlugin):

    _CC_URL = "https://www.cryptocompare.com"
    _token = None

    def __init__(self, telegram_bot):
        super().__init__(telegram_bot)

        token_path = os.path.join(con.CFG_DIR, con.TKN_FILE)

        try:
            if os.path.isfile(token_path):
                with open(token_path, 'r') as file:
                    self._token = json.load(file)["crypto-compare"]
            else:
                logging.error(f"No token file '{con.TKN_FILE}' found at '{token_path}'")
        except KeyError as e:
            cls_name = f"Class: {type(self).__name__}"
            logging.error(f"{repr(e)} - {cls_name}")

    def get_cmds(self):
        return ["wa", "wallet"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        if not args:
            if update.message:
                update.message.reply_text(
                    text=f"Usage:\n{self.get_usage()}",
                    parse_mode=ParseMode.MARKDOWN)
            return

        if RateLimit.limit_reached(update):
            return

        coins = utl.get_kw(args, "coins")

        try:
            cp = CryptoCompare(token=self._token)
            wallets = cp.get_wallet_info()
        except Exception as e:
            return self.handle_error(e, update)

        if wallets["Response"] == "Error":
            if update.message:
                update.message.reply_text(
                    text=f"{emo.ERROR} {wallets['Message']}",
                    parse_mode=ParseMode.MARKDOWN)
            return

        found = False

        # Return wallets for specified coin(s)
        if coins:
            coin_list = coins.split(",")

            for _, wa in wallets["Data"].items():
                if all(x.strip().upper() in wa["Coins"] for x in coin_list):
                    update.message.reply_text(
                        text=self._get_msg(wa),
                        parse_mode=ParseMode.MARKDOWN)

                    found = True

        # Return info about specified wallet(s)
        else:
            wallet = " ".join(args)

            for _, wa in wallets["Data"].items():
                if wallet.upper() in wa["Name"].upper():
                    update.message.reply_text(
                        text=self._get_msg(wa),
                        parse_mode=ParseMode.MARKDOWN)

                    found = True

        if not found:
            update.message.reply_text(
                text=f"{emo.INFO} No wallet found",
                parse_mode=ParseMode.MARKDOWN)

    def _get_msg(self, wallet_data):
        name = wallet_data["Name"]
        logo = utl.esc_md(wallet_data["LogoUrl"])
        sec = wallet_data["Security"]
        anon = wallet_data["Anonymity"]
        usage = wallet_data["EaseOfUse"]
        features = wallet_data["WalletFeatures"]
        coins = wallet_data["Coins"]
        platforms = wallet_data["Platforms"]
        src_url = utl.esc_md(wallet_data["SourceCodeUrl"])
        validation = wallet_data["ValidationType"]
        trading = wallet_data["HasTradingFacilities"]
        website = utl.esc_md(wallet_data["AffiliateURL"])
        rating = wallet_data["Rating"]["Avg"]
        users = wallet_data["Rating"]["TotalUsers"]

        ftr = "?" if not features else features
        src = f"`\n\nSource Code:\n`{src_url}" if src_url else ""

        return f"[{name}]({self._CC_URL}{logo})\n\n" \
               f"`Rating:     {rating} ({users} Users)\n`" \
               f"`Security:   {sec}\n`" \
               f"`Anonymity:  {anon}\n`" \
               f"`EaseOfUse:  {usage}\n`" \
               f"`Trading:    {utl.bool2str(trading)}\n`" \
               f"`Validation: {validation}\n\n`" \
               f"`Features:\n{', '.join(ftr)}\n\n`" \
               f"`Supported Coins:\n{', '.join(sorted(coins))}\n\n`" \
               f"`Platforms:\n{', '.join(platforms)}\n\n`" \
               f"`Website:\n`{website}" \
               f"{src}"

    def get_usage(self):
        return f"`{self.get_cmds()[0]} <wallet name> | coins=<symbol>(,<symbol>,[...])\n\n`"

    def get_description(self):
        return "Details about wallets"

    def get_category(self):
        return Category.UTILS
