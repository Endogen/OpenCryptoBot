from telegram import ParseMode
import opencryptobot.emoji as emo
from opencryptobot.plugin import OpenCryptoPlugin
from opencryptobot.config import ConfigManager as Cfg


class Feedback(OpenCryptoPlugin):

    def get_cmd(self):
        return "fe"

    @OpenCryptoPlugin.send_typing
    @OpenCryptoPlugin.save_data
    def get_action(self, bot, update, args):

        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        user = update.message.from_user
        if user.username:
            name = f"@{user.username}"
        else:
            name = user.first_name

        feedback = update.message.text.replace(f"/{self.get_cmd()} ", "")
        bot.send_message(Cfg.get("admin_id"), f"Feedback from {name}: {feedback}")

        update.message.reply_text(f"Thanks for letting us know {emo.TOP}")

    def get_usage(self):
        return f"`/{self.get_cmd()} <your feedback>`\n"

    def get_description(self):
        return "Send us your feedback"
