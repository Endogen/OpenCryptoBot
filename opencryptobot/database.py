import os
import sqlite3


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

        sql = "SELECT name FROM sqlite_master"
        if not cur.execute(sql).fetchone():
            with open(os.path.join(sql_path, "users.sql")) as f:
                cur.execute(f.read())
                con.commit()
            with open(os.path.join(sql_path, "commands.sql")) as f:
                cur.execute(f.read())
                con.commit()

            con.close()

        # SQL - Check if user exists
        with open(os.path.join(sql_path, "user_exists.sql")) as f:
            self.usr_exist_check_sql = f.read()

        # SQL - Add user
        with open(os.path.join(sql_path, "add_user.sql")) as f:
            self.add_usr_sql = f.read()

        # SQL - Save command
        with open(os.path.join(sql_path, "save_command.sql")) as f:
            self.save_cmd_sql = f.read()

    def save(self, usr_data, cmd):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        # Check if user already exists
        cur.execute(
            self.usr_exist_check_sql,
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

        # Save issued command
        cur.execute(
            self.save_cmd_sql,
            [usr_data.id, cmd])

        con.commit()
        con.close()
