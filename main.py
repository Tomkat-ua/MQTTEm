# python3.6
#### Energy monitor MQTT extractor

import datetime
import calendar
# import MySQLdb
import random
from paho.mqtt import client as mqtt_client
from prometheus_client import start_http_server, Gauge
from time import sleep as sleep
from datetime import datetime
from os import environ as environ
from sys import argv

appver = "0.2.1"
appname = "Energy monitor MQTT extractor"
appshortname = "MQTTEm"
print(appname + " ver. "+appver)
tab='  |'
env = argv[1]



if env == 'prod':
    server_port =int(environ.get('SERVER_PORT'))
    get_delay = int(environ.get('GET_DELAY'))
    broker = environ.get('BROKER_IP')
    port = int(environ.get('BROKER_PORT'))
    username = environ.get('USERNAME')
    password = environ.get('PASSWORD')
    sensor_real_counter_name = environ.get('SENSOR_REAL_COUNTER_NAME')
    sensor_real_counter_value = float(environ.get('SENSOR_REAL_COUNTER_VALUE'))
    topic_pattern = environ.get('TOPIC_PATTERN')
else:
    server_port=int('8081')
    get_delay = 5
    broker = 'ha.tomkat.cc'
    port = 1883
    username = 'mqtt'
    password = 'mqtt001'
    sensor_real_counter_name = 'energy_meter'
    sensor_real_counter_value = 25821
    topic_pattern = "monitors/+/#"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'

MQTT_VALUE = Gauge('esphome_sensor_state', 'topic', ['device','topic','sensor','data','device_location'])
APP_INFO = Gauge('app_info', 'Return app info',['appname','appshortname','version','env'])
APP_INFO.labels(appname,appshortname,appver,env).set(1)

device_location = ''

def get_time():
    date = datetime.utcnow()
    utc_time = calendar.timegm(date.utctimetuple())
    return(utc_time)

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def logformer(topic,message):
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    print(date_time + ": " + topic +": " + message)

def ins_to_db(device,topic,sensor,data):
    db=MySQLdb.connect(host="192.168.2.7",user="em",password="Emm",database="em", charset="utf8")
    cursor = db.cursor()
    if topic == 'status':
        query = "CALL DEVICES_STATUS_UPD (%s, %s, %s)"
        cursor.execute(query, (device,data,datetime.now()))
    if topic == 'sensor' or topic == 'binary_sensor':
        query = "CALL STATES_INS (%s, %s, %s , %s, %s)"
        cursor.execute(query, (device,sensor,data,datetime.now(),get_time()))
    db.commit()
    cursor.close()
    db.close()
##############

def subscribe(client: mqtt_client):
    device_status = 0
    def on_message_data(client, userdata, msg):
        nonlocal device_status
        topic_name = msg.topic.replace("-", "_")
        topic_data = topic_name.split("/")
        device = topic_data[1]
        topic = topic_data[2]
        data = msg.payload.decode()
        if topic == 'debug' and env == 'prod':
            logformer(device, data)
        if topic == 'sensor':
            sensor = topic_data[3]
            set_metrica(device, topic, sensor, data)
        if topic == 'status':
            sensor = device
            if data == 'online':
                data = 1
                device_status = 1
            else:
                data = 0
                device_status = 0
                set_metrica(device, topic, sensor, data)
            set_metrica(device, topic, sensor, data)

    client.subscribe(topic_pattern)
    client.on_message = on_message_data
    sleep(get_delay)

def set_metrica(device,topic,sensor,data):
    try:
        if sensor == 'location':
            global device_location
            device_location = data
        data = float(data)
        if sensor in sensor_real_counter_name:
            data = data + sensor_real_counter_value
        MQTT_VALUE.labels(device,topic,sensor,'value',device_location).set(data)
    except  ValueError as e:
        MQTT_VALUE.labels(device,topic,sensor,data,device_location).set(0)

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

if __name__ == '__main__':
    try:
        start_http_server(server_port)
    except Exception as e: print(e)
    while True:
        run()

