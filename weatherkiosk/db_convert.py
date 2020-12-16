#! /usr/bin/env python3

# -*- coding: utf-8 -*-
from datetime import datetime
import pymongo
from pymongo import MongoClient
import logging
from settings import DB_URI, DATABASE
import tmod
logging.basicConfig(
    filename='wu.log', 
    level=logging.INFO, 
    format='%(asctime)s %(message)s', 
    datefmt='%m/%d/%Y %I:%M:%S %p')

# Database info
mongo = MongoClient(DB_URI)
db = mongo[DATABASE]

class ConvertDB():
    degree_sign = '\N{DEGREE SIGN}'

    def __init__(self):
        self.import_data()
        self.write_many_db('HighLow', self.get_Info(self.high,self.low))
        #self.get_Info(self.high,self.low)

    def import_data(self):
        try:
            self.high = tmod.open_json('high2020-12-14.json', 'relative')
            self.low = tmod.open_json('low2020-12-14.json','relative')
        except Exception as e:
           self.high = tmod.open_json('high.json', 'relative')
           logging.info('Collect weather error:  ' + str(e))
           pass
        # print(f"This is high: {self.high}")
        
    def get_Info(self, file1, file2):
        """ Takes two list of dictionaries and gleans  inferamtion to put in DB"""   
        dic_list = []
        for i in range(len(file1)):
            temp = {
                'icon':  file1[i]['Condition'],
                'high' : file1[i]['OTemp'], 
                'low': file2[i]['OTemp'], 
                'date' : datetime.strptime(file1[i]['TDate'], '%Y-%m-%d')}
            dic_list.append(temp)
        print(dic_list)
        return dic_list

    def write_many_db(self, col, data):
      """ write many to a mongoDB database  """
      collection = db[col]
      collection.insert_many(data)
    
    

if __name__ == "__main__":
    app = ConvertDB()
