from datetime import datetime  
from BlockParser import BlockParser, LitecoinScriptHandler
from UTXODatabase import UTXODatabase
from StatWriter import StatWriter
from Timer import Timer
from env import GENESIS_HASH, init_files


def run_from_block(start_height = 0, start_timestamp = None, start_block_hash = GENESIS_HASH):
    if start_height == 0 and not start_timestamp and start_block_hash == GENESIS_HASH:
        init_files()
    parser = BlockParser(script_handler = LitecoinScriptHandler)
    db = UTXODatabase()
    writer = StatWriter()
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
            timer.start("compute_" + str(day) + "_" + str(i))
            db.insert(parser.insert_queue)
            db.delete(parser.delete_queue)
            parser.clear()
            writer.write_address_distribution(day, db)
            writer.write_age_distribution(day, db)
            timer.finish("compute_" + str(day) + "_" + str(i))
            day = block_day
        print(i)
        for tx in block['tx']:
            parser.process_tx(tx, block['time'])
        block_hash = block['nextblockhash']
        
if __name__ == "__main__":
    run_from_block(start_block_hash = "87b8ebea75041a14bbfe870785f9025f788330c50c78b5cacab7685a12b0b355")
        
