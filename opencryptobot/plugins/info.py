import threading
import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from telegram import ParseMode
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.tokenstats import TokenStats
from opencryptobot.api.cryptocompare import CryptoCompare
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Info(OpenCryptoPlugin):

    LOGO_URL_PARTIAL = "https://www.cryptocompare.com"

    coin_type = None
    based_on = None

    def get_cmd(self):
        return "i"

    def get_cmd_alt(self):
        return ["info"]

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

        try:
            type_thread = threading.Thread(target=self._get_coin_type, args=[coin])
            type_thread.start()

            coin_info = CryptoCompare().get_coin_general_info(coin, "USD")
        except Exception as e:
            self.handle_api_error(e, update)
            return

        if coin_info["Message"] != "Success" or not coin_info["Data"]:
            update.message.reply_text(
                text=f"{emo.ERROR} No data for *{coin}*",
                parse_mode=ParseMode.MARKDOWN)
            return

        name = coin_info["Data"][0]["CoinInfo"]["FullName"]
        image = f"{self.LOGO_URL_PARTIAL}{coin_info['Data'][0]['CoinInfo']['ImageUrl']}"
        algo = coin_info["Data"][0]["CoinInfo"]["Algorithm"]
        proof = coin_info["Data"][0]["CoinInfo"]["ProofType"]
        h_per_s = coin_info["Data"][0]["CoinInfo"]["NetHashesPerSecond"]
        block = coin_info["Data"][0]["CoinInfo"]["BlockNumber"]
        block_time = coin_info["Data"][0]["CoinInfo"]["BlockTime"]
        block_reward = coin_info["Data"][0]["CoinInfo"]["BlockReward"]

        type_thread.join()

        type = str("-")
        if self.coin_type:
            type = f"{self.coin_type}"
            if self.based_on:
                type += f" ({self.based_on})"

        update.message.reply_photo(
            photo=image,
            caption=f"`"
                    f"Name:         {name}\n"
                    f"Ticker:       {coin}\n"
                    f"Type:         {type}\n"
                    f"Algorithm:    {algo}\n"
                    f"Proof type:   {proof}\n"
                    f"Hashes (sec): {utl.format(int(h_per_s))}\n"
                    f"Block:        {block}\n"
                    f"Block time:   {block_time}\n"
                    f"Block reward: {block_reward}"
                    f"`",
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmd()} <coin>`"

    def get_description(self):
        return "General coin information"

    def get_category(self):
        return Category.GENERAL

    def _get_coin_type(self, coin):
        res = TokenStats().get_roi_for_symbol(coin)
        if res:
            if res["type"]:
                if res["type"] == "coin":
                    self.coin_type = "Coin"
                    self.based_on = None
                else:
                    self.coin_type = "Token"
                    self.based_on = res["type"].capitalize()
