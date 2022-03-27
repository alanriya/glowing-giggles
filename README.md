To install third party library in airflow, extend the docker image
## find the dockerfile in current folder to build.
docker build . --pull --tag extending_airflow:latest 

## add environment
echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env

./scripts/ci/tools/verify_docker_image.sh PROD extending_airflow:latest 

## docker compose to restart the 2 applications
docker-compose up -d --no-deps --build airflow-webserver airflow-scheduler airflow-triggerer

## docker-compose command
docker-compose -f docker-compose.yaml up -d

## create airflow with user of airflow and password of airflow
docker-compose up airflow-init

## testing dags
airflow tasks test dag_id task_id 2022-03-21



## increase the size of mysql to load larger database
docker exec -it my_mysql bash -c "echo 'max_allowed_packet = 1024M' >> /etc/mysql/mysql.conf.d/mysqld.cnf" 
docker restart my_mysql

# get the docker container id
VAR=$(docker ps | grep mysql | awk '{print $1}')
# log on to the container bash and insert the sql scripts.
docker exec -it $VAR /bin/bash -c dir

# In /etc/mysql/conf.d/mysql.cnf
<!-- !includedir /etc/mysql/conf.d/
!includedir /etc/mysql/mysql.conf.d/ -->
add this 
[mysql]
user=airflow 
password=airflow

## delete all volume
docker system prune --all --volumes
docker-compose down --volumes --remove-orphans

# after setting up, expose port 8080 and 8000
gcloud compute firewall-rules create default-allow-http-80 \
    --allow tcp:80 \
    --source-ranges 0.0.0.0/0 \
    --target-tags http-server \
    --description "Allow port 80 access to http-server"


# deploying to google cloud.
sudo apt-get update && sudo apt-get upgrade
sudo apt-get install git
sudo apt-get install docker.io
sudo chmod 666 /var/run/docker.sock
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker build . --pull --tag extending_airflow:latest
echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env
sudo chmod -R 777 logs
docker-compose up airflow-init
docker-compose -f docker-compose.yaml up -d

# deploying the fastapi app as a service
sudo apt install python3.9-venv
python -m venv .api
source .api/bin/activate
pip install -r app/requirements.txt


sudo adduser alan
# copy .service file to /etc/systemd/system
# edit the root folders.
sudo systemctl start gunicornLynx.service 
sudo systemctl status gunicornLynx.service 
sudo systemctl enable gunicornLynx.service 

sudo systemctl start externalAutomation.service 
sudo systemctl status externalAutomation.service 
sudo systemctl enable externalAutomation.service 




# deploying the external loading process as a service