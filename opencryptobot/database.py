import os
import zlib
import pickle
import sqlite3
import inspect
import opencryptobot.emoji as emo
import opencryptobot.constants as c


class Database:

    # Initialize database
    def __init__(self, db_path="data.db"):
        self._db_path = db_path

        # Create 'data' directory if not present
        data_dir = os.path.dirname(db_path)
        os.makedirs(data_dir, exist_ok=True)

        con = sqlite3.connect(db_path)
        cur = con.cursor()

        # If tables don't exist, create them
        if not cur.execute(self.get_sql("db_exists")).fetchone():
            cur.execute(self.get_sql("users"))
            con.commit()
            cur.execute(self.get_sql("chats"))
            con.commit()
            cur.execute(self.get_sql("repeaters"))
            con.commit()
            cur.execute(self.get_sql("cmd_data"))
            con.commit()

            con.close()

        # SQL - Check if user exists
        self.usr_exist_sql = self.get_sql("user_exists")
        # SQL - Check if chat exists
        self.cht_exist_sql = self.get_sql("chat_exists")
        # SQL - Add user
        self.add_usr_sql = self.get_sql("user_add")
        # SQL - Add chat
        self.add_cht_sql = self.get_sql("chat_add")
        # SQL - Read chat
        self.read_cht_sql = self.get_sql("read_chat")
        # SQL - Save command
        self.save_cmd_sql = self.get_sql("cmd_save")
        # SQL - Read repeating commands for a user or chat
        self.read_rep_sql = self.get_sql("rep_read")
        # SQL - Read repeating commands for a user
        self.read_rep_usr_sql = self.get_sql("rep_read_usr")
        # SQL - Read repeating commands
        self.read_rep_all_sql = self.get_sql("rep_read_all")
        # SQL - Save repeating command
        self.save_rep_sql = self.get_sql("rep_save")
        # SQL - Delete repeating command
        self.delete_rep_sql = self.get_sql("rep_delete")

    # Get string with SQL statement from file
    def get_sql(self, filename):
        cls = inspect.stack()[1][0].f_locals["self"].__class__
        cls_name = cls.__name__.lower()
        filename = f"{filename}.sql"

        with open(os.path.join(c.SQL_DIR, cls_name, filename)) as f:
            return f.read()

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

        if chat and chat.id != user.id:
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

    # Save new repeater to database
    def save_rep(self, update, interval):
        if update.message:
            usr = update.message.from_user
            cmd = update.message.text.lower()
            cht = update.message.chat
        elif update.inline_query:
            usr = update.effective_user
            cmd = update.inline_query.query[:-1].lower()
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
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        if user_id:
            if user_id == chat_id or chat_id is None:
                cur.execute(self.read_rep_usr_sql, [user_id])
            else:
                cur.execute(self.read_rep_sql, [user_id, chat_id])
        else:
            cur.execute(self.read_rep_all_sql)

        con.commit()

        result = cur.fetchall()

        results = list()
        for repeater in result:
            rep = list(repeater)
            rep[5] = pickle.loads(zlib.decompress(rep[5]))

            results.append(rep)

        con.close()
        return results

    # Delete repeaters from database
    def delete_rep(self, repeater_id):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        cur.execute(
            self.delete_rep_sql,
            [repeater_id])

        con.commit()
        con.close()

    # Read chat by chat_id
    def read_chat(self, chat_id):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        cur.execute(self.read_cht_sql, [chat_id])
        con.commit()

        result = cur.fetchall()

        con.close()

        if result:
            return list(result[0])

        return None

    # Execute raw SQL statements on database
    def execute_sql(self, sql, *args):
        dic = {"result": None, "error": None}

        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        try:
            cur.execute(sql, args)
            con.commit()
            dic["result"] = cur.fetchall()
        except Exception as e:
            dic["error"] = f"{emo.ERROR} {e}"

        con.close()
        return dic
