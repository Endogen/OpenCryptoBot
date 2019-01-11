import io
import zipfile
import requests
import opencryptobot.emoji as emo
import opencryptobot.constants as con

from opencryptobot.plugin import OpenCryptoPlugin
from opencryptobot.config import ConfigManager as Cfg


# TODO: Params: force, 'branch-name', release, check, restart
# TODO: Only update 'opencryptobot' and 'res'
class Update(OpenCryptoPlugin):

    def get_cmd(self):
        return "update"

    @OpenCryptoPlugin.only_owner
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        uid = update.message.from_user.id

        msg = f"{emo.WAIT} Checking for new version..."
        m = update.message.reply_text(msg)

        user = Cfg.get('update', 'github_user')
        repo = Cfg.get('update', 'github_repo')

        # Get newest version of this script from GitHub
        url = f"{con.GH_URL}{user}/{repo}{con.GH_MASTER}"
        response = requests.get(url)

        msg = f"{emo.CHECK} Checking for new version..."
        bot.edit_message_text(msg, chat_id=uid, message_id=m.message_id)

        if response.ok:
            cfg_etag = Cfg.get("update", "update_hash")
            new_etag = response.headers.get("ETag").replace('"', '')

            if cfg_etag == new_etag:
                msg = "You are running the latest version"
                update.message.reply_text(msg)
                return

            # Save current ETag (hash) of project zip to config
            Cfg.set(new_etag, "update", "update_hash")

            zip_file = zipfile.ZipFile(io.BytesIO(response.content))
            zip_file.extractall()

            msg = f"{emo.CHECK} Update completed! /restart"
            update.message.reply_text(msg)

            # time.sleep(0.2)
            # os.execl(sys.executable, sys.executable, *sys.argv)

        else:
            msg = emo.ERROR + "Update not executed. Unexpected status code: " + response.status_code
            update.message.reply_text(msg)

    def get_usage(self):
        return None

    def get_description(self):
        return None

    def get_category(self):
        return None
