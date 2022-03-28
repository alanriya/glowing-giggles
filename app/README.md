### Project Title: fastapi endpoint for outdated page
This is a simple fastapi application that is able to receive query string from user and return the results in json format. It is also able to take in a category and return the most outdated page.

### Technologies used:
python fastapi library used extensively for this UI because of the ease of development. see requirement.txt files for the packages. 

### Some improvements: 
As of now the query string might be susceptible to sql injection because of the f string. 

Currently: 
```result = db.execute(f"""SELECT * FROM mostoutdatedpage WHERE category = '{category}'""")```
Tried but did not work: 
```result = db.execute(f"""SELECT * FROM mostoutdatedpage WHERE category = '${category}'""", {'category': category})```
```result = db.execute(f"""SELECT * FROM mostoutdatedpage WHERE category = '%s'""", (category,))```

### installation and running of the project
You should be at the repo root folder.

```
sudo apt install python3.9-venv
python -m venv .api
source .api/bin/activate
pip install -r app/requirements.txt
```

- To run in development quickly: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
- In production, it is deployed as a service. see example gunicorn.service file.

### gunicorn.service file in production
```                                       
[Unit]
Description=api application to query the result
After=network.target
[Service]
User=alan_leeyungchong
Group=alan_leeyungchong
WorkingDirectory=/home/alan_leeyungchong/glowing-giggles
Environment="PATH=/home/alan_leeyungchong/glowing-giggles/.api/bin"
EnvironmentFile=/home/alan_leeyungchong/glowing-giggles/.env
ExecStart=/home/alan_leeyungchong/glowing-giggles/.api/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
[Install]
WantedBy=multi-user.target
```
