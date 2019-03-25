import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from telegram import ParseMode
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.apicache import APICache
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Ico(OpenCryptoPlugin):

    def get_cmds(self):
        return ["ico"]

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

                if "ico_data" not in data:
                    break

                if data["ico_data"]["ico_start_date"]:
                    ico_start = data["ico_data"]["ico_start_date"][:10]
                else:
                    ico_start = "None"

                if data["ico_data"]["ico_end_date"]:
                    ico_end = data["ico_data"]["ico_end_date"][:10]
                else:
                    ico_end = "None"

                raised = data["ico_data"]["total_raised"]
                raised_cur = data["ico_data"]["total_raised_currency"]

                pre_sale_c = data["ico_data"]["quote_pre_sale_currency"]
                pre_sale_a = data["ico_data"]["base_pre_sale_amount"]
                pre_sale_p = data["ico_data"]["quote_pre_sale_amount"]

                pub_sale_c = data["ico_data"]["quote_public_sale_currency"]
                pub_sale_a = data["ico_data"]["base_public_sale_amount"]
                pub_sale_p = data["ico_data"]["quote_public_sale_amount"]

                kyc_req = data["ico_data"]["kyc_required"]

                raised = utl.format(raised) if raised is not None else raised

                if pre_sale_a:
                    pre_sale_a = utl.format(pre_sale_a, symbol=coin)
                if pre_sale_p:
                    pre_sale_p = utl.format(pre_sale_p, symbol=pre_sale_c)

                if pub_sale_a:
                    pub_sale_a = utl.format(pub_sale_a, symbol=coin)
                if pub_sale_p:
                    pub_sale_p = utl.format(pub_sale_p, symbol=pub_sale_c)

                if pre_sale_a:
                    pre_sale_str = f"{pre_sale_a} {coin} for {pre_sale_p} {pre_sale_c}\n"
                else:
                    pre_sale_str = "None\n"

                if pub_sale_a:
                    pub_sale_str = f"{pub_sale_a} {coin} for {pub_sale_p} {pub_sale_c}\n"
                else:
                    pub_sale_str = "None\n"

                msg = f"`" \
                      f"Start:    {ico_start}\n" \
                      f"End:      {ico_end}\n" \
                      f"Raised:   {raised} {raised_cur}\n" \
                      f"Pre-Sale: {pre_sale_str}" \
                      f"Pub-Sale: {pub_sale_str}" \
                      f"KYC:      {'Yes' if kyc_req == True else 'No'}" \
                      f"`"
                break

        if msg:
            msg = f"`ICO data for {coin}`\n\n" + msg
        else:
            msg = f"{emo.INFO} No ICO data for *{coin}*"

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <symbol>`"

    def get_description(self):
        return "ICO info for coin"

    def get_category(self):
        return Category.PRICE
