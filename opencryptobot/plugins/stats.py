import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from telegram import ParseMode
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.apicache import APICache
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin, Category, Keyword


class Stats(OpenCryptoPlugin):

    def get_cmds(self):
        return ["s", "stats"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        keywords = utl.get_kw(args)
        arg_list = utl.del_kw(args)

        if not arg_list:
            if not keywords.get(Keyword.INLINE):
                update.message.reply_text(
                    text=f"Usage:\n{self.get_usage()}",
                    parse_mode=ParseMode.MARKDOWN)
            return

        if RateLimit.limit_reached(update):
            return

        coin = arg_list[0].upper()
        data = None
        cgid = None

        try:
            response = APICache.get_cg_coins_list()
        except Exception as e:
            return self.handle_error(e, update)

        # Get coin ID and data
        for entry in response:
            if entry["symbol"].upper() == coin:
                try:
                    data = CoinGecko().get_coin_by_id(entry["id"])
                except Exception as e:
                    return self.handle_error(e, update)

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

        cs = int(float(data['market_data']['circulating_supply']))
        sup_c = f"{utl.format(cs)} {symbol}"

        if data["market_data"]["total_supply"]:
            ts = int(float(data["market_data"]["total_supply"]))
            sup_t = f"{utl.format(ts)} {symbol}"
        else:
            sup_t = "N/A"

        usd = data["market_data"]["current_price"]["usd"]
        eur = data["market_data"]["current_price"]["eur"]
        btc = data["market_data"]["current_price"]["btc"]
        eth = data["market_data"]["current_price"]["eth"]

        p_usd = utl.format(usd, force_length=True)
        p_eur = utl.format(eur, force_length=True, template=p_usd)
        p_btc = utl.format(btc, force_length=True, template=p_usd)
        p_eth = utl.format(eth, force_length=True, template=p_usd)

        p_usd = "{:>12}".format(p_usd)
        p_eur = "{:>12}".format(p_eur)
        p_btc = "{:>12}".format(p_btc)
        p_eth = "{:>12}".format(p_eth)

        # Do not display BTC or ETH price if coin is BTC or ETH
        btc_str = "" if coin == "BTC" else f"BTC {p_btc}\n"
        eth_str = "" if coin == "ETH" else f"ETH {p_eth}\n"

        v_24h = utl.format(int(float(data["market_data"]["total_volume"]["usd"])))
        m_cap = utl.format(int(float(data["market_data"]["market_cap"]["usd"])))

        if data["market_data"]["price_change_percentage_1h_in_currency"]:
            c_1h = data["market_data"]["price_change_percentage_1h_in_currency"]["usd"]
            c1h = utl.format(float(c_1h), decimals=2, force_length=True)
            h1 = "{:>10}".format(f"{c1h}%")
        else:
            h1 = "{:>10}".format("N/A")

        if data["market_data"]["price_change_percentage_24h_in_currency"]:
            c_1d = data["market_data"]["price_change_percentage_24h_in_currency"]["usd"]
            c1d = utl.format(float(c_1d), decimals=2, force_length=True)
            d1 = "{:>10}".format(f"{c1d}%")
        else:
            d1 = "{:>10}".format("N/A")

        if data["market_data"]["price_change_percentage_7d_in_currency"]:
            c_1w = data["market_data"]["price_change_percentage_7d_in_currency"]["usd"]
            c1w = utl.format(float(c_1w), decimals=2, force_length=True)
            w1 = "{:>10}".format(f"{c1w}%")
        else:
            w1 = "{:>10}".format("N/A")

        if data["market_data"]["price_change_percentage_30d_in_currency"]:
            c_1m = data["market_data"]["price_change_percentage_30d_in_currency"]["usd"]
            c1m = utl.format(float(c_1m), decimals=2, force_length=True)
            m1 = "{:>10}".format(f"{c1m}%")
        else:
            m1 = "{:>10}".format("N/A")

        if data["market_data"]["price_change_percentage_1y_in_currency"]:
            c_1y = data["market_data"]["price_change_percentage_1y_in_currency"]["usd"]
            c1y = utl.format(float(c_1y), decimals=2, force_length=True)
            y1 = "{:>10}".format(f"{c1y}%")
        else:
            y1 = "{:>10}".format("N/A")

        msg = f"`" \
              f"{name} ({symbol})\n\n" \
              f"USD {p_usd}\n" \
              f"EUR {p_eur}\n" \
              f"{btc_str}" \
              f"{eth_str}\n" \
              f"Hour  {h1}\n" \
              f"Day   {d1}\n" \
              f"Week  {w1}\n" \
              f"Month {m1}\n" \
              f"Year  {y1}\n\n" \
              f"Market Cap Rank: {rank_mc}\n" \
              f"Coin Gecko Rank: {rank_cg}\n\n" \
              f"Volume 24h: {v_24h} USD\n" \
              f"Market Cap: {m_cap} USD\n" \
              f"Circ. Supp: {sup_c}\n" \
              f"Total Supp: {sup_t}\n\n" \
              f"`" \
              f"Stats on [CoinGecko](https://www.coingecko.com/en/coins/{cgid}) & " \
              f"[Coinlib](https://coinlib.io/coin/{coin}/{coin})"

        if keywords.get(Keyword.INLINE):
            return msg

        self.send_msg(msg, update, keywords)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <symbol>`"

    def get_description(self):
        return "Price, market cap and volume"

    def get_category(self):
        return Category.PRICE

    def inline_mode(self):
        return True
