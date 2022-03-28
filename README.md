### Project: Wikimedia
A project that decides whether to ingest the latest data based on the update timestamp of the latest folder. when the current latest date from the website is not the same as the previous date within the application, the data pipeline will start by first downloading the zipped dump files into the downloads folder which is mounted on the airflow container. the application is build with scability in mind, there are 4 folders mounted: downloads, dags, logs and plugins. this is for further extension if there is a need to do customed plugins. 

the api component is done using fastapi which provides classification of endpoints by tags. there are 2 endpoints:
- /query for submitting general query.
- /outdated_post for querying the most outdated page.

airflow UI can be found at http://VM_external_vm:8080
fastapi UI can be found at http://VM_external_vm:8000/docs

### Technologies used:
Technologies used:
- docker-compose
- docker
- python
- bash
- mysql and postgresql.

main data pipeline is built based on a customed apache airflow image with some additional packages installed for the customised task in the dag. metadata for airflow is hosted on postgresql, the data from Wikipedia is on the mysql.

airflow scheduler, webserver, triggerer, celery-worker, mysql and postgresql are spin up using docker-compose.

fastapi is used for the frontend UI. it is hosted on gunicorn and deployed on the cloud machine as a systemd application.

### getting started and deployment commands

The following is for getting the docker container to be up.
```
sudo apt-get update && sudo apt-get upgrade
sudo apt-get install git
git clone https://github.com/alanriya/glowing-giggles.git
cd ~/glowing-giggles
sudo apt-get install docker.io
sudo chmod 666 /var/run/docker.sock
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker build . --pull --tag extending_airflow:latest
echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env
echo -e "DATABASE_HOSTNAME=localhost\nDATABASE_PORT=3306\nDATABASE_PASSWORD=airflow\nDATABASE_USERNAME=airflow\nDATABASE_NAME=airflow" >> .env
docker-compose up airflow-init
docker-compose -f docker-compose.yaml up -d
nohup python external_automation/run_insert.py &
```
After docker-compose shows all services are healthy, go to the mysql docker container, 

In /etc/mysql/conf.d/mysql.cnf, below [mysql], add in
user=airflow
password=airflow

This is to ensure no password is needed when accessing mysql server.

The following is for deploying the fastapi app:
```
sudo apt install python3.9-venv
python -m venv .api
source .api/bin/activate
pip install -r app/requirements.txt
```

The following is for making fastapi to service:

copy .service file to /etc/systemd/system,

```
sudo systemctl start service_name.service 
sudo systemctl status service_name.service 
sudo systemctl enable service_name.service 
```
### Some useful commands:
For docker:
- remove all docker container: docker system prune --all --volumes
- remove orphan container: docker-compose down --volumes --remove-orphans

For docker-compose:
- bring up the container: docker-compose -f docker-compose.yaml up -d
- bring down the docker container: docker-compose down

For google cloud platform:
- To expose the ports so that the application can be found on public ip,
```
gcloud compute firewall-rules create default-allow-http-80 \
    --allow tcp:80 \
    --source-ranges 0.0.0.0/0 \
    --target-tags http-server \
    --description "Allow port 80 access to http-server"
```

### Some improvements to make project more robust
- test cases for dags
- CD/CI deployment using github action