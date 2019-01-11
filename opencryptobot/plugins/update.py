import os
import io
import sys
import time
import shutil
import zipfile
import requests
import opencryptobot.emoji as emo
import opencryptobot.constants as con

from opencryptobot.plugin import OpenCryptoPlugin
from opencryptobot.config import ConfigManager as Cfg


class Update(OpenCryptoPlugin):

    def get_cmd(self):
        return "update"

    @OpenCryptoPlugin.only_owner
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        # TODO: Implement arguments
        force = False
        check = False
        restart = False
        branch = False
        release = False

        uid = update.message.from_user.id

        msg = f"{emo.WAIT} Checking for new version..."
        m = update.message.reply_text(msg)

        user = Cfg.get('update', 'github_user')
        repo = Cfg.get('update', 'github_repo')

        # Get newest version of the project from GitHub
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

            zip_file = zipfile.ZipFile(io.BytesIO(response.content))
            zip_file.extractall()

            udp_dir = response.headers.get('Content-Disposition')
            udp_dir = udp_dir.split('=')[1].split('.')[0]

            cur_path = os.getcwd()
            upd_path = os.path.join(cur_path, udp_dir)

            shutil.rmtree(os.path.join(upd_path, con.CFG_DIR))

            for _, dirs, files in os.walk(upd_path):
                for dir in dirs:
                    cp = os.path.join(cur_path, dir)

                    if os.path.exists(cp):
                        shutil.rmtree(cp)

                    up = os.path.join(upd_path, dir)
                    shutil.copytree(up, cp)

                for file in files:
                    up = os.path.join(upd_path, file)
                    cp = os.path.join(cur_path, file)
                    shutil.copy(up, cp)

            # Save current ETag (hash) of project zip to config
            Cfg.set(new_etag, "update", "update_hash")

            if restart:
                msg = f"{emo.CHECK} Update completed..."
                update.message.reply_text(msg)
                msg = f"{emo.WAIT} Restarting bot..."
                update.message.reply_text(msg)

                time.sleep(0.2)
                os.execl(sys.executable, sys.executable, *sys.argv)
            else:
                msg = f"{emo.CHECK} Update completed. /restart"
                update.message.reply_text(msg)

        else:
            msg = f"{emo.ERROR} Update not executed. " \
                  f"Unexpected status code: {response.status_code}"
            update.message.reply_text(msg)

    def get_usage(self):
        return None

    def get_description(self):
        return None

    def get_category(self):
        return None
