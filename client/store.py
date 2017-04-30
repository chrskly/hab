
#
# Table: heading
#   - date
#   - degrees
#   - minutes
#
# Table: position
#   - lat
#   - long
#   - altitude
#
# Table: temperature
#
# Table: altitude
#

import sqlite3
import datetime

class store:

  def __init__(self):
    self.conn = sqlite3.connect('/data/hab.store.db')

  def store_heading(self, degrees, minutes):
    # save a heading back to the store
    cur = self.conn.cursor()
    cur.execute("INSERT INTO heading (degrees, minutes, date) VALUES ('%s', '%s', '%s')" % (degrees, minutes, datetime.datetime.now()))
    self.conn.commit()

  def store_temperature(self, degrees):
    # save a temperature reading back to the store
    cur = self.conn.cursor()
    cur.execute("INSERT INTO temperature (degrees, date) VALUES ('%s', '%s')" % (degrees, datetime.datetime.now()))
    self.conn.commit()

  def store_pressure(self, pressure):
    # save a pressure reading back to the store
    cur = self.conn.cursor()
    cur.execute("INSERT INTO pressure (pressure, date) VALUES ('%s', '%s')" % (pressure, datetime.datetime.now()))
    self.conn.commit()
