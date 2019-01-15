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

from opencryptobot.api.github import GitHub
from opencryptobot.plugin import OpenCryptoPlugin
from opencryptobot.config import ConfigManager as Cfg


class Update(OpenCryptoPlugin):

    UPD_DIR = "update"

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
            msg = f"{emo.ERROR} Combination of 'force' " \
                  f"and 'check' arguments not allowed"
            update.message.reply_text(msg)
            return

        kw = utl.get_keywords(args)

        branch = kw["branch"] if "branch" in kw else None
        release = kw["release"] if "release" in kw else None

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
            shutil.rmtree(os.path.join(os.getcwd(), self.UPD_DIR))
        except:
            pass

        # ---------- BRANCH ----------
        if branch:
            try:
                # Get latest commit info for branch
                response = gh.get_latest_branch(branch)
            except Exception as e:
                utl.handle_api_error(e)

                msg = f"{emo.ERROR} Couldn't get branch info"
                update.message.reply_text(msg)
                return

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
                utl.handle_api_error(e)

                msg = f"{emo.ERROR} Couldn't get release info..."
                update.message.reply_text(msg)
                return

            if release:
                tag = response[0]["tag_name"]
            else:
                tag = response["tag_name"]

            try:
                response = gh.get_tags()
            except Exception as e:
                utl.handle_api_error(e)

                msg = f"{emo.ERROR} Couldn't get release tags"
                update.message.reply_text(msg)
                return

            new_hash = str()
            for t in response:
                if t["name"] == tag:
                    new_hash = t["commit"]["sha"]
                    download_url = t["zipball_url"]

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
                msg = f"{emo.CHECK} New release available!"
                update.message.reply_text(msg)
                return

        # ---------- UPDATE ----------

        msg = f"{emo.WAIT} Downloading update..."
        m = update.message.reply_text(msg)

        try:
            response = requests.get(download_url)
            response.raise_for_status()
        except Exception as e:
            utl.handle_api_error(e)

            msg = f"{emo.ERROR} Couldn't download update"
            update.message.reply_text(msg)
            return

        msg = f"{emo.CHECK} Downloading update..."
        bot.edit_message_text(msg, chat_id=uid, message_id=m.message_id)

        msg = f"{emo.WAIT} Updating bot..."
        m = update.message.reply_text(msg)

        zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        zip_file.extractall(self.UPD_DIR)

        done = False
        unzip_dir = str()
        for _, dirs, _ in os.walk(self.UPD_DIR):
            for d in dirs:
                unzip_dir = d
                done = True
                break
            if done:
                break

        self._update_bot(os.path.join(self.UPD_DIR, unzip_dir))

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
        """
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
        """
    def get_usage(self):
        return None

    def get_description(self):
        return None

    def get_category(self):
        return None
