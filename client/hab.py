#!/bin/env python

import sys
import logging

from magnetometer import magnetometer
from barometer import barometer
from store import store
from sim import sim

logging.basicConfig(level=logging.DEBUG, format='%(created)f:%(funcName)s:%(message)s')

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
        self.heading = None

    def get_heading(self):
        # Get the heading from the magnetometer
        self.heading = self.magnetometer.degrees(self.magnetometer.heading())
        logging.info("heading : %s", self.heading)
        self.store.store_heading(self.heading[0], self.heading[1])

    def get_altitude(self):
        (pressure, temperature) = self.barometer.read_temperature_and_pressure()
        logging.info("barom temp : %s", temperature)
        logging.info("barom pres : %s", pressure)
        self.store.store_temperature(temperature)
        self.store.store_pressure(pressure)

    def get_location(self):
        self.sim.get_gps()

    def upload(self):
        self.sim.http_get()



if __name__ == "__main__":
    myhab = hab()
    #print "gps on %s" % myhab.sim.gps_is_on()
    #print "enabling gps %s" % myhab.sim.enable_gps()
    #print "gps on %s" % myhab.sim.gps_is_on()
    #print "connected : %s" % myhab.sim.is_connected_to_network()
    print "get gps : %s" % myhab.sim.get_gps()
    #print "http get : %s" % myhab.sim.http_get()
    #print "gprs connected %s" % myhab.sim.gprs_is_connected()
