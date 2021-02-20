#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# Imports ///////////////////
from datetime import datetime, timedelta, date, time
import pymongo
from pymongo import MongoClient
from bson.codec_options import CodecOptions
import pytz
import typer
from weatherkiosk.settings import DB_URI, DATABASE

# Database info
mongo = MongoClient(DB_URI)
db = mongo[DATABASE]

app = typer.Typer()

@app.command()
def past(
  str_date: str,
  read_collection = 'current', 
  write_collection = 'past', 
  find_key = 'updated', 
  sort_key = 'current_temp', 
  ):
  """ Gets High and Low temp for the date specified.
      Pass the date in this format YYYY-MM-DD 
      Example: past_cli.py 2021-02-10
  """
  past = get_past_by_date(
  read_collection, 
  find_key, 
  sort_key, 
  str_date
  )
  write_one_db(write_collection,past)
  print(past) 
  print(f'write document to the {write_collection} collection via get_past_by_date')


def past_list(listin, sort_key):
  """ sort list by a key in the dictionaries
      Then get first and last dictionary from the list """
  listout = []
  listin.sort(key=lambda item: item.get(sort_key))
  listout.append(listin[-1])
  listout.append(listin[0])
  return listout

def datetime_from_str_date(str_date):
  """ Pass string date YYYY-MM-DD  return datetime"""
  date_request = str_date
  year, month, day = date_request.split('-')
  datetime_ = datetime.combine(
    date(int(year), int(month), int(day)), time())
  return datetime_

def get_doc_date_db(col_read, find_key, str_date):
  """ Gets Documents from today mongoDB database """
  today = datetime_from_str_date(str_date)
  tomorrow = today + timedelta(1)
  collection = db[col_read]
  aware_times = collection.with_options(
        codec_options=CodecOptions(tz_aware=True,tzinfo=pytz.timezone('US/Eastern')))
  response = aware_times.find({find_key :{'$lt' : tomorrow, '$gte' : today}})
  results = [doc for doc in response]
  return results
  
def get_past_by_date(col_read,find_key, sort_key,str_date):
  date_doc = get_doc_date_db(col_read, find_key,str_date)
  temp_list = past_list(date_doc, sort_key)
  the_date = datetime_from_str_date(str_date)
  past = {
            'icon' : temp_list[0]['current_icon'],
            'high' : temp_list[0]['current_temp'], 
            'low' : temp_list[1]['current_temp'], 
            'date' : the_date}
  return past

def write_one_db(col, data):
  """ write one to a mongoDB database  """
  collection = db[col]
  collection.insert_one(data)


if __name__ == "__main__":
  app()    
 
