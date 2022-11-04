FROM python:3.8.10-slim-buster

RUN apt update \
	&& apt install -y curl \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /opt/alloxentric

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . /opt/alloxentric

EXPOSE 5050

#CMD ["python3", "app.py"]

CMD ["gunicorn", "app:app", "-w", "1", "--worker-class", "eventlet", "-b", "0.0.0.0:5050", "--log-config", "log.conf"]
