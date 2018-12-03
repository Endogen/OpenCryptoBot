import threading
import opencryptobot.emoji as emo

from telegram.ext import CommandHandler
from opencryptobot.plugin import OpenCryptoPlugin


# TODO: "@OpenCryptoPlugin.add_user" should be always there, not needed to add it
class Shutdown(OpenCryptoPlugin):

    def get_handler(self):
        return CommandHandler("shutdown", self._shutdown)

    @OpenCryptoPlugin.add_user
    @OpenCryptoPlugin.only_owner
    @OpenCryptoPlugin.send_typing
    def _shutdown(self, bot, update):
        msg = f"{emo.GOODBYE} Shutting down..."
        update.message.reply_text(msg)

        threading.Thread(target=self._shutdown_thread).start()

    def _shutdown_thread(self):
        self.updater.stop()
        self.updater.is_idle = False
