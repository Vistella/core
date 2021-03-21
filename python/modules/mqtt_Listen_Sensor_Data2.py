#------------------------------------------
#--- Author: Pradeep Singh
#--- Date: 20th January 2017
#--- Version: 1.0
#--- Python Ver: 2.7
#--- Details At: https://iotbytes.wordpress.com/store-mqtt-data-from-sensors-into-sql-database/
#------------------------------------------

import paho.mqtt.client as mqtt
import struct
import matplotlib.pyplot as plt

power = []

# MQTT Settings 
MQTT_Broker = "192.168.0.29"
MQTT_Port = 1883
Keep_Alive_Interval = 45
MQTT_Topic = "#"

#Subscribe to all Sensors at Base Topic
def on_connect(client, userdata, flags, rc):
  mqttc.subscribe(MQTT_Topic, 0)
  print("Connected")

#Save Data into DB Table
def on_message(mosq, obj, msg):
	# This is the Master Call for saving MQTT Data into DB
	# For details of "sensor_Data_Handler" function please refer "sensor_data_to_db.py"
	decodedPayload = msg.payload.decode("utf-8")
	print("MQTT Topic: " + msg.topic + ": " + decodedPayload)
	sensor_Data_Handler(msg.topic, decodedPayload)

def on_subscribe(mosq, obj, mid, granted_qos):
    pass

def sensor_Data_Handler(Topic, jsonData):
	if Topic == "Power":
		power.append(float(jsonData))
		if len(power) % 100 == 0:
			plt.plot(power)

mqttc = mqtt.Client()

# Assign event callbacks
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe

# Connect
mqttc.connect(MQTT_Broker, int(MQTT_Port), int(Keep_Alive_Interval))

# Continue the network loop
mqttc.loop_forever()
