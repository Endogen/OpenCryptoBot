import os
import sqlite3


# TODO: Read all SQL statements from files
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
            for _, _, files in os.walk(sql_path):
                for file in files:
                    with open(os.path.join(sql_path, file)) as f:
                        cur.execute(f.read())
                        con.commit()

            con.close()

    # Check if user is already present in database
    def user_exists(self, user_id):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        sql = "SELECT EXISTS(SELECT 1 FROM users WHERE user_id = ?)"
        cur.execute(sql, [user_id])
        con.commit()

        r = cur.fetchone()
        con.close()

        return True if r[0] == 1 else False

    def add_user(self, user_data):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        sql = "INSERT INTO users " \
              "(user_id, first_name, last_name, username, language) " \
              "VALUES (?, ?, ?, ?, ?)"

        cur.execute(sql, [user_data.id,
                          user_data.first_name,
                          user_data.last_name,
                          user_data.username,
                          user_data.language_code])
        con.commit()
        con.close()

    def save_cmd(self, usr_id, cmd):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        sql = "INSERT INTO commands " \
              "(user_id, command) " \
              "VALUES (?, ?)"

        cur.execute(sql, [usr_id, cmd])
        con.commit()
        con.close()
