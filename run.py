#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask
from bson import json_util
import json
from datetime import datetime, timedelta, date, time
from flask_restful import Api, Resource 
from flask_pymongo import MongoClient
from weatherkiosk.settings import DB_URI, DATABASE
import pytz

# Init app
app = Flask(__name__)
api = Api(app)

# Database
mongo = MongoClient(DB_URI)
db = mongo[DATABASE]


# Latest Class
# /current or /forecast or /indoor
class Latest(Resource):
  def get(self,col):
    collection = db[col]
    response = collection.find().sort("_id", -1).limit(1)
    result = [doc for doc in response]
    sterilized = json.loads(json_util.dumps(result))
    return sterilized
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
    past_days = datetime.combine(
      date.today(), 
      time()) - timedelta(days)
    past_days_plus_one =  past_days + timedelta(1)
    collection = db[col]
    response = collection.find({
        'date' :{'$lt' : past_days_plus_one, 
        '$gte' : past_days}}).sort('_id', -1).limit(1)
    result = [doc for doc in response]
    sterilized = json.loads(json_util.dumps(result))
    return sterilized
api.add_resource(History, "/<col>/<past>")

# Run Server
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
