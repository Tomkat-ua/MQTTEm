# python3.6
#### Energy monitor MQTT extractor
import datetime
import calendar
import MySQLdb
appver = "0.0.1"
appname = "Energy monitor MQTT extractor"
appshortname = "MQTTEm"

import random

from paho.mqtt import client as mqtt_client

from time import sleep as sleep
from datetime import datetime
# from os import environ as environ
import os
#import bot,asyncio

# os.environ['TZ'] = 'Europe/London'

print(appname + " ver. "+appver)
tab='  |'

env ='dev' #prod

if env == 'prod':
    server_port =int(environ.get('SERVER_PORT'))
    get_delay = int(environ.get('GET_DELAY'))
    broker = environ.get('BROKER_IP')
    port = int(environ.get('BROKER_PORT'))
    topic_pattern = environ.get('TOPIC')
    username = environ.get('USERNAME')
    password = environ.get('PASSWORD')
else:
    server_port=int('8081')
    get_delay = 10
    broker = '192.168.2.7'
    port = 1883

    username = 'mqtt'
    password = 'mqtt001'

# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
# topic_pattern = "monitors/+/debug/#"



# topic_pattern = "monitors/+/sensor/#"
# MQTT_VALUE = Gauge('esphome_sensor_state', 'topic', ['device_type','device_name','sensor_type','sensor_name','data'])
# APP_INFO = Gauge('app_info', 'Return app info',['appname','appshortname','version'])
# APP_INFO.labels(appname,appshortname,appver).set(1)


def get_time():

    date = datetime.utcnow()
    utc_time = calendar.timegm(date.utctimetuple())
    return(utc_time)

    # presentDate = datetime.now()
    # unix_timestamp = datetime.timestamp(presentDate)*1000
    # return(unix_timestamp)
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
    # if e == 0:
        # print(date_time +  " : Received " + message + " from " + topic + " topic")
    print(date_time + ": " + topic +": " + message)
    # else:
    #     print(date_time + " : Text value in topic : " + topic + " -- "+ message)

###############
def ins_to_db(device,topic,sensor,data):
    db=MySQLdb.connect(host="192.168.2.7",user="em",password="Emm",database="em", charset="utf8")
    cursor = db.cursor()
    if topic == 'status':
        query = "CALL DEVICES_STATUS_UPD (%s, %s, %s)"
        cursor.execute(query, (device,data,datetime.now()))
    if topic == 'sensor' or topic == 'binary_sensor':
        # print(get_time())
        # print(device+':'+sensor+':'+data)
        query = "CALL STATES_INS (%s, %s, %s , %s, %s)"
        cursor.execute(query, (device,sensor,data,datetime.now(),get_time()))
   # datetime.now(),
    db.commit()
    cursor.close()
    db.close()
    # time.sleep(10)
##############

def subscribe(client: mqtt_client):
    def on_message_data(client, userdata, msg):

        topic_name = msg.topic.replace("-", "_")
        topic_data = topic_name.split("/")
        # set_metrica(topic_data[0],topic_data[1],topic_data[2],topic_data[3],topic_data[4],value)
        device = topic_data[1]
        topic = topic_data[2]
        sensor = ''
        data = msg.payload.decode()
        if topic == 'sensor':
            sensor = topic_data[3]
            ins_to_db(device,topic,sensor,data)
        if topic == 'debug':
        #     # logformer(msg.topic, value)
            logformer(device, data)

        if topic == 'status':
            # print(device+':'+data)
            ins_to_db(device,topic,sensor,data)



    # topic_pattern = "monitors/+/sensor/#"
    topic_pattern = "monitors/+/#"
    client.subscribe(topic_pattern)
    client.on_message = on_message_data

    # topic_pattern = "monitors/+/debug/"
    # client.subscribe(topic_pattern)
    # client.on_message = on_message_log

# def set_metrica(p0,p1,p2,p3,p4,value):
#     try:
#         value = float(value)
#         MQTT_VALUE.labels(p0,p1,p2,p3,p4).set(value)
#     except  ValueError as e:
#         logformer(p0+'/'+p1+'/'+p2+'/'+p3+'/'+p4,value,1)
#         # print(e)
#         MQTT_VALUE.labels(p0,p1,p2,p3,value).set(0)

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

if __name__ == '__main__':
    try:
    #     start_http_server(server_port)
        run()
        sleep(get_delay)
    except Exception as e: print(e)
    # while True:
    #     run()
    #     sleep(get_delay)
