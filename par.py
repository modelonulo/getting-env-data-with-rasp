hostMqtt = "tailor.cloudmqtt.com"
user = "qvxzamte"
password = "m-5pfX9Fu9IR"
port = 18615
apiKey = "54e11171-8d33-4e0c-9759-3fcf7085be61"

import geocoder
import datetime
import os
import paho.mqtt.client as mosquitto
import time
from datetime import datetime, timezone, timedelta
import RPi.GPIO as GPIO
import Adafruit_DHT # camila
import requests # camila

mqttc = mosquitto.Client()
GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)

GPIO.output(12, 0) # desliga o rele

#mqtt
# Define event callbacks
def on_connect(mosq, obj, rc, extra):
    print("rc: " + str(rc))
    mqttc.subscribe("PUCPR/OMIoT/CarolineStoffelCamilaLima2020/alerta") 

def on_message(mosq, obj, msg):
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    if msg.topic == "PUCPR/OMIoT/CarolineStoffelCamilaLima2020/alerta":
        print('mensagem de alerta: ', int(msg.payload))
        try:
            rele = bool(msg.payload.decode('utf-8') == "1")
            print("rele ligado", rele)
            GPIO.output(12, rele)
             # mensagem de alerta vai ser 0 ou 1
        except Exception as err:
            print(err)    
           
def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mosq, obj, level, string):
    print(string)

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


# cria lista para armazenar 60 dados
lista60=[]

dia_de_inicio = 7

start_time = time.time() # inicializa
# Continue the network loop, exit when an error occurs
rc = 0
while True:
    if rc != 0:
       print("rc: " + str(rc))
       mqttc.disconnect()
       mqttc.connect(hostMqtt, port)
       rc = mqttc.loop()
    rc = mqttc.loop()
    elapsed = time.time() - start_time # calcula o tempo passado
    if elapsed > 60: # se passou mais de 60 segundos entra no if
        start_time = time.time() # nao esquecer essa linha para resetar o tempo.
        id_ = '7A819C2C8F79764C20967F2DB2459598'

        # informacao de tempo
        data_e_hora_atuais = datetime.now()
        diferenca = timedelta(hours=-3)
        fuso_horario = timezone(diferenca)
        data_e_hora_sao_paulo = data_e_hora_atuais.astimezone(fuso_horario)
        data, tempo = data_e_hora_sao_paulo.strftime('%Y-%m-%d %H:%M:%S').split(' ')
        hora, minuto, segundo = tempo.split(':')
        ano, mes, dia = data.split('-')
        # Removendo o 0 antes da hora, caso exista
        if hora[0] == '0':
           hora = hora[1]
        # Removendo o 0 antes do minuto, caso exista
        if minuto[0] == '0':
           minuto = minuto[1]
        # Removendo o 0 antes do mes, caso exista
        if mes[0] == '0':
           mes = mes[1]
        # Removendo o 0 antes do dia, caso exista
        if dia[0] == '0':
           dia = dia[1]
 

        # medicao de temperatura
        #OBS: caso ocorra erro, rodar no terminal: "pgrep libgpiod" -> "kill processo",  linux stuff  
        ######## dhtDevice = adafruit_dht.DHT11(board.D25) # D25 significa conectado no pino 25

        humidade, temperatura = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 25) # rodrigo

        ##### temperatura = retorna_temperatura()
        temperatura = str(temperatura)
        print("temp=",temperatura)





        # latitude e longitude
       
        try:
            response = requests.get('https://ifconfig.me/') 
            ip_addr = response.content.decode('utf-8') 

            g = geocoder.ip(ip_addr) 
            latitude, longitude = g.latlng
            latitude = str(latitude)
            longitude = str(longitude)
        except:
            # se ocorre um erro, envia as coordenadas do google maps
            latitude = '-24.708505'
            longitude = '-53.749052'
 

        dt = datetime.today()
        diff = dt.day - dia_de_inicio # calcula os dias passado desde 07/09/2020
        raio = 0.05
        print('diferenca de dias', diff)

        if diff == 0:
            latitude = float(latitude)
            longitude = float(longitude)
        elif diff == 1:
            latitude = float(latitude) + 1*raio
            longitude = float(longitude) + 1*raio
        elif diff == 2:
            latitude = float(latitude) + 2*raio
            longitude = float(longitude) +2*raio
        elif diff == 3:
            latitude = float(latitude) + 3*raio
            longitude = float(longitude) + 3*raio
        elif diff == 4:
            latitude = float(latitude) + 4*raio
            longitude = float(longitude) + 4*raio
        elif diff == 5:
            latitude = float(latitude) + 5*raio
            longitude = float(longitude) + 5*raio
        elif diff == 6:
            latitude = float(latitude) + 6*raio
            longitude = float(longitude) + 6*raio

        latitude = str(latitude)
        longitude = str(longitude)

        # Dados para serem enviados a cada 60 segundos
        dados = id_ + ';' + dia + ';' + mes + ';' + ano + ';' + hora + ';' + minuto + \
                   ';' + temperatura + ';' + latitude + ';' + longitude

        # publica a variavel dados no topico valores_instantaneos
        mqttc.publish("PUCPR/OMIoT/CamilaLima2020/valores_intantaneos", dados)
        # faz um subscribe no topico alerta
        mqttc.subscribe("PUCPR/OMIoT/CamilaLima2020/alerta", 0)
        #salva na lista60, para fazer as medicoes posteriores
        lista60.append(dados.split(';'))



    #print('len lista = ', len(lista60))
    # calculos de medias, min e max p/ o topico valores_medios
    if len(lista60) == 60:# se foram adicionados 60 dados, significa q passou 60 min

        media_hora = float()
        media_minuto = float()
        minima_temp = lista60[0][6]
        maxima_temp = lista60[0][6]
        media_latitude = float()
        media_longitude = float()
        soma_hora = int()
        soma_minuto = int()
        soma_latitude = float()
        soma_longitude = float()
        quantidade = len(lista60)

        # p/ debug de min e max temperatura, apenas p/ testes
        #maxima_temp = 0
        #minima_temp = 100
        
        try:
            for i in range(0, quantidade):
                soma_hora += int(lista60[i][4])
                soma_minuto += int(lista60[i][5])
                soma_latitude += float(lista60[i][7])
                soma_longitude += float(lista60[i][8])
                if lista60[i][6] != '':
                    if float(lista60[i][6]) < float(minima_temp):
                        minima_temp = float(lista60[i][6])
                    if float(lista60[i][6]) > float(maxima_temp):
                        maxima_temp = float(lista60[i][6])
                    
            media_hora = soma_hora / quantidade
            media_minuto = soma_minuto / quantidade
            media_latitude = soma_latitude / quantidade
            media_longitude = soma_longitude / quantidade
        except:
            dados60min = ''

        # dados para serem enviados a cada 60 min
        dados60min = str(media_hora)+';'+str(media_minuto)+';'+str(minima_temp)+';'+str(maxima_temp)+';'+str(media_latitude)+';'+str(media_longitude)
        # codigo do broker p/ envio
        #mqttc.connect(hostMqtt, port)
        # Publish a message no topico valores_medios
        mqttc.publish("PUCPR/OMIoT/CamilaLima2020/valores_medios", dados60min)        
        #mqttc.disconnect()
        lista60 = []

    # aguarda 1 segundos p/ recomecar
    time.sleep(1)
