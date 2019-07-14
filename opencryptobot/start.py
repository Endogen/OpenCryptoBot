import os
import json
import logging
import opencryptobot.constants as con

from argparse import ArgumentParser
from opencryptobot.database import Database
from opencryptobot.telegrambot import TelegramBot
from opencryptobot.config import ConfigManager as Cfg
from logging.handlers import TimedRotatingFileHandler


class OpenCryptoBot:

    def __init__(self):
        # Parse command line arguments
        self.args = self._parse_args()

        # Load config file
        Cfg(self.args.config)

        # Set up logging
        log_path = self.args.logfile
        log_level = self.args.loglevel
        self._init_logger(log_path, log_level)

        # Create database
        db_path = self.args.database
        self.db = Database(db_path)

        # Create bot
        bot_token = self._get_bot_token()
        self.tg = TelegramBot(bot_token, self.db)

    # Parse arguments
    def _parse_args(self):
        desc = "Telegram bot for crypto currency info"
        parser = ArgumentParser(description=desc)

        # Config file path
        parser.add_argument(
            "-cfg",
            dest="config",
            help="path to conf file",
            default=os.path.join(con.CFG_DIR, con.CFG_FILE),
            required=False,
            metavar="FILE")

        # Save logfile
        parser.add_argument(
            "--no-logfile",
            dest="savelog",
            action="store_false",
            help="don't save logs to file",
            required=False,
            default=True)

        # Use database
        parser.add_argument(
            "--no-database",
            dest="savedata",
            action="store_false",
            help="save command history to database",
            required=False,
            default=True)

        # Logfile path
        parser.add_argument(
            "-log",
            dest="logfile",
            help="path to logfile",
            default=os.path.join(con.LOG_DIR, con.LOG_FILE),
            required=False,
            metavar="FILE")

        # Log level
        parser.add_argument(
            "-lvl",
            dest="loglevel",
            type=int,
            choices=[0, 10, 20, 30, 40, 50],
            help="Disabled, Debug, Info, Warning, Error, Critical",
            default=30,
            required=False)

        # Module log level
        parser.add_argument(
            "-mlvl",
            dest="mloglevel",
            help="set log level for a module",
            default=None,
            required=False)

        # Database path
        parser.add_argument(
            "-db",
            dest="database",
            help="path to SQLite database file",
            default=os.path.join(con.DAT_DIR, con.DAT_FILE),
            required=False,
            metavar="FILE")

        # Bot token
        parser.add_argument(
            "-tkn",
            dest="token",
            help="Telegram bot token",
            required=False,
            default=None)

        # Webhook
        parser.add_argument(
            "--webhook",
            dest="webhook",
            action="store_true",
            help="use webhook instead of polling",
            required=False,
            default=False)

        return parser.parse_args()

    # Configure logging
    def _init_logger(self, logfile, level):
        logger = logging.getLogger()
        logger.setLevel(level)

        log_format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'

        # Log to console
        console_log = logging.StreamHandler()
        console_log.setFormatter(logging.Formatter(log_format))
        console_log.setLevel(level)

        logger.addHandler(console_log)

        # Save logs if enabled
        if self.args.savelog:
            # Create 'log' directory if not present
            log_path = os.path.dirname(logfile)
            if not os.path.exists(log_path):
                os.makedirs(log_path)

            file_log = TimedRotatingFileHandler(
                logfile,
                when="H",
                encoding="utf-8")

            file_log.setFormatter(logging.Formatter(log_format))
            file_log.setLevel(level)

            logger.addHandler(file_log)

        # Set log level for specified modules
        if self.args.mloglevel:
            for modlvl in self.args.mloglevel.split(","):
                module, loglvl = modlvl.split("=")
                logr = logging.getLogger(module)
                logr.setLevel(int(loglvl))

    # Read bot token from file
    def _get_bot_token(self):
        if self.args.token:
            return self.args.token

        token_path = os.path.join(con.CFG_DIR, con.TKN_FILE)

        try:
            if os.path.isfile(token_path):
                with open(token_path, 'r') as file:
                    return json.load(file)["telegram"]
            else:
                exit(f"ERROR: No token file '{con.TKN_FILE}' found at '{token_path}'")
        except KeyError as e:
            cls_name = f"Class: {type(self).__name__}"
            logging.error(f"{repr(e)} - {cls_name}")
            exit("ERROR: Can't read bot token")

    def start(self):
        if self.args.webhook:
            self.tg.bot_start_webhook()
        else:
            self.tg.bot_start_polling()

        self.tg.bot_idle()
