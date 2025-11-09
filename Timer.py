import time

class Timer:
    def __init__(self):
        self.time_lookup = {}
        
    def start(self, tag):
        self.time_lookup[tag] = time.time()
        
    def finish(self, tag):
        duration = time.time() - self.time_lookup[tag]
        print(tag, duration)
        del self.time_lookup[tag]
    
