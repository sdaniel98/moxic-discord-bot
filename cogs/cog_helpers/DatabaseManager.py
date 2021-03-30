import sqlite3
import json
import base64

class DatabaseManager:

    def __init__(self):
        self.connection = sqlite3.connect("./database/discord_users.db")

    async def add_user(self, discord_id, fflogs_id, lodestone_id, lodestone_data):
        try:
            cur = self.connection.cursor()
            query = f"INSERT INTO discord_users (discord_id, fflogs_id, lodestone_id, lodestone_data_cache) VALUES " \
                    f"({discord_id}, {fflogs_id}, {lodestone_id}, \"{lodestone_data}\")"
            cur.execute(query)
        except Exception as e:
            cur.close()
            self.connection.rollback()
        else:
            cur.close()
            self.connection.commit()

    async def get_fflogs_id(self, discord_id):
        try:
            cur = self.connection.cursor()
            query = f"SELECT fflogs_id FROM discord_users WHERE discord_id={discord_id}"
            cur.execute(query)
        except Exception as e:
            cur.close()
            print(f"Error accessing database for fflogs_id: {e}")
        else:
            tmp = cur.fetchone()
            cur.close()
            return tmp[0]

    async def get_lodestone_id(self, discord_id):
        try:
            cur = self.connection.cursor()
            query = f"SELECT lodestone_id FROM discord_users WHERE discord_id={discord_id}"
            cur.execute(query)
        except Exception as e:
            cur.close()
            print(f"Error accessing database for fflogs_id: {e}")
        else:
            tmp = cur.fetchone()
            cur.close()
            return tmp[0]

    async def get_lodestone_cache(self, discord_id):
        try:
            print(discord_id)
            cur = self.connection.cursor()
            query = f"SELECT lodestone_data_cache FROM discord_users WHERE discord_id={discord_id}"
            cur.execute(query)
        except Exception as e:
            cur.close()
            print(f"Error accessing database for fflogs_id: {e}")
        else:
            tmp = cur.fetchone()[0]
            cur.close()
            #convert cache string to bytes then base64decode it then convert back to string and turn it into a dictionary
            return json.loads((base64.b64decode(tmp.encode())).decode())

    async def update_lodestone_cache(self, discord_id, new_cache):
        try:
            cur = self.connection.cursor()
            query = f"UPDATE discord_users SET lodestone_data_cache = \"{new_cache}\" WHERE discord_id = {discord_id}"
            cur.execute(query)
        except Exception as e:
            cur.close()
            self.connection.rollback()
            print(f"Error updating lodestone cache: {e}")
        else:
            cur.close()
            self.connection.commit()

    def close(self):
        self.connection.close()
