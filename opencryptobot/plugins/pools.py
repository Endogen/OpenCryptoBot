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


class Pools(OpenCryptoPlugin):

    _TW_URL = "https://twitter.com/"
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
        return ["po", "pool"]

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

        try:
            cp = CryptoCompare(token=self._token)
            pools = cp.get_pool_info()
        except Exception as e:
            return self.handle_error(e, update)

        if pools["Response"] == "Error":
            if update.message:
                update.message.reply_text(
                    text=f"{emo.ERROR} {pools['Message']}",
                    parse_mode=ParseMode.MARKDOWN)
            return

        found = False

        coins = utl.get_kw(args, "coins")

        # Return pools for specified coin(s)
        if coins:
            coin_list = coins.split(",")

            for _, po in pools["Data"].items():
                if all(x.strip().upper() in po["Coins"] for x in coin_list):
                    update.message.reply_text(
                        text=self._get_msg(po),
                        parse_mode=ParseMode.MARKDOWN)

                    found = True

        # Return info about specified pool(s)
        else:
            pool = " ".join(args)

            for _, po in pools["Data"].items():
                if pool.upper() in po["Name"].upper():
                    update.message.reply_text(
                        text=self._get_msg(po),
                        parse_mode=ParseMode.MARKDOWN)

                    found = True

        if not found:
            update.message.reply_text(
                text=f"{emo.INFO} No mining pool found",
                parse_mode=ParseMode.MARKDOWN)

    def _get_msg(self, wallet_data):
        name = wallet_data["Name"]
        logo = utl.esc_md(wallet_data["LogoUrl"])
        rating = wallet_data["Rating"]["Avg"]
        users = wallet_data["Rating"]["TotalUsers"]
        avg_fee = wallet_data["AverageFee"]
        exp_fee = wallet_data["FeeExpanded"]
        shared_fee = wallet_data["TxFeeSharedWithMiner"]
        payout = wallet_data["MinimumPayout"]
        merge = wallet_data["MergedMining"]
        mrg_min = wallet_data["MergedMiningCoins"]
        features = wallet_data["PoolFeatures"]
        coins = wallet_data["Coins"]
        locations = wallet_data["ServerLocations"]
        payment = wallet_data["PaymentType"]
        website = utl.esc_md(wallet_data["AffiliateURL"])
        twitter = utl.esc_md(wallet_data["Twitter"])

        exp_fee = "?" if not exp_fee else exp_fee.replace("; ", "\n")
        payout = "?" if not payout else payout.replace("; ", "\n")
        ftr = "?" if not features else features
        mrg_min = "" if not merge else f"`Merge Mining Coins:\n{', '.join(mrg_min)}\n\n`"
        mrg_min = mrg_min.replace(", ", "\n")

        return f"[{name}]({self._CC_URL}{logo})\n\n" \
               f"`Rating: {rating} ({users} Users)\n\n`" \
               f"`Features:\n{', '.join(ftr)}\n\n`" \
               f"`Supported Coins:\n{', '.join(sorted(coins))}\n\n`" \
               f"`Server Locations:\n{', '.join(locations)}\n\n`" \
               f"`Payment Type:\n{', '.join(payment)}\n\n`" \
               f"`Min. Payout:\n{payout}\n\n`" \
               f"`Shared Tx Fee: {shared_fee}\n`" \
               f"`Average Fee: {avg_fee}\n\n`" \
               f"`Fee Expanded:\n{exp_fee}\n\n`" \
               f"{mrg_min}" \
               f"`Website:\n`{website}\n\n" \
               f"`Twitter:\n`{self._TW_URL}{twitter[1:]}"

    def get_usage(self):
        return f"`{self.get_cmds()[0]} <pool name> | coins=<symbol>(,<symbol>,[...])\n\n`"

    def get_description(self):
        return "Info about mining pools"

    def get_category(self):
        return Category.UTILS
