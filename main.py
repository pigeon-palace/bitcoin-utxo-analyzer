from datetime import datetime  
from parse.BlockParser import BlockParser
from parse.LitecoinScriptHandler import LitecoinScriptHandler
from stat.UtxoAddressDistribution import UtxoAddressDistribution
from stat.UtxoAgeDistribution import UtxoAgeDistribution
from UTXODatabase import UTXODatabase
from Timer import Timer
from env import GENESIS_HASH, init_files, AGE_NAME, ADDRESS_NAME


def run_from_block(start_height = 0, start_timestamp = None, start_block_hash = GENESIS_HASH):
    if start_height == 0 and not start_timestamp and start_block_hash == GENESIS_HASH:
        init_files()
    parser = BlockParser(script_handler = LitecoinScriptHandler)
    db = UTXODatabase()
    utxo_age = UtxoAgeDistribution(AGE_NAME)
    utxo_address = UtxoAddressDistribution(ADDRESS_NAME)
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
            utxo_age.compute(day, db)
            timer.finish("utxo_age_" + str(day) + "_" + str(i))
            timer.start("utxo_address_" + str(day) + "_" + str(i))
            utxo_address.compute(day, db)
            timer.finish("utxo_address_" + str(day) + "_" + str(i))
            day = block_day
        print(i)
        for tx in block['tx']:
            parser.process_tx(tx, block['time'])
        block_hash = block['nextblockhash']
        
if __name__ == "__main__":
    run_from_block()
        
