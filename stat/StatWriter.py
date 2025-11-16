import csv
import math 
from env import ADDRESSES_NAME, AGE_NAME

class StatWriter:        
    def __init__(self, filename):
        self.filename = filename
        
    def append(self, results):
        with open(self.filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(results)
        
