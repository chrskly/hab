#!/bin/env python

# Server-side component for HAB tracker

import web
import model
import json
import MySQLdb

urls = (
  '/api/telemetry', 'telemetry',
)


app = web.application(urls, globals())

class telemetry:

  def GET(self):
    # Get the latest data from the DB
    #cur = connect_to_db();
    # {"geometry": {"type": "Point", "coordinates": [138.70170891787507, -35.502951363284197]}, "type": "Feature", "properties": {}}
    #cur.execute("SELECT dt, lat, lng, alt, sog, cog, temp FROM telemetry ORDER BY dt DESC LIMIT 1;")
    #rows = cur.fetchall()
    res = model.get_latest_telemetry()
    #dt, lat, lng, alt, sog, cog, temp = rows[0]
    r = res[0]
    #response = { 'dt' : dt.strftime('%Y-%m-%dT%H:%M:%SZ'), 'lat' : lat, 'lng' : lng, 'alt' : alt, 'sog' : sog, 'cog' : cog, 'temp' : temp }
    #response = { 'geometry' : { 'type' : "Point", "coordinates" : [ lng, lat ] }, "type" : "Feature", "properties" : {} }
    response = { 'geometry' : { 'type' : "Point", "coordinates" : [ r.lng, r.lat ] }, "type" : "Feature", "properties" : {} }
    web.header('Content-Type', 'application/json')
    return json.dumps(response)

  def POST(self):
    # HAB pushes update to server
    pass

if __name__=="__main__":
  web.internalerror = web.debugerror
  app.run()
