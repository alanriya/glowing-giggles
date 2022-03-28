VAR=$(docker ps | grep mysql | awk '{print $1}')
# execute the insert
docker exec -it $VAR /bin/bash -c "mysql -u airflow airflow < /opt/airflow/downloads/simplewiki-latest-category.sql"
# docker exec -it $VAR /bin/bash -c "mysql -u airflow airflow < /opt/airflow/downloads/simplewiki-latest-categorylinks.sql"
# docker exec -it $VAR /bin/bash -c "mysql -u airflow airflow < /opt/airflow/downloads/simplewiki-latest-page.sql"
# docker exec -it $VAR /bin/bash -c "mysql -u airflow airflow < /opt/airflow/downloads/simplewiki-latest-pagelinks.sql"
# docker exec -it $VAR /bin/bash -c "mysql -u airflow airflow < /opt/airflow/downloads/simplewiki-latest-templatelinks.sql"