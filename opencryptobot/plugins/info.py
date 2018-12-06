import opencryptobot.emoji as emo
import opencryptobot.constants as con

from telegram import ParseMode
from opencryptobot.plugin import OpenCryptoPlugin
from opencryptobot.api.cryptocompare import CryptoCompare


class Info(OpenCryptoPlugin):

    def get_cmd(self):
        return "i"

    @OpenCryptoPlugin.send_typing
    @OpenCryptoPlugin.save_data
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        coin = args[0].upper()

        coin_info = CryptoCompare().coin_general_info(coin, "USD")

        if coin_info["Message"] != "Success":
            update.message.reply_text(
                text=f"{emo.ERROR} No data for *{coin}*",
                parse_mode=ParseMode.MARKDOWN)
            return

        name = coin_info["Data"][0]["CoinInfo"]["FullName"]
        image = f"{con.CG_LOGO_URL_PARTIAL}{coin_info['Data'][0]['CoinInfo']['ImageUrl']}"
        algo = coin_info["Data"][0]["CoinInfo"]["Algorithm"]
        proof = coin_info["Data"][0]["CoinInfo"]["ProofType"]
        h_per_s = coin_info["Data"][0]["CoinInfo"]["NetHashesPerSecond"]
        block = coin_info["Data"][0]["CoinInfo"]["BlockNumber"]
        block_time = coin_info["Data"][0]["CoinInfo"]["BlockTime"]
        block_reward = coin_info["Data"][0]["CoinInfo"]["BlockReward"]

        update.message.reply_photo(
            photo=image,
            caption=f"`"
                    f"Name:            {name} ({coin})\n"
                    f"Algorithm:       {algo}\n"
                    f"Proof type:      {proof}\n"
                    f"Hashes (sec):    {int(h_per_s)}\n"
                    f"Block (current): {block}\n"
                    f"Block time:      {block_time}\n"
                    f"Block reward:    {block_reward}"
                    f"`",
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmd()} <coin>`"

    def get_description(self):
        return "General coin information"
