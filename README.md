To install third party library in airflow, extend the docker image
## find the dockerfile in current folder to build.
docker build . --pull --tag extending_airflow:latest 

## add environment
echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env

./scripts/ci/tools/verify_docker_image.sh PROD extending_airflow:latest 

## docker compose to restart the 2 applications
docker-compose up -d --no-deps --build airflow-webserver airflow-scheduler airflow-triggerer

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

# In /etc/mysql/my.cnf
!includedir /etc/mysql/conf.d/
!includedir /etc/mysql/mysql.conf.d/
add this 
[mysql]
user=airflow 
password=airflow




# deploying to google cloud.
apt-get install git
apt-get install docker.io
sudo chmod 666 /var/run/docker.sock
docker build . --pull --tag extending_airflow:latest
docker-compose -f docker-compose.yaml up -d