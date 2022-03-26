FROM apache/airflow:2.2.4
COPY requirements.txt /requirements.txt
USER airflow
RUN pip install --user --upgrade pip 
RUN pip install --no-cache-dir --user -r /requirements.txt 