import os
import pickle
import logging
import sqlite3

from opencryptobot.config import ConfigManager as Cfg


class Database:

    # Initialize database
    def __init__(self, db_path="data.db", sql_path="sql"):
        self._db_path = db_path

        # Create 'data' directory if not present
        data_dir = os.path.dirname(db_path)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        con = sqlite3.connect(db_path)
        cur = con.cursor()

        # If tables don't exist, create them
        sql = "SELECT name FROM sqlite_master"
        if not cur.execute(sql).fetchone():
            with open(os.path.join(sql_path, "users.sql")) as f:
                cur.execute(f.read())
                con.commit()
            with open(os.path.join(sql_path, "chats.sql")) as f:
                cur.execute(f.read())
                con.commit()
            with open(os.path.join(sql_path, "repeaters.sql")) as f:
                cur.execute(f.read())
                con.commit()
            with open(os.path.join(sql_path, "cmd_data.sql")) as f:
                cur.execute(f.read())
                con.commit()

            con.close()

        # SQL - Check if user exists
        with open(os.path.join(sql_path, "user_exists.sql")) as f:
            self.usr_exist_sql = f.read()

        # SQL - Check if chat exists
        with open(os.path.join(sql_path, "chat_exists.sql")) as f:
            self.cht_exist_sql = f.read()

        # SQL - Add user
        with open(os.path.join(sql_path, "user_add.sql")) as f:
            self.add_usr_sql = f.read()

        # SQL - Add chat
        with open(os.path.join(sql_path, "chat_add.sql")) as f:
            self.add_cht_sql = f.read()

        # SQL - Save command
        with open(os.path.join(sql_path, "cmd_save.sql")) as f:
            self.save_cmd_sql = f.read()

        # SQL - Read repeating command
        with open(os.path.join(sql_path, "rep_read.sql")) as f:
            self.read_rep_sql = f.read()

        # SQL - Save repeating command
        with open(os.path.join(sql_path, "rep_save.sql")) as f:
            self.save_rep_sql = f.read()

    def save_src(self, update):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        if update.message:
            user = update.message.from_user
            chat = update.message.chat
        elif update.inline_query:
            user = update.effective_user
            chat = update.effective_chat
        else:
            logging.error(f"Can't save usage. User and chat unknown: {update}")
            return None

        if user.id in Cfg.get("admin_id"):
            if not Cfg.get("database", "track_admins"):
                return None

        # Check if user already exists
        cur.execute(
            self.usr_exist_sql,
            [user.id])

        con.commit()

        # Add user if he doesn't exist
        if cur.fetchone()[0] != 1:
            cur.execute(
                self.add_usr_sql,
                [user.id,
                 user.first_name,
                 user.last_name,
                 user.username,
                 user.language_code])

            con.commit()

        chat_id = None

        if chat.id != user.id:
            chat_id = chat.id

            # Check if chat already exists
            cur.execute(
                self.cht_exist_sql,
                [chat.id])

            con.commit()

            # Add chat if it doesn't exist
            if cur.fetchone()[0] != 1:
                cur.execute(
                    self.add_cht_sql,
                    [chat.id,
                     chat.type,
                     chat.title,
                     chat.username])

                con.commit()

        return {"user_id": user.id, "chat_id": chat_id}

    def save_cmd(self, update):
        ids = self.save_src(update)

        if not ids:
            return

        if update.message:
            cmd = update.message.text
        elif update.inline_query:
            cmd = update.inline_query.query[:-1]
        else:
            logging.error(f"Can't save usage. Command unknown: {update}")
            return

        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        # Save issued command
        cur.execute(
            self.save_cmd_sql,
            [ids["user_id"], ids["chat_id"], cmd])

        con.commit()
        con.close()

    # TODO: https://dba.stackexchange.com/questions/43284/two-nullable-columns-one-required-to-have-value
    # TODO: ZIP data to reach smaller data size for DB
    def save_rep(self, update, interval):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        ids = self.save_src(update)
        cmd = update.message.text
        ser = pickle.dumps(update)

        # Save msg to be repeated
        cur.execute(
            self.save_rep_sql,
            [ids["user_id"], ids["chat_id"], cmd, interval, ser])

        con.commit()
        con.close()

    def read_rep(self):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        cur.execute(self.read_rep_sql)
        con.commit()

        result = cur.fetchall()

        results = list()
        for repeater in result:
            rep_details = list(repeater)
            rep_details[4] = pickle.loads(rep_details[4])

            results.append(rep_details)

        con.close()
        return results

    def execute_sql(self, sql, *args):
        if Cfg.get("database", "use_db"):
            con = sqlite3.connect(self._db_path)
            cur = con.cursor()

            cur.execute(sql, args)
            con.commit()

            result = cur.fetchall()

            con.close()
            return result
