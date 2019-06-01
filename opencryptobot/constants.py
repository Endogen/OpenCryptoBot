import os

# Partial URL for coin logo
CMC_LOGO_URL_PARTIAL = "https://s2.coinmarketcap.com/static/img/coins/128x128/"

CFG_DIR = "conf"
CFG_FILE = "config.json"
TKN_FILE = "token.json"

LOG_DIR = "log"
LOG_FILE = "opencryptobot.log"

DAT_DIR = "data"
DAT_FILE = "opencryptobot.db"

SQL_DIR = "sql"

UPD_DIR = "update"

BCK_DIR = "backup"

RES_DIR = "res"
BPMN_DIR = os.path.join(RES_DIR, "bpmn")

SRC_DIR = "opencryptobot"
PLG_DIR = "plugins"

MAX_TG_MSG_LEN = 4096
CG_DATA_LIMIT = 2000
DEF_CACHE_REFRESH = 86400  # In seconds
DEF_UPDATE_CHECK = 86400  # In seconds
