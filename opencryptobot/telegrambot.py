import os
import uuid
import logging
import importlib
import opencryptobot.emoji as emo

from telegram import ParseMode, InlineQueryResultArticle, InputTextMessageContent
from telegram.error import InvalidToken
from telegram.ext import Updater, CommandHandler, InlineQueryHandler
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin
from opencryptobot.config import ConfigManager as Cfg


class TelegramBot:

    plugins = list()

    def __init__(self, bot_token, bot_db):
        self.db = bot_db
        self.token = bot_token

        read_timeout = Cfg.get("telegram", "read_timeout")
        connect_timeout = Cfg.get("telegram", "connect_timeout")

        kwargs = dict()
        if read_timeout:
            kwargs["read_timeout"] = read_timeout
        if connect_timeout:
            kwargs["connect_timeout"] = connect_timeout

        try:
            self.updater = Updater(bot_token, request_kwargs=kwargs)
        except InvalidToken:
            exit("ERROR: Bot token not valid")

        self.job_queue = self.updater.job_queue
        self.dispatcher = self.updater.dispatcher

        self._load_plugins()

        # Handler for inline-mode
        self.dispatcher.add_handler(InlineQueryHandler(self._inline))

        # Handle all Telegram related errors
        self.dispatcher.add_error_handler(self._handle_tg_errors)

        # If enabled, fill cache
        if Cfg.get("use_cache"):
            logging.info("Starting Caching")
            CoinGecko.refresh_cache()
            logging.info("Finished Caching")

    # Start the bot
    def bot_start_polling(self):
        self.updater.start_polling(clean=True)

    # Go in idle mode
    def bot_idle(self):
        self.updater.idle()

    def bot_start_webhook(self):
        self.updater.start_webhook(
            listen=Cfg.get("webhook", "listen"),
            port=Cfg.get("webhook", "port"),
            url_path=self.token,
            key=Cfg.get("webhook", "privkey_path"),
            cert=Cfg.get("webhook", "cert_path"),
            webhook_url=f"{Cfg.get('webhook', 'url')}:"
                        f"{Cfg.get('webhook', 'port')}/"
                        f"{self.token}")

    def _load_plugins(self):
        for _, _, files in os.walk(os.path.join("opencryptobot", "plugins")):
            for file in files:
                if not file.lower().endswith(".py"):
                    continue
                if file.startswith("_"):
                    continue

                module_name = file[:-3]
                module_path = f"opencryptobot.plugins.{module_name}"

                try:
                    module = importlib.import_module(module_path)
                    plugin_class = getattr(module, module_name.capitalize())
                    instance = plugin_class(self.updater, self.db)

                    if isinstance(instance, OpenCryptoPlugin):
                        cmd = instance.get_cmd()
                        act = instance.get_action

                        self.dispatcher.add_handler(
                            CommandHandler(cmd, act, pass_args=True)
                        )

                        TelegramBot.plugins.append(instance)
                        logging.info(f"Plugin '{module_name}' added")

                except Exception as ex:
                    msg = f"File '{file}' can't be loaded as a plugin: {ex}"
                    logging.warning(msg)

    def _inline(self, bot, update):
        query = update.inline_query.query
        if not query or not query.startswith("/") or not query.endswith("."):
            return

        args = query.split(" ")
        args[len(args) - 1] = args[len(args)-1].replace(".", "")
        cmd = args[0][1:]
        args.pop(0)

        value = str()
        description = str()
        for plugin in self.plugins:
            if plugin.get_cmd() == cmd:
                if not plugin.inline_mode():
                    return

                value = plugin.get_action(bot, update, args=args)
                description = plugin.get_description()
                break

        if not value:
            return

        results = list()
        results.append(
            InlineQueryResultArticle(
                id=uuid.uuid4(),
                title=description,
                input_message_content=InputTextMessageContent(value, parse_mode=ParseMode.MARKDOWN)
            )
        )

        bot.answer_inline_query(update.inline_query.id, results)

    # Handle all telegram and telegram.ext related errors
    def _handle_tg_errors(self, bot, update, error):
        error_msg = f"{emo.ERROR} Telegram ERROR: *{error}*"
        logging.error(error)

        if update.message:
            update.message.reply_text(
                text=error_msg,
                parse_mode=ParseMode.MARKDOWN)
        else:
            update.callback_query.message.reply_text(
                text=error_msg,
                parse_mode=ParseMode.MARKDOWN)
