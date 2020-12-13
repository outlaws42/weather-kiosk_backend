#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# Imports ///////////////////
from time import sleep
from datetime import datetime, timedelta, date, time
import pymongo
from pymongo import MongoClient
from bson.codec_options import CodecOptions
import pytz
from weatherkiosk.settings import DB_URI, DATABASE
from weatherkiosk.tmod import combine_dict
from  weatherkiosk.owm import Weather

# Refresh rate /////////////////////////////////
refresh_type = '1'  # 1 = minutes 2 = Seconds
refresh_rate_amount = 15

if refresh_type == '1':
  # Minutes Refresh (minutes*60) sleep() is in seconds
  refresh = (refresh_rate_amount*60)  
else:
  # Seconds Refresh refresh_rate_amount sleep() is in seconds
  refresh = refresh_rate_amount

# Database info
mongo = MongoClient(DB_URI)
db = mongo[DATABASE]

class GetWeather():
  run_once = 1

  def __init__(self):
    self.weather = Weather()
    self.weather.get_weather_info()
    self.forecast = combine_dict(self.weather.get_forecast())
    self.weather_info = combine_dict(self.weather.gleen_info())
    self.write_one_db('forecast', self.forecast)
    self.write_one_db('current', self.weather_info)

    # collection read , collection writing, find key, sort key
    self.get_high_low_temp_db('current', 'HighLow', 'updated', 'current_temp')

    # collection read , find key, sort key
    self.get_high_low_today('current', 'updated', 'current_temp')

    # self.get_latest_db('forecast')
    # self.del_all_collection('HighLow')
    # print('Check is done')
    # self.write_weather('HighLow', self.get_high_low('current'))

    # print(self.forecast)
    # print(self.weather_info)

  def write_one_db(self, col, data):
    """ write one to a mongoDB database  """
    collection = db[col]
    collection.insert_one(data)
  
  def get_latest_db(self, col):
    """ Get the latest document from a mongoDB database by ID  """
    collection = db[col]
    last = collection.find().sort("_id", -1).limit(1)
    latest = [doc for doc in last]
    print(f'The latest from collection {col}')
    print(latest)
    return latest 

  def del_all_collection(self, col):
    """ Delete all documents in a collection from a mongoDB database  """
    collection = db[col]
    collection.delete_many({})
    print(f'Deleted all documents in the {col} collection')

  def get_high_low_temp_db(self, coll_read, coll_write, find_key, sort_key):
    """ Gets High and Low temp for the day. only between 11:30pm and 12pm """
    now = datetime.now()
    print(f"Current datetime is {now}, self.run_once = {self.run_once}")
    today12am = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today1230am = now.replace(hour=0, minute=35, second=0, microsecond=0)
    today1130pm = now.replace(hour=23, minute=30, second=0, microsecond=0)
    if now >= today1130pm and self.run_once == 1:
      high_low = self.get_high_low_today(coll_read, find_key, sort_key)
      self.write_one_db(coll_write, high_low)
      self.run_once = 0
      print(high_low) 
      print(f"now = {now}, self.run_once = {self.run_once} ")
      print(f'write document to the {coll_write} collection via get_high_low_temp_db')
    else:
      if today12am <= now <= today1230am:
        self.run_once = 1
        print(f"Reset run_once, Date: {now},  self.run_once = {self.run_once}")
        

  def get_doc_today_db(self, col, key):
    """ Gets Documents from today mongoDB database """
    today = datetime.combine(date.today(), time())
    tomorrow = today + timedelta(1)
    collection = db[col]
    aware_times = collection.with_options(
          codec_options=CodecOptions(tz_aware=True,tzinfo=pytz.timezone('US/Eastern')))
    response = aware_times.find({key :{'$lt' : tomorrow, '$gte' : today}})
    results = [doc for doc in response]
    return results

  def get_high_low_today(self, col,find_key, sort_key):
    today_doc = self.get_doc_today_db(col, find_key)
    temp_list = self.high_low_list(today_doc, sort_key)
    today = datetime.combine(date.today(), time())
    high_low = {
              'icon' : temp_list[0]['current_icon'],
              'high' : temp_list[0]['current_temp'], 
              'low' : temp_list[1]['current_temp'], 
              'date' : today}
    print(high_low)

    return high_low

  def high_low_list(self, listin, key):
    """ sort list by a key in the dictionaries
        Then get first and last dictionary from the list """
    listout = []
    listin.sort(key=lambda item: item.get(key))
    listout.append(listin[-1])
    listout.append(listin[0])
    return listout

if __name__ == "__main__":
    try:
        while True:
            app = GetWeather()    
            sleep(refresh)
    except (KeyboardInterrupt) as e:
        print(e)
        print('Interupted')