#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask
from bson import json_util
import json
from bson.codec_options import CodecOptions
import pytz
from datetime import datetime, timedelta, date, time
from flask_restful import Api, Resource 
from flask_pymongo import MongoClient
from weatherkiosk.settings import DB_URI, DATABASE, DATABASE2

# Init app
app = Flask(__name__)
api = Api(app)

# Database
mongo = MongoClient(DB_URI)
# db = mongo[DATABASE]
# db2 = mongo[DATABASE2]

def timestamp_from_datetime(dt):
  """ Convert Datetime to timestamp """
  timestamp_ = int(dt.timestamp())
  return timestamp_

def str_date_from_datetime(self, datetime_):
  str_date = datetime_.strftime('%Y-%m-%d')
  return str_date

def put_in_dict(root_key, date_key, in_list, date_stamp ):
  dict = {root_key : {}}
  for key in in_list[0]:
    dict[root_key][key] = in_list[0][key]
  dict[root_key][date_key] = date_stamp
  print(dict)
  return dict

def check_for_indoor_negative(dictionary, root_key, key):
  """
  Checks checks to see if the temp is negative if so it makes it 0
  """
  if dictionary[root_key][key] < 0:
    print('NEGATIVE NUMBER')
    dictionary[root_key][key] = 0
    print(dictionary)
  return dictionary

def check_for_indoor_time(dictionary, root_key, date_key, temp_key):
  """
  Checks to see how much time between now
  and when the last write to the db
  if to long then sets to 0
  """
  time_stamp = dictionary[root_key][date_key]
  now = datetime.now()
  then = datetime.fromtimestamp(time_stamp)
  tdelta = now - then
  seconds = tdelta.total_seconds()
  hour = 60*60
  print(f"timeDelta: {tdelta}")
  print(f"seconds: {seconds}")
  if seconds >= hour:
    dictionary[root_key][temp_key] = 0
    print(f"Indoor Dictionary after time check {dictionary}")
  return dictionary

# /weather/current or /weather/forecast or /weather/indoor
class Latest(Resource):
  def get(self,col, database):
    print(database)
    db = mongo[database]
    root_key = ''
    date_key = ''
    if col  == 'current' or col == 'forecast' or col == 'indoor' or col == 'sensors':
      if col == 'current':
        date_key = 'updated'
        root_key = 'current'
      elif col == 'forecast':
        date_key = 'date'
        root_key = 'forecast'
      elif col == 'indoor':
        date_key = 'dt'
        root_key = 'indoor'
      elif col == 'sensors':
        date_key = 'dt'
        root_key = 'sensors'
    else:
      return 404
    result = self.get_latest_with_tz_db(db, col)
    date_stamp = timestamp_from_datetime(result[0][date_key])
    dict = put_in_dict(root_key, date_key, result, date_stamp)
    if root_key == 'indoor':
      check_for_indoor_negative(dict, root_key,'front_room')
      check_for_indoor_time(dict, root_key, date_key,'front_room')
    sterilized = json.loads(json_util.dumps(dict))
    return sterilized
  
  def get_latest_with_tz_db(self, db, col_read):
    """ Gets latest document by _id mongoDB database with 
       local timezone return list with latest document"""
    collection = db[col_read]
    aware_times = collection.with_options(
          codec_options=CodecOptions(tz_aware=True,tzinfo=pytz.timezone('US/Eastern')))
    response = aware_times.find({},{'_id' : 0}).sort("_id", -1).limit(1)
    results = [doc for doc in response]
    return results

api.add_resource(Latest, "/<database>/<col>")

# History 
# /weather/past/day or /weather/past/year
class History(Resource):
  def get(self,database,col,past):
    print(past)
    db = mongo[database]
    if col == 'past' and past == 'day' or past == 'year':
      if past == 'year':
        days = 365 #517
      elif past == 'day':
        days = 1
      else:
        days = 0
    else:
      return f'404 ${past}'
    try:
      result = self.get_certain_dated_entry_db(db, col, days)
      print(f'High_Low Result: {result}')
      date_stamp = timestamp_from_datetime(result[0]['date'])
      dict = put_in_dict(f'forecast_{past}', 'date', result, date_stamp)
    except:
      dict = {f'forecast_{past}':{'icon': 0, 'high': 0, 'low': 0,  'date' : 0}}
    sterilized = json.loads(json_util.dumps(dict))
    return sterilized
      

  def get_certain_dated_entry_db(self, db, col, past):
    """ Gets past document by date from today mongoDB 
    database with return list with past document"""
    past_days = datetime.combine(
      date.today(), 
      time()) - timedelta(past)
    past_days_plus_one =  past_days + timedelta(1)
    collection = db[col]
    response = collection.find({
        'date' :{'$lt' : past_days_plus_one, 
        '$gte' : past_days}},{'icon' : 1,'high': 1, 'low': 1, 'date': 1, '_id' : 0}).sort('_id', -1).limit(1)
    result = [doc for doc in response]
    return result
api.add_resource(History, "/<database>/<col>/<past>")

# Run Server
if __name__ == "__main__":
    app.run(debug=True, port=5500, host='0.0.0.0')
