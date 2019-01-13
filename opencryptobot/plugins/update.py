import os
import io
import sys
import time
import shutil
import zipfile
import requests
import opencryptobot.emoji as emo
import opencryptobot.utils as utl
import opencryptobot.constants as con

from opencryptobot.plugin import OpenCryptoPlugin
from opencryptobot.config import ConfigManager as Cfg


class Update(OpenCryptoPlugin):

    def get_cmd(self):
        return "update"

    @OpenCryptoPlugin.only_owner
    @OpenCryptoPlugin.send_typing
    def get_action(self, bot, update, args):
        restart = False
        force = False
        check = False

        if "force" in args:
            force = True
        if "check" in args:
            check = True
        if "restart" in args:
            restart = True

        if force and check:
            msg = f"{emo.ERROR} Combination of `force` " \
                  f"and `check` arguments not allowed"
            update.message.reply_text(msg)
            return

        kw = utl.get_keywords(args)

        branch = kw["branch"] if "branch" in kw else None
        release = kw["release"] if "release" in kw else None

        if branch and release:
            msg = f"{emo.ERROR} Combination of `branch` " \
                  f"and `release` arguments not allowed"
            update.message.reply_text(msg)
            return

        msg = f"{emo.WAIT} Checking version..."
        m = update.message.reply_text(msg)

        user = Cfg.get('update', 'github_user')
        repo = Cfg.get('update', 'github_repo')

        uid = update.message.from_user.id

        if branch:
            # Get latest commit details
            url = f"{con.GH_API_URL}{user}/{repo}{con.GH_API_BRANCH}{branch}"
            response = requests.get(url)

            if not response.ok:
                msg = f"{emo.ERROR} Couldn't get metadata for " \
                      f"download. Status code: {response.status_code}"
                update.message.reply_text(msg)
                return

            msg = f"{emo.CHECK} Checking version..."
            bot.edit_message_text(msg, chat_id=uid, message_id=m.message_id)

            cfg_hash = Cfg.get("update", "update_hash")
            new_hash = response.json()["commit"]["sha"]

            if cfg_hash == new_hash and not force:
                msg = f"{emo.CHECK} You are running the latest version"
                update.message.reply_text(msg)
                return

            if check:
                msg = f"{emo.CHECK} New version available!"
                update.message.reply_text(msg)
                return

            msg = f"{emo.WAIT} Downloading data..."
            m = update.message.reply_text(msg)

            # Get latest version of branch as zip
            url = f"{con.GH_URL}{user}/{repo}{con.GH_MASTER}"
            response = requests.get(url)

        else:
            if release:
                # Get specific release
                url = f"{con.GH_API_URL}{user}/{repo}{con.GH_API_RELEASES}"
            else:
                # Get latest release
                url = f"{con.GH_API_URL}{user}/{repo}{con.GH_API_RELEASE}{'latest'}"

            response = requests.get(url)

            if not response.ok:
                msg = f"{emo.ERROR} Couldn't get metadata for " \
                      f"download. Status code: {response.status_code}"
                update.message.reply_text(msg)
                return

            msg = f"{emo.CHECK} Checking version..."
            bot.edit_message_text(msg, chat_id=uid, message_id=m.message_id)

            if release:
                tag = response.json()[0]["tag_name"]
            else:
                tag = response.json()["tag_name"]

            url = f"{con.GH_API_URL}{user}/{repo}{con.GH_API_TAGS}"
            response = requests.get(url)

            if not response.ok:
                msg = f"{emo.ERROR} Couldn't get metadata for " \
                      f"download. Status code: {response.status_code}"
                update.message.reply_text(msg)
                return

            for t in response.json():
                if t["name"] == tag:
                    new_hash = t["commit"]["sha"]
                    download_url = t["zipball_url"]

            cfg_hash = Cfg.get("update", "update_hash")

            if cfg_hash == new_hash and not force:
                msg = f"{emo.CHECK} You are already running this release"
                update.message.reply_text(msg)
                return

            if check:
                msg = f"{emo.CHECK} New version available!"
                update.message.reply_text(msg)
                return

            msg = f"{emo.WAIT} Downloading data..."
            m = update.message.reply_text(msg)

            response = requests.get(download_url)

        if not response.ok:
            msg = f"{emo.ERROR} Couldn't download data. " \
                f"Status code: {response.status_code}"
            update.message.reply_text(msg)
            return

        msg = f"{emo.CHECK} Downloading data..."
        bot.edit_message_text(msg, chat_id=uid, message_id=m.message_id)

        msg = f"{emo.WAIT} Updating bot..."
        m = update.message.reply_text(msg)

        zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        zip_file.extractall("update")

        done = False
        for _, dirs, _ in os.walk("update"):
            for d in dirs:
                upd_dir = d
                done = True
                break
            if done:
                break

        self._update_bot(os.path.join("update", upd_dir))

        Cfg.set(new_hash, "update", "update_hash")

        msg = f"{emo.CHECK} Updating bot..."
        bot.edit_message_text(msg, chat_id=uid, message_id=m.message_id)

        if restart:
            msg = f"{emo.WAIT} Restarting bot..."
            update.message.reply_text(msg)

            time.sleep(0.2)
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            msg = "Bot /restart needed"
            update.message.reply_text(msg)

    def _update_bot(self, upd_dir):
        cur_path = os.getcwd()
        upd_path = os.path.join(cur_path, upd_dir)

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

        shutil.rmtree(upd_path)

    def get_usage(self):
        return None

    def get_description(self):
        return None

    def get_category(self):
        return None
