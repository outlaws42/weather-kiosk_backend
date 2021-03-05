#! /usr/bin/env python3

# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import time
import datetime
import pymongo
from pymongo import MongoClient
import weatherkiosk.tmod as tmod
from weatherkiosk.settings import BROKER_ADDRESS, DB_URI, DATABASE

# Database info
mongo = MongoClient(DB_URI)
db = mongo[DATABASE]

class IndoorTemp(mqtt.Client):

	# Callback fires when conected to MQTT broker.
    def on_connect(self, client, userdata, flags, rc):
        #print('Connected with result code {0}'.format(rc))
        # Subscribe (or renew if reconnect).
        self.subscribe('room/temperature/front')
        self.looping_flag=0
        
    
    # Callback fires when a published message is received.
    def on_message(self,client, userdata, msg):
        in_temp = str(msg.payload.decode("utf-8"))
        
        time_now = datetime.datetime.utcnow()
        t = {
            'front_room' : round(float(in_temp)), 
            'dt' : time_now, 
            'replace' : 1
            }
        # t = {
        #     'front_room' : round(float(in_temp)), 
        #     'living_room': 0,
        #     'dt' : time_now, 
        #     'replace' : 1
        #     }
        self.replace_one_db('indoor', t)
   
    def replace_one_db(self, col, data):
      """ write one to a mongoDB database  """
      collection = db[col]
      collection.replace_one({'replace' : 1}, data, True)
      print(f'write indoor temp to the {col} collection')

    def run(self):
        self.broker_add = BROKER_ADDRESS
        try:
            self.connect(self.broker_add, 1883, 60)  # Connect to MQTT broker (also running on Pi)
            self.loop_start()
            self.looping_flag = 1
            counter=0
            while self.looping_flag == 1:
                time.sleep(4) #  Pause 1/100 second
                counter+=1
        except Exception as e:
            print(e)
            t = '-58'
            tmod.save_file('temp.txt',t)
            pass

        self.disconnect()
        self.loop_stop()
 
if __name__ == "__main__":
    app = IndoorTemp()   
    rc = app.run()
           
