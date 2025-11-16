import math 
from StatWriter import StatWriter

class UtxoAgeDistribution(StatWriter): 
    def compute(self, date, db):
        results = [0 for i in range(16)]
        for row in db.cur.execute("""SELECT timestamp, amount FROM utxo;"""):
            utxo_timestamp = row[0]
            days_since = max((date.timestamp() - utxo_timestamp)/86400,1)
            results[int(math.log2(days_since))] += row[1]
        row = [date.strftime('%Y-%m-%d')] + results
        self.append(AGE_NAME, row)
        
        
