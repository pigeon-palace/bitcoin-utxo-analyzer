import requests
from env import COIN, REST_URL
#1410432
class BlockParser:
    def __init__(self):
        self.delete_queue = []
        self.insert_queue = []
        
    def getblock(self, block_hash):
        return requests.get(REST_URL + '/block/' + block_hash + '.json').json()
        
    def process_tx(self, tx, timestamp):
        for vin in tx['vin']:
            if 'coinbase' in vin:
                continue
            delete_hash = vin['txid'] + "_" + str(vin['vout'])
            self.delete_queue.append((delete_hash,))
        index = 0
        for vout in tx['vout']:
            insert_hash = tx['txid'] + "_" + str(index)
            address = self.get_address_from_script(vout['scriptPubKey'])
            amount = int(vout['value'] * COIN)
            if amount > 0:
                self.insert_queue.append((insert_hash, address, amount, timestamp))
            index += 1
    
    def get_address_from_script(self, script):
        if 'addresses' in script:
            address = script['addresses'][0]
        else:
            if script['type'] != 'pubkey':
                if script['type'] == 'nonstandard':
                    return "UNKNOWN"
                if script['type'] == 'nulldata':
                    return "UNKNOWN"
                raise Exception("script['type'] unknown", script['type'])
            address = script['asm'].split(" ")[0]
        return address
        
    def clear(self):
        self.insert_queue = []
        self.delete_queue = []
        
