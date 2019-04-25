import os
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

    def save_user_and_chat(self, usr_data, cht_data):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        # Check if user already exists
        cur.execute(
            self.usr_exist_sql,
            [usr_data.id])

        con.commit()

        # Add user if he doesn't exist
        if cur.fetchone()[0] != 1:
            cur.execute(
                self.add_usr_sql,
                [usr_data.id,
                 usr_data.first_name,
                 usr_data.last_name,
                 usr_data.username,
                 usr_data.language_code])

            con.commit()

        chat_id = None

        if cht_data.id != usr_data.id:
            chat_id = cht_data.id

            # Check if chat already exists
            cur.execute(
                self.cht_exist_sql,
                [cht_data.id])

            con.commit()

            # Add chat if it doesn't exist
            if cur.fetchone()[0] != 1:
                cur.execute(
                    self.add_cht_sql,
                    [cht_data.id,
                     cht_data.type,
                     cht_data.title,
                     cht_data.username])

                con.commit()

        return {"user_id": usr_data.id, "chat_id": chat_id}

    def save_cmd(self, usr_data, cht_data, cmd):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        ids = self.save_user_and_chat(usr_data, cht_data)

        # Save issued command
        cur.execute(
            self.save_cmd_sql,
            [ids["user_id"], ids["chat_id"], cmd])

        con.commit()
        con.close()

    # TODO: https://dba.stackexchange.com/questions/43284/two-nullable-columns-one-required-to-have-value
    def save_rep(self, user, chat, cmd, interval):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        ids = self.save_user_and_chat(user, chat)

        # Save msg to be repeated
        cur.execute(
            self.save_rep_sql,
            [ids["user_id"], ids["chat_id"], cmd, interval])

        con.commit()
        con.close()

    def read_rep(self):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        # TODO: Do this nicely - look up the code
        cur.execute(self.read_rep_sql)
        con.commit()

        result = cur.fetchall()

        con.close()
        return result

    def execute_sql(self, sql, *args):
        if Cfg.get("database", "use_db"):
            con = sqlite3.connect(self._db_path)
            cur = con.cursor()

            cur.execute(sql, args)
            con.commit()

            result = cur.fetchall()

            con.close()
            return result
