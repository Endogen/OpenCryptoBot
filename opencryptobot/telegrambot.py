import os
import uuid
import logging
import importlib
import threading
import opencryptobot.emoji as emo
import opencryptobot.utils as utl
import opencryptobot.constants as con

from importlib import reload
from opencryptobot.plugin import Keyword
from opencryptobot.api.github import GitHub
from opencryptobot.api.apicache import APICache
from opencryptobot.config import ConfigManager as Cfg

from telegram import ParseMode, InlineQueryResultArticle, InputTextMessageContent, Chat
from telegram.ext import Updater, InlineQueryHandler, RegexHandler, MessageHandler, Filters
from telegram.error import InvalidToken


def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


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
        except InvalidToken as e:
            cls_name = f"Class: {type(self).__name__}"
            logging.error(f"{repr(e)} - {cls_name}")
            exit("ERROR: Bot token not valid")

        self.job_queue = self.updater.job_queue
        self.dispatcher = self.updater.dispatcher

        # Load classes in folder 'plugins'
        self._load_plugins()

        # Handler for files downloads (plugins)
        mh = MessageHandler(Filters.document, self._download)
        self.dispatcher.add_handler(mh)

        # Handler for command-links
        self._add_link_handler()

        # Handler for inline-mode
        inline_handler = InlineQueryHandler(self._inline)
        self.dispatcher.add_handler(inline_handler)

        # Handle all Telegram related errors
        self.dispatcher.add_error_handler(self._handle_tg_errors)

        # Refresh cache periodically
        self._refresh_cache()

        # Check for updates periodically
        self._update_check()

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

    def _cmd_link_callback(self, bot, update):
        cmd = update.effective_message.text.split('__')[0].replace("/_", "")
        args = update.effective_message.text.split('__')[1].split("_")

        for p in self.plugins:
            if cmd.lower() in p.get_cmds():
                p.get_action(bot, update, args=args)
                break

    def _add_link_handler(self):
        self.dispatcher.add_handler(RegexHandler(
            utl.comp("^/_([a-zA-Z0-9]*)__([\w]*)$"), self._cmd_link_callback))

    def _load_plugins(self):
        threads = list()

        for _, _, files in os.walk(os.path.join(con.SRC_DIR, con.PLG_DIR)):
            for file in files:
                if not file.lower().endswith(".py"):
                    continue
                if file.startswith("_"):
                    continue

                threads.append(self._load_plugin(file))

        # Make sure that all plugins are loaded
        for thread in threads:
            thread.join()

        for plugin in self.plugins:
            plugin.after_plugins_loaded()

    @threaded
    def _load_plugin(self, file):
        try:
            module_name = file[:-3]
            module_path = f"{con.SRC_DIR}.{con.PLG_DIR}.{module_name}"
            module = importlib.import_module(module_path)

            plugin_class = getattr(module, module_name.capitalize())
            plugin_class(self).after_plugin_loaded()
        except Exception as ex:
            msg = f"File '{file}' can't be loaded as a plugin: {ex}"
            logging.warning(msg)

    def remove_plugin(self, module_name):
        for plugin in self.plugins:
            if type(plugin).__name__.lower() == module_name.lower():
                plugin.remove_plugin()
                break

    def reload_plugin(self, module_name):
        self.remove_plugin(module_name)

        try:
            module_path = f"{con.SRC_DIR}.{con.PLG_DIR}.{module_name}"
            module = importlib.import_module(module_path)

            reload(module)

            plugin_class = getattr(module, module_name.capitalize())
            plugin_class(self)
        except Exception as ex:
            msg = f"Plugin '{module_name.capitalize()}' can't be reloaded: {ex}"
            logging.warning(msg)
            raise ex

    def _download(self, bot, update):
        # Check if in a private chat
        if bot.get_chat(update.message.chat_id).type != Chat.PRIVATE:
            return

        # Check if user that triggered the command is allowed to execute it
        if update.effective_user.id not in Cfg.get("admin_id"):
            return

        name = update.message.effective_attachment.file_name
        file = bot.getFile(update.message.document.file_id)
        file.download(os.path.join(con.SRC_DIR, con.PLG_DIR, name))

        try:
            self.reload_plugin(name.replace(".py", ""))
            update.message.reply_text(f"{emo.CHECK} Plugin loaded successfully")
        except Exception as ex:
            update.message.reply_text(f"{emo.ERROR} {ex}")

    def _inline(self, bot, update):
        query = update.inline_query.query
        if not query or not query.startswith("/") or not query.endswith("."):
            return

        def _send(msg, description=None):
            if not description:
                description = str(msg)

            content = InputTextMessageContent(str(msg), parse_mode=ParseMode.MARKDOWN)
            inline_result = InlineQueryResultArticle(
                id=uuid.uuid4(),
                title=description,
                input_message_content=content)

            bot.answer_inline_query(update.inline_query.id, [inline_result])

        args = query.split(" ")
        args[len(args) - 1] = args[len(args)-1].replace(".", "")
        cmd = args[0][1:].lower()
        args.pop(0)

        args.append(f"{Keyword.INLINE}=true")

        plgn = None
        for plugin in self.plugins:
            if cmd in plugin.get_cmds():
                if not plugin.inline_mode():
                    message = "Inline mode not supported"
                    return _send(f"{emo.INFO} {message}")

                plgn = plugin
                break

        if not plgn:
            message = "Command not found"
            return _send(f"{emo.INFO} {message}")

        v = plgn.get_action(bot, update, args=args)

        if not v:
            message = "No message returned"
            return _send(f"{emo.ERROR} {message}")

        if not isinstance(v, str):
            message = "No *string* returned"
            return _send(f"{emo.ERROR} {message}")

        if v.startswith(emo.ERROR) or v.startswith(emo.INFO):
            return _send(v)

        _send(v, plgn.get_description())

    # Handle all telegram and telegram.ext related errors
    def _handle_tg_errors(self, bot, update, error):
        cls_name = f"Class: {type(self).__name__}"
        logging.error(f"{error} - {cls_name} - {update}")

        if not update:
            return

        error_msg = f"{emo.ERROR} Telegram ERROR: *{error}*"

        if update.message:
            update.message.reply_text(
                text=error_msg,
                parse_mode=ParseMode.MARKDOWN)
        elif update.callback_query:
            update.callback_query.message.reply_text(
                text=error_msg,
                parse_mode=ParseMode.MARKDOWN)

    def _refresh_cache(self):
        if Cfg.get("refresh_cache") is not None:
            sec = utl.get_seconds(Cfg.get("refresh_cache"))

            if not sec:
                sec = con.DEF_CACHE_REFRESH
                msg = f"Refresh rate for caching not valid. Using {sec} seconds"
                logging.warning(msg)

            try:
                self.job_queue.run_repeating(APICache.refresh, sec, first=0)
            except Exception as e:
                logging.error(repr(e))

    def _update_check(self):
        def _check_for_update(bot, job):
            user = Cfg.get('update', 'github_user')
            repo = Cfg.get('update', 'github_repo')
            gh = GitHub(github_user=user, github_repo=repo)

            try:
                # Get latest release
                response = gh.get_latest_release()
            except Exception as ex:
                logging.error(repr(ex))
                return

            if job.context:
                if job.context["tag"] == response["tag_name"]:
                    return
            else:
                job.context = dict()
                job.context["tag"] = response["tag_name"]

            release_notes = response["body"]

            try:
                response = gh.get_tags()
            except Exception as ex:
                logging.error(repr(ex))
                return

            new_hash = str()
            for t in response:
                if t["name"] == job.context["tag"]:
                    new_hash = t["commit"]["sha"]
                    break

            cfg_hash = Cfg.get("update", "update_hash")

            if cfg_hash != new_hash:
                for admin in Cfg.get("admin_id"):
                    update_cmd = utl.esc_md("/update")
                    tag = job.context['tag']

                    try:
                        bot.send_message(
                            admin,
                            f"New release *{utl.esc_md(tag)}* available\n\n"
                            f"*Release Notes*\n{utl.esc_md(release_notes)}\n\n"
                            f"{update_cmd}",
                            parse_mode=ParseMode.MARKDOWN)
                    except Exception as ex:
                        err = f"Can't send release notes to chat {admin}"
                        logging.error(f"{err} - {ex}")

        if Cfg.get("update", "update_check") is not None:
            sec = utl.get_seconds(Cfg.get("update", "update_check"))

            if not sec:
                sec = con.DEF_UPDATE_CHECK
                msg = f"Update check time not valid. Using {sec} seconds"
                logging.warning(msg)

            try:
                self.job_queue.run_repeating(_check_for_update, sec, first=0)
            except Exception as e:
                logging.error(repr(e))
