from telegram import ParseMode
import opencryptobot.emoji as emo
from opencryptobot.config import ConfigManager as Cfg
from opencryptobot.plugin import OpenCryptoPlugin, Category


class Feedback(OpenCryptoPlugin):

    def get_cmds(self):
        return ["feedback"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
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

        feedback = update.message.text.replace(f"/{self.get_cmds()[0]} ", "")

        for admin in Cfg.get("admin_id"):
            bot.send_message(admin, f"Feedback from {name}: {feedback}")

        update.message.reply_text(f"Thanks for letting us know {emo.TOP}")

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <your feedback>`\n"

    def get_description(self):
        return "Send us your feedback"

    def get_category(self):
        return Category.BOT
