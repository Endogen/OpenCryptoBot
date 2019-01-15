import os
# TODO: Check if these can be part or the corresponding module
# Partial URL for coin logo
CG_LOGO_URL_PARTIAL = "https://www.cryptocompare.com"
CMC_URL_PARTIAL = "https://coinmarketcap.com/currencies/"
CMC_LOGO_URL_PARTIAL = "https://s2.coinmarketcap.com/static/img/coins/128x128/"
ALL_CRYPTO_WP_PARTIAL = "https://www.allcryptowhitepapers.com/"
COIN_PAPRIKA_PARTIAL = "https://coinpaprika.com/coin/"

CFG_DIR = "conf"
CFG_FILE = "config.json"
BOT_TKN_FILE = "bot.token"
CRYPAN_TKN_FILE = "cryptopanic.token"

LOG_DIR = "log"
LOG_FILE = "opencryptobot.log"

DAT_DIR = "data"
DAT_FILE = "opencryptobot.db"

SQL_DIR = "sql"

RES_DIR = "res"
BPMN_DIR = os.path.join(RES_DIR, "bpmn")

MAX_TG_MSG_LEN = 4096

CG_DATA_LIMIT = 2000

# In seconds
DEF_CACHE_REFRESH = 86400
