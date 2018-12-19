import os

# Partial URL for coin logo
CG_LOGO_URL_PARTIAL = "https://www.cryptocompare.com"
CMC_URL_PARTIAL = "https://coinmarketcap.com/currencies/"
CMC_LOGO_URL_PARTIAL = "https://s2.coinmarketcap.com/static/img/coins/128x128/"
ALL_CRYPTO_WP_PARTIAL = "https://www.allcryptowhitepapers.com/"
COIN_PAPRIKA_PARTIAL = "https://coinpaprika.com/coin/"

GITHUB_BASE_URL = "https://raw.githubusercontent.com/"

CFG_DIR = "conf"
CFG_FILE = "config.json"
TOK_FILE = "bot.token"

LOG_DIR = "log"
LOG_FILE = "opencryptobot.log"

DAT_DIR = "data"
DAT_FILE = "opencryptobot.db"

SQL_DIR = "sql"

RES_DIR = "res"
BPMN_DIR = os.path.join(RES_DIR, "bpmn")

MAX_TG_MSG_LEN = 4096

CG_DATA_LIMIT = 2000
