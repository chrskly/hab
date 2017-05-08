
import serial


class sim(object):

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

    def serial_is_connected(self):
        return self.ser.is_open

    def _get_until_OK(self):
        # Read lines until we see the string 'OK'
        response = ""
        while True:
            more = self.ser.read(128)
            response += more
            print "more %s" % more
            if "OK" in more:
                break
        return response

    def at_command(self, request, response_prefix):
        # Generic request
        self.ser.write(b"%s" % request)
        raw_response = self._get_until_OK()
        if response_prefix != "":
            for line in raw_response.splitlines():
                if line.startswith(response_prefix):
                    command, data = line.split(": ")
                    return data
            return False
        return True

    def gps_is_on(self):
        # Return True/False for GPS state
        # Request  : AT+CGNSPWR?
        # Response : +CGNSPWR: 1
        status = self.at_command("AT+CGNSPWR?\n", "+CGNSPWR:")
        if '1' in status:
            return True
        else:
            return False

    def enable_gps(self):
        # Turn GPS on
        status = self.at_command("AT+CGNSPWR=1\n", "")
        return True

    def gsm_is_connected(self):
        # Check if we're connected to the GSM network
        # Request  : AT+CREG?
        # Response : +CREG: 0,1
        status = self.at_command("AT+CREG?\n", "+CREG:")
        n, stat = status.split(",")
        if int(stat) == 1:
            return True
        return False

    def gprs_is_connected(self):
        # Check if we have GPRS connectivity
        # Request  : AT+CGREG?
        # Response : +CGREG: 0,1
        status = self.at_command("AT+CGREG?\n", "+CGREG:")
        n, stat = status.split(",")
        if int(stat) == 1:
            return True
        return False

    def get_gps(self):
        # Get GPS data
        # Request  : AT+CGNSINF
        # Response : +CGNSINF: 1,1,20160918184431.000,53.287397,-6.215190,45.900,0.28,330.5,1,,1.3,1.6,0.9,,12,6,,,26,,
        data = self.at_command("AT+CGNSINF\n", "+CGNSINF:")
        gps = data.split(",")
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
        return response


    def http_get(self):
        self.ser.write(b"AT+CIPSTART=\"TCP\",\"chrskly.com\",80\n")
        self._get_until_OK()
        self.ser.write(b"AT+CIPSEND\n")
        self.ser.write(b"GET / HTTP/1.0\n")
        self.ser.write(b"Host:chrskly.com\n")
        print self._get_until_OK()
        self.ser.write(b"AT+CIPCLOSE\n")
