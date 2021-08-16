import paho.mqtt.client as mosquitto
from urllib.parse import urlparse
import os
import csv

hostMqtt = "tailor.cloudmqtt.com"
user = "qvxzamte"
password = "m-5pfX9Fu9IR"
port = 18615
apiKey = "54e11171-8d33-4e0c-9759-3fcf7085be61"

# Define event callbacks

def on_connect(mosq, obj, rc, extra):
        # Start subscribe, with QoS level 0
    mosq.subscribe(
        "PUCPR/OMIoT/CamilaLima2020/valores_intantaneos", 0)
    mosq.subscribe(
        "PUCPR/OMIoT/CamilaLima2020/valores_medios", 0)

topico = "PUCPR/OMIoT/CamilaLima2020/"

def on_message(mosq, obj, msg):
    print('>>>', msg.topic + " " + str(msg.qos) + " " + str(msg.payload))    

    if "valores_intantaneos" in msg.topic:
        print('valores_intantaneos')
        data_inst = str(msg.payload.decode('utf-8')).split(';')
        print("data", data_inst)

        print("TEMP:", data_inst[6])
        temp = float(data_inst[6])
        with open('valores_intantaneos.csv', 'a', newline='') as valores_intantaneos_csv:
            writer = csv.writer(valores_intantaneos_csv)
            writer.writerow(data_inst)

        if temp >= 25.0:
            print('enviar alerta')
            mqttc.publish(
                "PUCPR/OMIoT/CamilaLima2020/alerta", "1")
        else:
            mqttc.publish(
                "PUCPR/OMIoT/CamilaLima2020/alerta", "0")

    if "valores_medios" in msg.topic:
        print('valores_medios')
        data_med = str(msg.payload.decode('utf-8')).split(';')
        with open('valores_medios.csv', 'a', newline='') as valores_medios_csv:
            writer = csv.writer(valores_medios_csv)
            writer.writerow(data_med)

def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed: " + str(obj) + str(mid) + " " + str(granted_qos))

def on_log(mosq, obj, level, string):
    print(string)

mqttc = mosquitto.Client()
# Assign event callbacks
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

# Uncomment to enable debug messages
mqttc.on_log = on_log

# Connect
mqttc.username_pw_set(user, password)
mqttc.connect(hostMqtt, port)

# Publish a message
#mqttc.publish("hello/world", "my message")

# Continue the network loop, exit when an error occurs

mqttc.loop_forever()
