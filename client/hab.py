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

    def get_heading(self):
        # Get the heading from the magnetometer
        self.curent_heading = self.magnetometer.degrees(self.magnetometer.heading())
        logging.info("heading : %s", self.current_heading)
        self.store.store_heading(self.current_heading[0], self.current_heading[1])

    def get_altitude(self):
        (pressure, temperature) = self.barometer.read_temperature_and_pressure()
        logging.info("barom temp : %s", temperature)
        logging.info("barom pres : %s", pressure)
        self.store.store_temperature(temperature)
        self.store.store_pressure(pressure)

    def get_location(self):
        self.current_gps = self.sim.get_gps()

    def upload_telemetry(self):
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



if __name__ == "__main__":
    myhab = hab()
    myhab.sim.enable_gps()
    logging.info("LOCK STATUS : %s" % myhab.sim.gps_has_lock())
    #myhab.get_location()
    #print myhab.upload_telemetry()

