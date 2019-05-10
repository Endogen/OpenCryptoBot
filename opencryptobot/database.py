import os
import zlib
import pickle
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

        # SQL - Read repeating commands
        with open(os.path.join(sql_path, "rep_read_all.sql")) as f:
            self.read_rep_all_sql = f.read()

        # SQL - Read repeating commands for a user or chat
        with open(os.path.join(sql_path, "rep_read.sql")) as f:
            self.read_rep_sql = f.read()

        # SQL - Save repeating command
        with open(os.path.join(sql_path, "rep_save.sql")) as f:
            self.save_rep_sql = f.read()

        # SQL - Delete repeating command
        with open(os.path.join(sql_path, "rep_delete.sql")) as f:
            self.delete_rep_sql = f.read()

    # Save user and / or chat to database
    def save_usr_and_cht(self, user, chat):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

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

        con.close()
        return {"user_id": user.id, "chat_id": chat_id}

    # Save issued commands to database
    def save_cmd(self, usr, cht, cmd):
        ids = self.save_usr_and_cht(usr, cht)

        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        # Save issued command
        cur.execute(
            self.save_cmd_sql,
            [ids["user_id"], ids["chat_id"], cmd])

        con.commit()
        con.close()

    # TODO: Create table 'repeater' with primary key 'user' & 'command'
    # TODO: Don't allow to have multiple same repeaters
    # Save new repeater to database
    def save_rep(self, update, interval):
        if update.message:
            usr = update.message.from_user
            cmd = update.message.text
            cht = update.message.chat
        elif update.inline_query:
            usr = update.effective_user
            cmd = update.inline_query.query[:-1]
            cht = update.effective_chat
        else:
            raise Exception("Not possible to save repeater")

        ids = self.save_usr_and_cht(usr, cht)
        upd = zlib.compress(pickle.dumps(update))

        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        # Save msg to be repeated
        cur.execute(
            self.save_rep_sql,
            [ids["user_id"], ids["chat_id"], cmd, interval, upd])

        con.commit()
        con.close()

    # Read repeaters from database
    def read_rep(self, user_id=None, chat_id=None):
        if Cfg.get("database", "use_db"):
            con = sqlite3.connect(self._db_path)
            cur = con.cursor()

            if user_id:
                cur.execute(
                    self.read_rep_sql,
                    [user_id, chat_id])
            else:
                cur.execute(self.read_rep_all_sql)

            con.commit()

            result = cur.fetchall()

            results = list()
            for repeater in result:
                rep = list(repeater)
                rep[4] = pickle.loads(zlib.decompress(rep[4]))

                results.append(rep)

            con.close()
            return results

    def delete_rep(self, user_id, command):
        if Cfg.get("database", "use_db"):
            con = sqlite3.connect(self._db_path)
            cur = con.cursor()

            cur.execute(
                self.delete_rep_sql,
                [int(user_id), command])

            con.commit()
            con.close()

    # Execute raw SQL statements on database
    def execute_sql(self, sql, *args):
        if Cfg.get("database", "use_db"):
            con = sqlite3.connect(self._db_path)
            cur = con.cursor()

            cur.execute(sql, args)
            con.commit()

            result = cur.fetchall()

            con.close()
            return result
