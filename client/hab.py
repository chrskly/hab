#!/bin/env python

import sys
import logging

from magnetometer import magnetometer
from barometer import barometer
from store import store
from sim import sim

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(funcName)s] %(message)s')

class hab:

    def __init__(self):
        # interface to magnetometer
        self.magnetometer = magnetometer(gauss = 4.7, declination = (-2,5))
        # interface to barometer
        self.barometer = barometer()
        # interface to persistent store
        self.store = store()
        # interface to GPS/GPRS module
        self.sim = sim()

        # current heading
        self.current_heading = None
        # current GPS data (json returned from sim.get_gps())
        self.current_gps = None
        # current baromoeter data
        self.current_barom = {}

    def get_magnetomoeter_reading(self):
        """
        Get the heading from the magnetometer
        """
        self.curent_heading = self.magnetometer.degrees(self.magnetometer.heading())
        logging.info("heading : %s", self.current_heading)
        self.store.store_heading(self.current_heading[0], self.current_heading[1])

    def get_barometer_reading(self):
        """
        Get the temperature and pressure from the barometer.
        """
        (pressure, temperature) = self.barometer.read_temperature_and_pressure()
        logging.info("barom temp : %s", temperature)
        logging.info("barom pres : %s", pressure)
        # Keep latest readings in dict
        self.current_barom['temperature'] = temperature
        self.current_barom['pressure'] = pressure
        # Also store readings in local db
        self.store.store_temperature(temperature)
        self.store.store_pressure(pressure)

    def get_telemetry(self):
        self.current_gps = self.sim.get_gps()

    def upload_telemetry(self):
        """
        Sends msg to server : GPS,<long>,<lat>,<alt>,<sog>,<cog>
        """
        logging.info("uploading telemetry")
        if not self.current_gps:
            logging.info("WARNING : no GPS data. Skipping telemetry upload.")
            return True
        # GPS,<long>,<lat>
        self.sim.data_upload("GPS,%s,%s,%s,%s,%s," % \
            (self.current_gps['longitude'],
             self.current_gps['latitude'],
             self.current_gps['altitude'],
             self.current_gps['speed_over_ground'],
             self.current_gps['course_over_ground']))

    def upload_barometer_reading(self):
        """
        Send msg to server : BAROM,<temp>,<pressure>
        """
        logging.info("uploading barometer data")
        if not self.current_barom:
            logging.info("WARNING : no barometer data. Skipping barometer data upload.")
            return True
        # BAROM,<temp>,<pressure>
        self.sim.data_upload("BAROM,%s,%s" % (self.current_barom['temperature'], self.current_barom['pressure']))

    def main_loop(self):
        """
        Do all the things.
        """
        self.sim.enable_gps()
        self.sim.enable_gsm()
        self.sim.enable_gprs()
        logging.info("LOCK STATUS : %s" % self.sim.gps_has_lock())
        # poll GPS
        self.get_telemetry()
        print self.upload_telemetry()
        # poll barometer
        self.get_barometer_reading()
        print self.upload_barometer_reading()


if __name__ == "__main__":
    myhab = hab()
    myhab.main_loop()

