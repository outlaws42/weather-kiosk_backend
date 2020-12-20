#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, jsonify

from datetime import datetime, timedelta, date, time
from flask_restful import Api, Resource, abort, fields, marshal_with 
from flask_pymongo import MongoClient
from weatherkiosk.settings import DB_URI, DATABASE
import pytz

# Init app
app = Flask(__name__)
api = Api(app)

# Database
mongo = MongoClient(DB_URI)
db = mongo[DATABASE]


# Forecast Class
class Forecast(Resource):
  def get(self):
    collection = db['forecast']
    last = collection.find().sort("_id", -1).limit(1)
    result = [doc for doc in last]
    print(result)
    return jsonify({'forecast' : f"{result}"})
api.add_resource(Forecast, "/forecast")

# Current Class
class Current(Resource):
  def get(self):
    collection = db['current']
    response = collection.find().sort("_id", -1).limit(1)
    result = [doc for doc in response]
    print(result)
    return jsonify({'current' : f"{result}"})
api.add_resource(Current, "/current")

# Indoor Class
class Indoor(Resource):
  def get(self):
    collection = db['indoor']
    response = collection.find().sort("_id", -1).limit(1)
    result = [doc for doc in response]
    print(result)
    return jsonify({'current' : f"{result}"})
api.add_resource(Indoor, "/indoor")

# History Class
class History(Resource):
  def get(self):
    today = datetime.combine(date.today(), time())
    tomorrow = today + timedelta(1)
    collection = db['HighLow']
    response = collection.find({
      'date' :{'$lt' : tomorrow, 
      '$gte' : today}})
    results = [doc for doc in response]
    return jsonify({'History' : f"{results}"})

api.add_resource(History, "/history")

# History Year ago Class
class HistoryYear(Resource):
  def get(self):
    year_ago = datetime.combine(date.today(), time()) - timedelta(366)
    year_ago_plus =  year_ago + timedelta(1)
    collection = db['HighLow']
    response = collection.find({
        'date' :{'$lt' : year_ago_plus, 
        '$gte' : year_ago}}).sort('_id', -1).limit(1)
    result = [doc for doc in response]
    return jsonify({'HistoryYear' : f"{result}"})

api.add_resource(HistoryYear, "/history/year")

# History Day ago Class
class HistoryDay(Resource):
  def get(self):
    day_ago = datetime.combine(date.today(), time()) - timedelta(1)
    day_ago_plus =  day_ago + timedelta(1)
    collection = db['HighLow']
    response = collection.find({
        'date' :{'$lt' : day_ago_plus, 
        '$gte' : day_ago}}).sort('_id', -1).limit(1)
    result = [doc for doc in response]
    return jsonify({'Historyday' : f"{result}"})

api.add_resource(HistoryDay, "/history/day")

# Get Certain Day from database Class
class CollectDate(Resource):
  def get(self):
    date_request = '2020-12-19'
    year, month, day = date_request.split('-')
    today = datetime.combine(
      date(int(year), int(month), int(day)), time())
    tomorrow = today + timedelta(1)
    collection = db['current']
    response = collection.find({
      'updated' :{'$lt' : tomorrow, '$gte' : today}})
    results = [doc for doc in response]
    test = self.high_low_list(results, 'updated')
    return jsonify({'Date' : f"{test}"})

  def high_low_list(self, listin, key):
    """ sort list by a key in the dictionaries
        Then get first and last dictionary from the list """
    listout = []
    listin.sort(key=lambda item: item.get(key))
    listout.append(listin[-1])
    listout.append(listin[0])
    return listout
api.add_resource(CollectDate, "/date")

# Run Server
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
