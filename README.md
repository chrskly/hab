# High Altitude Baloon Project

This is the code for my high altitude baloon project.

## Project Goals

  - Take high quality pictures and video from altitudes > 20km
  - Ensure payload can be recovered after flight
  - Record path of baloon during flight
  - Measure outside temperature and pressure
  - Custom built payload

## Components

  - Raspberry Pi Zero    : brain
  - Logitech C910 camera : recording video
  - MS5611               : pressure/temperature sensor
  - HMC5883L             : compass/3-axis for recording heading
  - SIM808               : GSM/GPRS/GPS module, phoning home
  - Balloon 600g 28KM    : lift
  - Parachute            : safe landing
  - Battery (??)         : power source
  - Level converter      : interface between SIM808 and rPi

## Power

Assume 4 hours needed

Reported power consumption
  - Raspberry Pi Zero : 5V, 0.08A,      0.4W
  - MS5611            : 3V, 0.0000013A, 0.0000039W
  - HMC5883L          : 3V, 0.0001A,    0.0003W
  - SIM808            : 3V, 0.02A,      xxx

  Total               : 0.1A * 4hrs = 0.4 Ah

Will need to measure real consumption.

Unrechargeable lithium energisers are recommended. Lithium polymer OK too.

## Links

  https://ukhas.org.uk/general:beginners_guide_to_high_altitude_ballooning
  http://robotrising.org
  https://www.balloonchallenge.org/tutorials
  https://wiki.freebsd.org/WebcamCompat
  https://www.sparkfun.com/tutorials/189
  https://jasonmadigan.com/2013/07/04/high-altitude-adventures-part-3/
  https://wiki.freebsd.org/FreeBSD/arm/Raspberry%20Pi

  ms5611 lib https://github.com/Schm1tz1/arduino-ms5xxx
  map http://leafletjs.com/reference.html
    
## TODO

  - monitor temperature of CPU? As pressure drops, CPU will have a harder time
    dissipating heat.
  - beacon mode? Do I want to monitor power remaining and shut off video
    recoding when low to increase likelyhood of recovery?
  - Trial run. Need something to act as a faraday cage around SIM808 to simulate
    losing GSM signal.

