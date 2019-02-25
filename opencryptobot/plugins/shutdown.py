import threading
import opencryptobot.emoji as emo

from opencryptobot.plugin import OpenCryptoPlugin


class Shutdown(OpenCryptoPlugin):

    def get_cmds(self):
        return ["shutdown"]

    @OpenCryptoPlugin.only_owner
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        msg = f"{emo.GOODBYE} Shutting down..."
        update.message.reply_text(msg)

        threading.Thread(target=self._shutdown_thread).start()

    def get_usage(self):
        return None

    def get_description(self):
        return None

    def get_category(self):
        return None

    def _shutdown_thread(self):
        self.tgb.updater.stop()
        self.tgb.updater.is_idle = False
