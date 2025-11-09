import sqlite3
from env import DATABASE_NAME
class UTXODatabase:
    def __init__(self):
        self.con = sqlite3.connect(DATABASE_NAME)
        self.cur = self.con.cursor()
        
    def insert(self, insert_queue):
        self.cur.executemany("INSERT INTO utxo (hash, address, amount, timestamp) VALUES (?, ?, ?, ?)", insert_queue)
        self.con.commit()
        
    def delete(self, delete_queue):
        self.cur.executemany("DELETE FROM utxo WHERE hash = (?);", delete_queue)
        self.con.commit()

