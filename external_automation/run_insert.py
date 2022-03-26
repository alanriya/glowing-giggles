import os, sys
import time
sys.path.append(os.getcwd())
from os import listdir



class InsertWatcher:
    def __init__(self):
        pass
    
    def watch_and_insert(self):
        """"
        An infinite loop that watches a certain file in the downloads folder.
        
        When True, run the insert script
        """
        while True:
            if "insert" in listdir(f"{sys.path[-1]}/downloads"):
                os.system(f"{sys.path[-1]}/downloads/insertData.sh")
                os.system(f"rm {sys.path[-1]}/downloads/insert")
                os.system(f"touch {sys.path[-1]}/downloads/compute")
            time.sleep(5) 
    
if __name__ == "__main__":
    InsertWatcher().watch_and_insert()


