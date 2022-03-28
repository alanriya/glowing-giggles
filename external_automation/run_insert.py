import os, sys
import time
sys.path.append(os.getcwd())
from os import listdir

current_dir = "/home/alan/snakey/airflow-template"
class InsertWatcher:
    def __init__(self):
        pass
    
    def watch_and_insert(self):
        """"
        An infinite loop that watches a certain file in the downloads folder.
        
        When True, run the insert script
        """
        while True:
            if "insert" in listdir(f"{current_dir}/downloads"):
                print("starting_insert")
                os.system(f"{current_dir}/downloads/insertData.sh")
                print("insert done")
                os.system(f"rm {current_dir}/downloads/insert")
                print("remove insert file")
                os.system(f"touch {current_dir}/downloads/compute")
                print("created compute file")
            time.sleep(5) 
    
if __name__ == "__main__":
    InsertWatcher().watch_and_insert()


