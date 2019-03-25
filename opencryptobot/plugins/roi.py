import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from telegram import ParseMode
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.tokenstats import TokenStats
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Roi(OpenCryptoPlugin):

    def get_cmds(self):
        return ["roi"]

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
            data = TokenStats().get_roi_for_symbol(coin)
        except Exception as e:
            return self.handle_error(e, update)

        if not data:
            update.message.reply_text(
                text=f"{emo.INFO} No data found for {coin}",
                parse_mode=ParseMode.MARKDOWN)
            return

        msg = str(f"`Return on Investment for {coin}`\n\n")

        roi_usd_x = utl.format(data["roix_usd"], decimals=2, force_length=True, on_none="-")
        roi_usd_x = "{:>10}".format(roi_usd_x)

        roi_btc_x = utl.format(data["roix_btc"], decimals=2, force_length=True, on_none="-")
        roi_btc_x = "{:>10}".format(roi_btc_x)

        roi_eth_x = utl.format(data["roix_eth"], decimals=2, force_length=True, on_none="-")
        roi_eth_x = "{:>10}".format(roi_eth_x)

        # If all values are the same then this means
        # that there was no ICO and thus no ROI available
        if roi_usd_x == roi_btc_x == roi_eth_x:
            update.message.reply_text(
                text=f"{emo.INFO} No ROI data for {coin}",
                parse_mode=ParseMode.MARKDOWN)
            return

        if data["roix_usd"]:
            msg += f"`ROI USD: {roi_usd_x}x`\n"
        else:
            msg += f"`ROI USD:  {roi_usd_x}`\n"

        if data["roix_btc"]:
            msg += f"`ROI BTC: {roi_btc_x}x`\n"
        else:
            msg += f"`ROI BTC:  {roi_btc_x}`\n"

        if data["roix_eth"]:
            msg += f"`ROI ETH: {roi_eth_x}x`\n\n"
        else:
            msg += f"`ROI ETH:  {roi_eth_x}`\n\n"

        pre_p_usd = data["usd_price_at_presale"]
        pre_p_usd_f = utl.format(pre_p_usd, decimals=2, force_length=True, on_zero='-')

        pre_p_btc = data["btc_price_at_presale"]
        pre_p_btc_f = utl.format(pre_p_btc, decimals=8, on_zero='-')

        pre_p_eth = data["eth_price_at_presale"]
        pre_p_eth_f = utl.format(pre_p_eth, decimals=8, on_zero='-')

        msg += f"`Presale Price USD: {pre_p_usd_f}`\n"
        msg += f"`Presale Price BTC: {pre_p_btc_f}`\n"
        msg += f"`Presale Price ETH: {pre_p_eth_f}`\n\n"

        lnc_p_usd = data["usd_price_at_launch"]
        lnc_p_usd_f = utl.format(lnc_p_usd, decimals=2, force_length=True, on_zero='-')

        lnc_p_btc = data["btc_price_at_launch"]
        lnc_p_btc_f = utl.format(lnc_p_btc, decimals=8, on_zero='-')

        lnc_p_eth = data["eth_price_at_launch"]
        lnc_p_eth_f = utl.format(lnc_p_eth, decimals=8, on_zero='-')

        msg += f"`Launch Price USD:  {lnc_p_usd_f}`\n"
        msg += f"`Launch Price BTC:  {lnc_p_btc_f}`\n"
        msg += f"`Launch Price ETH:  {lnc_p_eth_f}`\n\n"

        cur_p_usd = data["current_usd_price"]
        cur_p_usd_f = utl.format(cur_p_usd, decimals=2, force_length=True, on_zero='-')

        cur_p_btc = data["current_btc_price"]
        cur_p_btc_f = utl.format(cur_p_btc, decimals=8, on_zero='-')

        cur_p_eth = data["current_eth_price"]
        cur_p_eth_f = utl.format(cur_p_eth, decimals=8, on_zero='-')

        msg += f"`Current Price USD: {cur_p_usd_f}`\n"
        msg += f"`Current Price BTC: {cur_p_btc_f}`\n"
        msg += f"`Current Price ETH: {cur_p_eth_f}`"

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <symbol>`"

    def get_description(self):
        return "Return on Investment for a coin"

    def get_category(self):
        return Category.PRICE
