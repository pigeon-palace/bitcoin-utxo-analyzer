from datetime import datetime  
from BlockParser import BlockParser
from UTXODatabase import UTXODatabase
from StatWriter import StatWriter
from Timer import Timer
from env import GENESIS_HASH, init_files


def run_from_block(start_height = 0, timestamp = None, block_hash = GENESIS_HASH):
    if start_height == 0 and not timestamp:
        init_files()
    parser = BlockParser()
    db = UTXODatabase()
    writer = StatWriter()
    timer = Timer()
    block = parser.getblock(block_hash)
    day = datetime.utcfromtimestamp(block['time'])
    for i in range(start_height,10**7):
        print(i)
        block = parser.getblock(block_hash)
        block_day = datetime.utcfromtimestamp(block['time'])
        if(timestamp and block['time'] < timestamp):
            day = block_day
            block_hash = block['nextblockhash']
            continue
        if block_day.day != day.day:
            timer.start("compute_" + str(day) + "_" + str(i))
            db.insert(parser.insert_queue)
            db.delete(parser.delete_queue)
            parser.clear()
            writer.write_address_distribution(day, db)
            writer.write_age_distribution(day, db)
            timer.finish("compute_" + str(day) + "_" + str(i))
            day = block_day
        for tx in block['tx']:
            parser.process_tx(tx, block['time'])
        block_hash = block['nextblockhash']
        
if __name__ == "__main__":
    run_from_block()
        
