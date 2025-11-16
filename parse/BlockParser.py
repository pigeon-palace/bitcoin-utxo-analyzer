import requests
from env import COIN, REST_URL
#1410432
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
        
