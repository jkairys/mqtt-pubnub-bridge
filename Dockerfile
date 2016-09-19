FROM python:3.5
RUN pip3 install paho-mqtt pubnub
RUN mkdir /opt/app
COPY main.py /opt/app

CMD ["python3", "/opt/app/main.py"]

