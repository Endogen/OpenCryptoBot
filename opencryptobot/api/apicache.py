import logging

from coinmarketcap import Market
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.api.coinpaprika import CoinPaprika


class APICache(object):

    cg_fiat_list = list()
    cg_coin_list = list()
    cg_exch_list = list()
    cp_coin_list = list()
    cmc_coin_list = list()

    @staticmethod
    def refresh(bot, job):
        logging.info("Starting Caching")

        APICache.refresh_coingecko_coin_list()
        APICache.refresh_coingecko_exchange_list()
        APICache.refresh_coinpaprika_coin_list()
        APICache.refresh_coinmarketcap_coin_list()

        logging.info("Finished Caching")

    # Functions to refresh cache ------------------------

    @staticmethod
    def refresh_coingecko_coin_list():
        APICache.cg_coin_list = CoinGecko().get_coins_list()

    @staticmethod
    def refresh_coinpaprika_coin_list():
        APICache.cp_coin_list = CoinPaprika().get_list_coins()

    @staticmethod
    def refresh_coinmarketcap_coin_list():
        APICache.cmc_coin_list = Market().listings()["data"]

    @staticmethod
    def refresh_coingecko_exchange_list():
        APICache.cg_exch_list = CoinGecko().get_exchanges_list()

    # Functions to return cached data -------------------

    @staticmethod
    def get_cg_coins_list():
        if APICache.cg_coin_list:
            return APICache.cg_coin_list
        else:
            return CoinGecko().get_coins_list()

    @staticmethod
    def get_cp_coin_list():
        if APICache.cp_coin_list:
            return APICache.cp_coin_list
        else:
            return CoinPaprika().get_list_coins()

    @staticmethod
    def get_cmc_coin_list():
        if APICache.cmc_coin_list:
            return APICache.cmc_coin_list
        else:
            return Market().listings()["data"]

    @staticmethod
    def get_cg_exchanges_list():
        if APICache.cg_exch_list:
            return APICache.cg_exch_list
        else:
            return CoinGecko().get_exchanges_list()
