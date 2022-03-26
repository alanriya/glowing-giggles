from utils.urls import LATEST_CATEGORY, LATEST_STATS, LATEST_CATEGORYLINK, LATEST_PAGE, LATEST_PAGE_LINK, LATEST_TEMPLATE_LINK


def download_files():
    import requests
    for url in [LATEST_CATEGORY, LATEST_CATEGORYLINK, LATEST_PAGE, LATEST_PAGE_LINK, LATEST_TEMPLATE_LINK]:
        filename = url.split("/")[-1]
        local_file = f"/opt/airflow/downloads/{filename}"
        print(f"downloaded {local_file}")
        data = requests.get(url)
        
        with open(local_file, 'wb')as file:
            file.write(data.content)
        
        
    
    