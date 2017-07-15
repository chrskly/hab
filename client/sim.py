
import time
import serial
import logging

class sim(object):
    """
    This is a controller for dealing with the SIM808 module. The module is
    connected to the rPi via their serial ports.
    """

    def __init__(self):
        self.ser = serial.Serial()
        self.ser.baudrate = 9600
        self.ser.port = '/dev/ttyAMA0'
        self.ser.timeout = 1
        self.ser.open()
        # Send AT command first time we open
        self.ser.write(b'AT\n')
        self.ser.read(128)
        self.ser.write(b'AT\n')
        self._get_until_OK()

    # Misc fns

    def _serial_is_connected(self):
        return self.ser.is_open

    def _serial_read(self, byte=128):
        return self.ser.read(byte)

    def _serial_write(self, payload):
        self.ser.write(payload.encode())

    def _get_until_OK(self, ok="OK", max_reads=10):
        """
        Read from serial port (sim module) until we see OK msg.
          ok='OK'  : wait for a line with OK on it
          ok='foo' : wait for a line with 'foo' in it
          ok=None  : Just return the first line read
        """
        reads = 1
        while True:
            line = self._serial_read()
            if not ok:
                return line
            logging.debug("(%s/%s) reading from sim : %s", reads, max_reads, line)
            if ok in line:
                return line
            if "ERROR" in line:
                return False
            if reads >= max_reads:
                return False
            reads += 1

    def _at_command(self, request, response_prefix="OK", sleep=1, newline=True):
        """
        Send AT command to the module.
        ARGS
            request         : command to execute
            response_prefix : read response lines until we get this
            sleep           : add additional sleep in ms
            newline         : append newline to request
        """
        payload = b"%s" % request
        logging.debug("Sending command : %s", payload)
        if newline:
            self._serial_write("%s\n" % payload)
        else:
            self._serial_write(payload)
        if sleep:
            time.sleep(sleep)
        response = self._get_until_OK(ok=response_prefix)

        if not response:
            return False

        # Just return whole response if we're just waiting on an OK
        if response_prefix == "OK" or not response_prefix:
            return response
        # If we're looking for a specific prefix, return the matching line
        else:
            for line in response.splitlines():
                if line.startswith(response_prefix):
                    logging.debug("AT command response : %s", line)
                    return line
        return False

    # GPS fns

    def gps_is_on(self):
        """
        Check GPS service state.
        Request  : AT+CGNSPWR?
        Response : +CGNSPWR: 1
        """
        logging.debug("Checking GPS service state")
        command = "AT+CGNSPWR?"
        response = self._at_command(command, wait_for_ok=False)
        command, data = response.split(":")
        if data == 1:
            logging.debug("GPS is on")
            return True
        else:
            logging.debug("GPS is off")
            return False

    def enable_gps(self):
        """
        Turn GPS on
        Request  : AT+CGNSPWR=1
        Response : OK
        """
        logging.debug("Enabling GPS service")
        command = "AT+CGNSPWR=1"
        response = self._at_command(command)
        return True

    def get_gps(self):
        """
        Get GPS data
        Request  : AT+CGNSINF
        Response : +CGNSINF: 1,1,20160918184431.000,53.287397,-6.215190,45.900,0.28,330.5,1,,1.3,1.6,0.9,,12,6,,,26,,
        """
        logging.debug("Fetching GPS data")
        data = self._at_command("AT+CGNSINF", response_prefix="+CGNSINF:")
        if not data:
            return False
        response_received = False
        for line in data.splitlines():
            logging.debug("Reading GPS data : %s", line)
            if line.startswith("+CGNSINF"):
                response_received = True
                cmd, value = line.split(": ")
        if not response_received:
            return False
        gps = value.split(",")
        response = {}
        response['run_status'] = gps[0]
        response['fix_status'] = gps[1]
        response['date'] = gps[2]
        response['latitude'] = gps[3]
        response['longitude'] = gps[4]
        response['altitude'] = gps[5]
        response['speed_over_ground'] = gps[6]
        response['course_over_ground'] = gps[7]
        response['fix_mode'] = gps[8]
        response['hdop'] = gps[10]
        response['pdop'] = gps[11]
        response['vdop'] = gps[12]
        response['gps_satellites_in_view'] = gps[14]
        response['gnss_satellites_used'] = gps[15]
        response['glonass_satellites_used'] = gps[16]
        response['cno_max'] = gps[18]
        response['hpa'] = gps[19]
        response['vpa'] = gps[20]
        logging.debug("GPS DATA : %s" % response)
        return response

    def gps_has_lock(self):
        """
        True/False, GPS has a lock on satellites and knows its location.
        """
        response = self.get_gps()
        logging.info("fix_status : %s" % response['fix_status'])
        if response['fix_status'] == '0':
            return False
        return True

    # GSM fns

    def gsm_registered(self):
        """
        Check GSM registrations status. Are we connected?
        Request  : AT+CREG?
        Response : +CREG: <n>,<stat>[,<lac>,<ci>]
          n
            0 - disable
            1 - enable
            2 - enable (w/ location)
          stat
            0 - not registered
            1 - registered, home
            2 - not registered, searching
            3 - registration denied
            4 - unknown
            5 - registrered, roaming
        """
        command = "AT+CREG?"
        logging.debug("Checking GSM connection status")
        response = self._at_command(command, response_prefix="+CREG")
        if not response:
            return False
        prefix, raw_response = response.split(':')
        n, stat = raw_response.split(",")
        return int(stat) == 1 or int(stat) == 5

    def enable_gsm(self):
        """
        Connect to GSM.
        """
        command = "AT+CREG=1"
        logging.debug("Connecting to GSM")
        response = self._at_command(command, response_prefix="+CREG")
        return True

    def gprs_registered(self):
        """
        Check GPRS registration status. Are we connected (to data network)?
        Request  : AT+CGREG?
        Response : +CGREG: 0,1
        """
        status = self._at_command("AT+CGREG?", response_prefix="+CGREG:")
        n, stat = status.split(",")
        if int(stat) == 1:
            return True
        return False

    def enable_gprs(self):
        """
        Connect to GPRS.
        """
        command = "AT+CGATT=1"
        logging.debug("Connecting to GPRS")
        response = self._at_command(command, response_prefix="+CGATT")
        return True

    def gprs_is_attached(self):
        """
        Check if we are attached to GPRS
        """
        logging.debug("Checking if GPRS is attached")
        command = "AT+CGATT?"
        response = self._at_command(command, response_prefix='+CGATT')
        if not response:
            return False
        prefix, raw_response = response.split(': ')
        return int(raw_response) == 1

    # Data fns

    def get_ip(self):
        """
        Look up our IP address
        """
        ip = self._at_command("AT+CIFSR", response_prefix=None)
        if not ip:
            return False
        logging.debug("IP is %s", ip)
        return ip

    def abort_upload(self):
        cmd = 'AT+CIPSHUT'
        if not self._at_command(cmd):
            logging.debug("WARNING abort failed")
        return

    def data_upload(self, message):
        """
        Upload a message to the HAB server.
        """
        # Check GSM connected
        if not self.gsm_registered():
            logging.info("Upload failed because GSM not registered")
            self.abort_upload()
            return False
        # Check connection status
        if not self.gprs_registered():
            logging.info("Upload failed because GPRS not registered")
            self.abort_upload()
            return False
        # Check if GPRS is attached
        if not self.gprs_is_attached():
            logging.info("Upload failed because GPRS not attached")
            self.abort_upload()
            return False
        # Check APN setup
        cmd = 'AT+CSTT?'
        logging.debug(self._at_command(cmd))
        # Set APN
        cmd = 'AT+CSTT="CMNET"'
        if not self._at_command(cmd):
            logging.debug("Upload failed because problem checking conn status")
            self.abort_upload()
            return False
        # Enable wireless
        cmd = 'AT+CIICR'
        if not self._at_command(cmd):
            logging.debug("Upload failed because problem checking conn status (2)")
            self.abort_upload()
            return False
        # See what our IP is
        if not self.get_ip():
          logging.debug("Upload failed because problem getting IP")
          self.abort_upload()
          return False
        # Set up TCP connection
        cmd = 'AT+CIPSTART="TCP","HAB.CHRSKLY.COM",10000'
        if not self._at_command(cmd):
            logging.debug("Upload failed because there was a problem establishing TCP conn")
            self.abort_upload()
            return False
        # Send message
        cmd = "AT+CIPSEND"
        if not self._at_command(cmd, response_prefix='>'):
            logging.debug("Upload failed because there was a problem sending data to the TCP connection")
            self.abort_upload()
            return False

        cmd = "%s\r\n\x1A" % message
        if not self._at_command(cmd):
            logging.debug("Upload failed because there was a problem sending data to the TCP connection")
            self.abort_upload()
            return False
        # close connection
        cmd = 'AT+CIPCLOSE'
        if not self._at_command(cmd):
            logging.debug("WARNING failed to shutdown TCP connection")
        self.abort_upload()
        return True

