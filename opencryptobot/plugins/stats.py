import opencryptobot.emoji as emo

from telegram import ParseMode
from opencryptobot.plugin import OpenCryptoPlugin
from opencryptobot.api.coingecko import CoinGecko


# TODO: Add additional data from response
class Stats(OpenCryptoPlugin):

    def get_cmd(self):
        return "s"

    @OpenCryptoPlugin.send_typing
    @OpenCryptoPlugin.save_data
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        coin = args[0].upper()
        data = None
        cgid = None

        cg = CoinGecko()

        # Get coin ID and data
        for entry in cg.get_coins_list():
            if entry["symbol"].upper() == coin:
                data = cg.get_coin_by_id(entry["id"])
                cgid = entry["id"]
                break

        if not data:
            update.message.reply_text(
                text=f"{emo.ERROR} No data for *{coin}*",
                parse_mode=ParseMode.MARKDOWN)
            return

        name = data["name"]
        symbol = data["symbol"].upper()

        rank_mc = data["market_cap_rank"]
        rank_cg = data["coingecko_rank"]

        sup_c = "{0:,}".format(
            int(float(
                data["market_data"]["circulating_supply"]))) + f" {symbol}"

        if data["market_data"]["total_supply"]:
            sup_t = "{0:,}".format(
                int(float(
                    data["market_data"]["total_supply"]))) + f" {symbol}"
        else:
            sup_t = "N/A"

        p_usd = "{0:.8f}".format(data["market_data"]["current_price"]["usd"])
        p_eur = "{0:.8f}".format(data["market_data"]["current_price"]["eur"])
        p_btc = "{0:.8f}".format(data["market_data"]["current_price"]["btc"])
        p_eth = "{0:.8f}".format(data["market_data"]["current_price"]["eth"])

        # TODO: How to dynamically set the width?
        #max_len = max([len(p_usd), len(p_eur), len(p_btc), len(p_eth)])

        p_usd = "{:>13}".format(p_usd)
        p_eur = "{:>13}".format(p_eur)
        p_btc = "{:>13}".format(p_btc)
        p_eth = "{:>13}".format(p_eth)

        # Do not display BTC or ETH price if coin is BTC or ETH
        btc_str = "" if coin == "BTC" else f"BTC {p_btc}\n"
        eth_str = "" if coin == "ETH" else f"ETH {p_eth}\n"

        v_24h = "{0:,}".format(int(float(data["market_data"]["total_volume"]["usd"])))
        m_cap = "{0:,}".format(int(float(data["market_data"]["market_cap"]["usd"])))

        if data["market_data"]["price_change_percentage_1h_in_currency"]:
            c_1h = data["market_data"]["price_change_percentage_1h_in_currency"]["usd"]
            c1h = "{0:.2f}".format(float(c_1h))
            h1 = "{:>11}".format(f"{c1h}%")
        else:
            h1 = "{:>11}".format("N/A")

        if data["market_data"]["price_change_percentage_24h_in_currency"]:
            c_1d = data["market_data"]["price_change_percentage_24h_in_currency"]["usd"]
            c1d = "{0:.2f}".format(float(c_1d))
            d1 = "{:>11}".format(f"{c1d}%")
        else:
            d1 = "{:>11}".format("N/A")

        if data["market_data"]["price_change_percentage_7d_in_currency"]:
            c_1w = data["market_data"]["price_change_percentage_7d_in_currency"]["usd"]
            c1w = "{0:.2f}".format(float(c_1w))
            w1 = "{:>11}".format(f"{c1w}%")
        else:
            w1 = "{:>11}".format("N/A")

        if data["market_data"]["price_change_percentage_30d_in_currency"]:
            c_1m = data["market_data"]["price_change_percentage_30d_in_currency"]["usd"]
            c1m = "{0:.2f}".format(float(c_1m))
            m1 = "{:>11}".format(f"{c1m}%")
        else:
            m1 = "{:>11}".format("N/A")

        if data["market_data"]["price_change_percentage_1y_in_currency"]:
            c_1y = data["market_data"]["price_change_percentage_1y_in_currency"]["usd"]
            c1y = "{0:.2f}".format(float(c_1y))
            y1 = "{:>11}".format(f"{c1y}%")
        else:
            y1 = "{:>11}".format("N/A")

        update.message.reply_text(
            text=f"`"
                 f"{name} ({symbol})\n\n"
                 f"USD {p_usd}\n"
                 f"EUR {p_eur}\n"
                 f"{btc_str}"
                 f"{eth_str}\n"
                 f"Hour  {h1}\n"
                 f"Day   {d1}\n"
                 f"Week  {w1}\n"
                 f"Month {m1}\n"
                 f"Year  {y1}\n\n"
                 f"Market Cap Rank: {rank_mc}\n"
                 f"Coin Gecko Rank: {rank_cg}\n\n"
                 f"Volume 24h: {v_24h} USD\n"
                 f"Market Cap: {m_cap} USD\n"
                 f"Circ. Supp: {sup_c}\n"
                 f"Total Supp: {sup_t}\n\n"
                 f"`"
                 f"Stats on [CoinGecko](https://www.coingecko.com/en/coins/{cgid}) & "
                 f"[Coinlib](https://coinlib.io/coin/{coin}/{coin})",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True)

    def get_usage(self):
        return f"`/{self.get_cmd()} <coin>`"

    def get_description(self):
        return "Price, market cap and volume"
