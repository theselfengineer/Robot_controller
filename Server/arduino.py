import serial
import RPi.GPIO as GPIO
import time
import threading
import sys

class arduino(threading.Thread):
    def __init__(self, text, out):
        threading.Thread.__init__(self)
        self.ser = serial.Serial("/dev/ttyACM0",9600)  #change ACM number as found from ls /dev/tty/ACM*
        self.ser.baudrate=9600

    def run (self):
        while true:
            read_ser=ser.readline()
            print(read_ser)

def Main():
    ard = arduino()
    ard.run()
    print 'Exiting'

if __name__ == '__main__':
    try:
        Main()
    except KeyboardInterrupt:
        print 'Interrupted'
        sys.exit(0)