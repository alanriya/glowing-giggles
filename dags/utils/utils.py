import pdb

def get_latest_date():
    latest_date = None
    with open("./downloads/filedate.txt", "r") as f:
        lines = f.readlines()
        lines = [i.strip().replace("/", '') for i in lines]
        latest_date = lines[-1]
    return latest_date
        
if __name__ == "__main__":
    print( get_latest_date())