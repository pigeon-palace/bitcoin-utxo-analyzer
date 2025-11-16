import csv
import math 
from StatWriter import StatWriter

class UtxoAddressDistribution(StatWriter):        
    def compute(self, date, db):
        results = [0 for i in range(16)]
        for row in db.cur.execute("""SELECT SUM(amount) FROM utxo GROUP BY address;"""):
            amount = row[0]
            if amount:
                results[int(math.log10(amount))] += amount
        results = [date.strftime('%Y-%m-%d')] + results
        self.append(ADDRESSES_NAME, results)
            
