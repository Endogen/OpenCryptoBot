import os
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

        if Cfg.get("use_db"):
            # Create database
            sql_dir = con.SQL_DIR
            db_path = self.args.database
            self.db = Database(db_path, sql_dir)
        else:
            self.db = None

        # Create bot
        bot_token = self._get_bot_token()
        self.tg = TelegramBot(bot_token, self.db)

    # Parse arguments
    def _parse_args(self):
        desc = "Telegram bot for crypto currency info"
        parser = ArgumentParser(description=desc)

        # Config file
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
            required=False)
        parser.set_defaults(savelog=True)

        # Save history
        parser.add_argument(
            "--no-database",
            dest="savedata",
            action="store_false",
            help="save command history to database",
            required=False)
        parser.set_defaults(savedata=True)

        # Logfile
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

        # Database
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
            required=False)
        parser.set_defaults(webhook=False)

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

        token_path = os.path.join(con.CFG_DIR, con.TOK_FILE)

        if os.path.isfile(token_path):
            with open(token_path, 'r') as file:
                return file.read().splitlines()[0]
        else:
            exit(f"ERROR: No token file found at '{token_path}'")

    def start(self):
        if self.args.webhook:
            self.tg.bot_start_webhook()
        else:
            self.tg.bot_start_polling()

        self.tg.bot_idle()


if __name__ == '__main__':
    OpenCryptoBot().start()
