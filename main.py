# python3.6
#### Energy monitor MQTT extractor

import datetime
import calendar
import random
from paho.mqtt import client as mqtt_client
from prometheus_client import start_http_server, Gauge
from time import sleep as sleep
from datetime import datetime
from os import environ as environ
from sys import argv

appver = "0.3.1"
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
    # topic_pattern = "monitors/em2/+/#"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'

# MQTT_VALUE = Gauge('esphome_sensor_state', 'topic', ['device','topic','sensor','data','device_location'])
# METRICA_DEVICE = Gauge('esphome_device_state', 'ESPHome device state metrica', ['device','location','firmware_ver','wifi_ssid','wifi_ip','wifi_mac','device_status'])
METRICA_DEVICE = Gauge('esphome_device_state', 'ESPHome device state metrica', ['device','property','value'])
METRICA_SENSOR = Gauge('esphome_sensor_state', 'ESPHome sensor state metrica', ['device','sensor'])
APP_INFO = Gauge('app_info', 'Return app info',['appname','appshortname','version','env'])
APP_INFO.labels(appname,appshortname,appver,env).set(1)
################----------------------------------------------------------------------------------------------
class Device:
    device_name=''

class Topic():
    name=''
    raw=''
    data=''

################----------------------------------------------------------------------------------------------


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



##############

def subscribe(client: mqtt_client):
    em = Device()
    # device_name=''
    topic = Topic()
    def set_metrica(sensor, data):
        METRICA_DEVICE.labels(em.device_name, topic.name[2], sensor).set(data)

    def logformer():
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        print(date_time + ": " + em.device_name + ": " + topic.data)

    def on_message_data(client, userdata, msg):

        topic.raw = msg.topic
        topic.name = topic.raw.replace("-", "_")
        topic.data = msg.payload.decode()
        topic.name = topic.name.split("/")
        # device_name = topic.name[1]
        em.device_name = topic.name[1]
        if topic.name[2] == 'sensor':
            METRICA_SENSOR.labels(em.device_name,topic.name[3]).set(topic.data)
        else:
            if topic.name[2] == 'location':     set_metrica( topic.data, 0)
            if topic.name[2] == 'firmware_ver': set_metrica( topic.data, 0)
            if topic.name[2] == 'logs':         logformer()
            if topic.name[2] == 'status':
                if topic.data == 'online': set_metrica('', 1)
                else: set_metrica('', 0)
            if topic.name[2] == 'wifi_mac':  set_metrica(topic.data, 0)
            if topic.name[2] == 'wifi_ip':   set_metrica(topic.data, 0)
            if topic.name[2] == 'wifi_ssid': set_metrica(topic.data, 0)


    client.subscribe(topic_pattern)
    client.on_message = on_message_data
    sleep(get_delay)

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

