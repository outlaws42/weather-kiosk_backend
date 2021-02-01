#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# Imports ///////////////////
from datetime import datetime, timedelta, date, time
import pymongo
from pymongo import MongoClient
from bson.codec_options import CodecOptions
import pytz
from weatherkiosk.settings import DB_URI, DATABASE

# The date needed for misssing high low temp in string form and 'YYYY-MM-DD'
missing_date = '2021-01-30' 

# Database info
mongo = MongoClient(DB_URI)
db = mongo[DATABASE]

# DB collection information for reading and writing
read_collection = 'current'
write_collection = 'past'
key_find = 'updated'
key_sort = 'current_temp'

class GetHighLow():

  def __init__(self):
    self.main()

  def main(self): 
    # collection read , collection writing, find key, sort key
    self.get_high_low_temp_db(
      read_collection, 
      write_collection, 
      key_find, 
      key_sort, 
      missing_date
      )

  def get_high_low_temp_db(
    self, 
    coll_read, 
    coll_write, 
    find_key, 
    sort_key, 
    str_date
    ):
    """ Gets High and Low temp for the day. """
    high_low = self.get_high_low_today(
      coll_read, 
      find_key, 
      sort_key, 
      str_date
      )
    self.write_one_db(coll_write,high_low)
    print(high_low) 
    print(f'write document to the {coll_write} collection via get_high_low_temp_db')


  def high_low_list(self, listin, sort_key):
    """ sort list by a key in the dictionaries
        Then get first and last dictionary from the list """
    listout = []
    listin.sort(key=lambda item: item.get(sort_key))
    listout.append(listin[-1])
    listout.append(listin[0])
    return listout

  def datetime_from_str_date(self, str_date):
    """ Pass string date YYYY-MM-DD  return datetime"""
    date_request = str_date
    year, month, day = date_request.split('-')
    datetime_ = datetime.combine(
      date(int(year), int(month), int(day)), time())
    return datetime_

  def get_doc_today_db(self, col_read, find_key, str_date):
    """ Gets Documents from today mongoDB database """
    today = self.datetime_from_str_date(str_date)
    tomorrow = today + timedelta(1)
    collection = db[col_read]
    aware_times = collection.with_options(
          codec_options=CodecOptions(tz_aware=True,tzinfo=pytz.timezone('US/Eastern')))
    response = aware_times.find({find_key :{'$lt' : tomorrow, '$gte' : today}})
    results = [doc for doc in response]
    return results
  
  def get_high_low_today(self, col_read,find_key, sort_key,str_date):
    today_doc = self.get_doc_today_db(col_read, find_key,str_date)
    temp_list = self.high_low_list(today_doc, sort_key)
    today = self.datetime_from_str_date(str_date)
    high_low = {
              'icon' : temp_list[0]['current_icon'],
              'high' : temp_list[0]['current_temp'], 
              'low' : temp_list[1]['current_temp'], 
              'date' : today}
    return high_low

  def write_one_db(self, col, data):
    """ write one to a mongoDB database  """
    collection = db[col]
    collection.insert_one(data)


if __name__ == "__main__":
  app = GetHighLow()    
 
