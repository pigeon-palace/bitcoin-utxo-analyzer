import requests
import math 
import time
import os
import csv
import sqlite3

GENESIS_HASH = "80ca095ed10b02e53d769eb6eaf92cd04e9e0759e5be4a8477b42911ba49c78f"
REST_URL = 'http://127.0.0.1:9332/rest'
DATABASE_FILENAME = "build/utxo.db"
ADDRESSES_FILENAME = "build/address_balance_distribution.csv"
AGE_FILENAME = "build/utxo_age_distribution.csv"
COIN = 10**8

class BlockParser:
    def __init__(self, script_handler):
        self.delete_queue = []
        self.insert_queue = []
        self.script_handler = script_handler
        
    def getblock(self, block_hash):
        return requests.get(REST_URL + '/block/' + block_hash + '.json').json()
        
    def process_tx(self, tx, timestamp):
        for vin in tx['vin']:
            if 'coinbase' in vin:
                continue
            delete_id = vin['txid'] + "_" + str(vin['vout'])
            self.delete_queue.append((delete_id,))
        index = 0
        for vout in tx['vout']:
            insert_id = tx['txid'] + "_" + str(index)
            try:
                address = self.script_handler.get_address_from_script(vout['scriptPubKey'])
            except:
                raise Exception("script['type'] unknown", tx)
            amount = int(vout['value'] * COIN)
            if amount > 0:
                self.insert_queue.append((insert_id, address, amount, timestamp))
            index += 1
        
    def clear(self):
        self.insert_queue = []
        self.delete_queue = []
        
class LitecoinScriptHandler:
    def get_address_from_script(script):
        if 'addresses' in script:
            address = script['addresses'][0]
        elif script['type'] == 'pubkey':
            address = script['asm'].split(" ")[0]
        elif script['type'] == 'nonstandard':
            address = "UNKNOWN"
        elif script['type'] == 'nulldata':
            address = "UNKNOWN"
        elif script['type'] == 'witness_mweb_hogaddr':
            address = "hogwarts"
        elif script['type'] == 'witness_mweb_pegin':
            address = "hogwarts"
        else:
            raise Exception("script['type'] unknown", script['type'])
        return address
       
class StatWriter:        
    def compute_address_distribution(self, date, db):
        results = [0 for i in range(16)]
        for row in db.cur.execute("""SELECT SUM(amount) FROM utxo GROUP BY address;"""):
            amount = row[0]
            if amount:
                results[int(math.log10(amount))] += amount
        row = [date.strftime('%Y-%m-%d')] + results
        self.append(ADDRESSES_NAME, row)
        
    def compute_age_distribution(self, date, db):
        results = [0 for i in range(16)]
        for row in db.cur.execute("""SELECT timestamp, amount FROM utxo;"""):
            utxo_timestamp = row[0]
            days_since = max((date.timestamp() - utxo_timestamp)/86400,1)
            results[int(math.log2(days_since))] += row[1]
        row = [date.strftime('%Y-%m-%d')] + results
        self.append(AGE_NAME, row)
        
    def append(self, filename, results):
        with open(filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(results)
        
class UTXODatabase:
    def __init__(self):
        self.con = sqlite3.connect(DATABASE_FILENAME)
        self.cur = self.con.cursor()
        
    def insert(self, insert_queue):
        self.cur.executemany("INSERT INTO utxo (hash, address, amount, timestamp) VALUES (?, ?, ?, ?)", insert_queue)
        self.con.commit()
        
    def delete(self, delete_queue):
        self.cur.executemany("DELETE FROM utxo WHERE hash = (?);", delete_queue)
        self.con.commit()

class Timer:
    def __init__(self):
        self.time_lookup = {}
        
    def start(self, tag):
        self.time_lookup[tag] = time.time()
        
    def finish(self, tag):
        duration = time.time() - self.time_lookup[tag]
        print(tag, duration)
        del self.time_lookup[tag]
    
def remove_file(filename):
    try:
        os.remove(filename)
    except FileNotFoundError:
        pass
    
def confirm(desc):
    answer = input(desc + " Continue? (y/yes)")
    if answer.lower() not in ["y","yes"]:
        raise Exception("Failed to proceed: use y/yes to continue.")
    
def init_files():
    confirm("Resetting build directory.")
    remove_file(ADDRESSES_FILENAME)
    remove_file(AGE_FILENAME)
    remove_file(DATABASE_FILENAME)
    con = sqlite3.connect(DATABASE_FILENAME)
    cur = con.cursor()
    cur.execute("CREATE TABLE utxo(id INTEGER PRIMARY KEY AUTOINCREMENT, hash, address, amount INTEGER, timestamp INTEGER)")
    cur.execute("CREATE UNIQUE INDEX id_hash ON utxo (hash);")
   

def run_from_block(start_height = 0, start_timestamp = None, start_block_hash = GENESIS_HASH):
    if start_height == 0 and not start_timestamp and start_block_hash == GENESIS_HASH:
        init_files()
    else:
        confirm("Reusing preexisting build directory.")
            
    parser = BlockParser(script_handler = LitecoinScriptHandler())
    db = UTXODatabase()
    stat = StatWriter()
    timer = Timer()
    block = parser.getblock(start_block_hash)
    
    block_hash = block['hash']
    if block_hash != GENESIS_HASH:
        start_height = block['height']
        
    day = datetime.utcfromtimestamp(block['time'])
    
    while start_timestamp and block['time'] < start_timestamp:
        block = parser.getblock(block_hash)
        day = datetime.utcfromtimestamp(block['time'])
        block_hash = block['nextblockhash']
    
    for i in range(start_height,10**7):
        block = parser.getblock(block_hash)
        block_day = datetime.utcfromtimestamp(block['time'])
        if block_day.day != day.day:
            timer.start("db_insert" + str(day) + "_" + str(i))
            db.insert(parser.insert_queue)
            timer.finish("db_insert" + str(day) + "_" + str(i))
            timer.start("db_delete" + str(day) + "_" + str(i))
            db.delete(parser.delete_queue)
            parser.clear()
            timer.finish("db_delete" + str(day) + "_" + str(i))
            timer.start("utxo_age_" + str(day) + "_" + str(i))
            stat.compute_age(day, db)
            timer.finish("utxo_age_" + str(day) + "_" + str(i))
            timer.start("utxo_address_" + str(day) + "_" + str(i))
            stat.compute_address(day, db)
            timer.finish("utxo_address_" + str(day) + "_" + str(i))
            day = block_day
        print(i)
        for tx in block['tx']:
            parser.process_tx(tx, block['time'])
        block_hash = block['nextblockhash']
        
if __name__ == "__main__":
    run_from_block()
        
