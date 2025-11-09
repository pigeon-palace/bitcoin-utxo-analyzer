import os
import csv
import sqlite3

GENESIS_HASH = "80ca095ed10b02e53d769eb6eaf92cd04e9e0759e5be4a8477b42911ba49c78f"
REST_URL = 'http://127.0.0.1:9332/rest'
DATABASE_NAME = "build/utxo.db"
ADDRESSES_NAME = "build/address_balance_distribution.csv"
AGE_NAME = "build/utxo_age_distribution.csv"
COIN = 10**8
ADDRESS_HEADER = ["date"] + [ str(10**i/COIN) + " <= x < " +str(10**(i+1)/COIN) for i in range(16)]
AGES_HEADER = ["date"] + [str(2**(i-1)) + " < x <= " + str(2**i) for i in range(16)]

def init_files():
    try:
        os.remove(ADDRESSES_NAME)
    except FileNotFoundError:
        pass

    with open(ADDRESSES_NAME, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(ADDRESS_HEADER)
        
    try:
        os.remove(AGE_NAME)
    except FileNotFoundError:
        pass


    with open(AGE_NAME, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(AGES_HEADER)
        
    try:
        os.remove(DATABASE_NAME)
    except FileNotFoundError:
        pass
        
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()
    cur.execute("CREATE TABLE utxo(id INTEGER PRIMARY KEY AUTOINCREMENT, hash, address, amount INTEGER, timestamp INTEGER)")
    cur.execute("CREATE UNIQUE INDEX id_hash ON utxo (hash);")
   
