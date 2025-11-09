import csv
import math 
from env import ADDRESSES_NAME, AGE_NAME

class StatWriter:        
    def write_address_distribution(self, date, db):
        results = [0 for i in range(16)]
        for row in db.cur.execute("""SELECT SUM(amount) FROM utxo GROUP BY address;"""):
            amount = row[0]
            if amount:
                results[int(math.log10(amount))] += amount
        results = [date.strftime('%Y-%m-%d')] + results
        self.append(ADDRESSES_NAME, results)
            
    def write_age_distribution(self, date, db):
        results = [0 for i in range(16)]
        for row in db.cur.execute("""SELECT timestamp, amount FROM utxo;"""):
            utxo_timestamp = row[0]
            days_since = max((date.timestamp() - utxo_timestamp)/86400,1)
            results[int(math.log2(days_since))] += row[1]
        results = [date.strftime('%Y-%m-%d')] + results
        self.append(AGE_NAME, results)
        
    def append(self, filename, results):
        with open(filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(results)
        
