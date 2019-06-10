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

from telegram import ParseMode
from opencryptobot.api.github import GitHub
from opencryptobot.plugin import OpenCryptoPlugin
from opencryptobot.config import ConfigManager as Cfg


class Update(OpenCryptoPlugin):

    def get_cmds(self):
        return ["update"]

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
            msg = f"{emo.ERROR} Combination of 'force' " \
                  f"and 'check' arguments not allowed"
            update.message.reply_text(msg)
            return

        kw = utl.get_kw(args)
        branch = kw.get("branch", None)
        release = kw.get("release", None)

        if branch and release:
            msg = f"{emo.ERROR} Combination of 'branch' " \
                  f"and 'release' arguments not allowed"
            update.message.reply_text(msg)
            return

        msg = f"{emo.WAIT} Check for update..."
        m = update.message.reply_text(msg)

        user = Cfg.get('update', 'github_user')
        repo = Cfg.get('update', 'github_repo')
        gh = GitHub(github_user=user, github_repo=repo)

        uid = update.message.from_user.id
        download_url = str()

        try:
            # Clean old update data if present
            shutil.rmtree(os.path.join(os.getcwd(), con.UPD_DIR))
        except:
            pass

        # ---------- BRANCH ----------
        if branch:
            try:
                # Get latest commit info for branch
                response = gh.get_latest_branch(branch)
            except Exception as e:
                return self.handle_error(e, update)

            cfg_hash = Cfg.get("update", "update_hash")
            new_hash = response["commit"]["sha"]

            msg = f"{emo.CHECK} Check for update..."
            bot.edit_message_text(msg, chat_id=uid, message_id=m.message_id)

            if cfg_hash == new_hash and not force:
                msg = f"{emo.CHECK} You are already running the latest version"
                update.message.reply_text(msg)
                return

            if check:
                msg = f"{emo.CHECK} New branch commits available!"
                update.message.reply_text(msg)
                return

            # Get latest version of branch as zip
            download_url = f"https://github.com/{user}/{repo}/archive/{branch}.zip"

        # ---------- RELEASE ----------
        else:
            try:
                if release:
                    # Get specific release
                    response = gh.get_releases()
                else:
                    # Get latest release
                    response = gh.get_latest_release()
            except Exception as e:
                return self.handle_error(e, update)

            if release:
                tag = response[0]["tag_name"]
                release_notes = response[0]["body"]
            else:
                tag = response["tag_name"]
                release_notes = response["body"]

            try:
                response = gh.get_tags()
            except Exception as e:
                return self.handle_error(e, update)

            new_hash = str()
            for t in response:
                if t["name"] == tag:
                    new_hash = t["commit"]["sha"]
                    download_url = t["zipball_url"]
                    break

            if not new_hash:
                msg = f"{emo.ERROR} Tag '{tag}' unknown"
                update.message.reply_text(msg)
                return

            cfg_hash = Cfg.get("update", "update_hash")

            msg = f"{emo.CHECK} Check for update..."
            bot.edit_message_text(msg, chat_id=uid, message_id=m.message_id)

            if cfg_hash == new_hash and not force:
                msg = f"{emo.CHECK} You are already running this release"
                update.message.reply_text(msg)
                return

            if check:
                msg = f"{emo.CHECK} New release *{tag}* available!\n\n" \
                      f"*Release Notes*\n{release_notes}"
                update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
                return

        # ---------- DOWNLOAD & UPDATE ----------

        msg = f"{emo.WAIT} Downloading update..."
        m = update.message.reply_text(msg)

        try:
            response = requests.get(download_url)
            response.raise_for_status()
        except Exception as e:
            return self.handle_error(e, update)

        msg = f"{emo.CHECK} Downloading update..."
        bot.edit_message_text(msg, chat_id=uid, message_id=m.message_id)

        msg = f"{emo.WAIT} Updating bot..."
        m = update.message.reply_text(msg)

        zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        zip_file.extractall(con.UPD_DIR)

        done = False
        unzip_dir = str()
        for _, dirs, _ in os.walk(con.UPD_DIR):
            for d in dirs:
                unzip_dir = d
                done = True
                break
            if done:
                break

        self._update_bot(os.path.join(con.UPD_DIR, unzip_dir))

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
