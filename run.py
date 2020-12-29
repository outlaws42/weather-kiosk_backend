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
from weatherkiosk.settings import DB_URI, DATABASE

# Init app
app = Flask(__name__)
api = Api(app)

# Database
mongo = MongoClient(DB_URI)
db = mongo[DATABASE]

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

# /current or /forecast or /indoor
class Latest(Resource):
  def get(self,col):
    result = self.get_latest_with_tz_db(col)
    date_stamp = timestamp_from_datetime(result[0]['updated'])
    dict = put_in_dict('current', 'updated', result, date_stamp)
    sterilized = json.loads(json_util.dumps(dict))
    return sterilized
  
  def get_latest_with_tz_db(self, col_read):
    """ Gets latest document by _id mongoDB database with 
       local timezone return list with latest document"""
    collection = db[col_read]
    aware_times = collection.with_options(
          codec_options=CodecOptions(tz_aware=True,tzinfo=pytz.timezone('US/Eastern')))
    response = aware_times.find({},{'_id' : 0}).sort("_id", -1).limit(1)
    results = [doc for doc in response]
    return results

api.add_resource(Latest, "/<col>")

# History 
# /HighLow/day or /HighLow/year
class History(Resource):
  def get(self,col, past):
    if past == 'year':
      days = 366
    elif past == 'day':
      days = 1
    else:
      days = 0
    result = self.get_certain_dated_entry_db(col, days)
    date_stamp = timestamp_from_datetime(result[0]['date'])
    dict = put_in_dict(f'forecast_{past}', 'date', result, date_stamp)
    sterilized = json.loads(json_util.dumps(dict))
    return sterilized

  def get_certain_dated_entry_db(self, col, past):
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
api.add_resource(History, "/<col>/<past>")

# Run Server
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
