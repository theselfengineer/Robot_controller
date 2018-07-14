import serial
import time
import sys
from PyQt4.QtCore import *

class Auto_Thread(QThread):
    def __init__(self, c):
        QThread.__init__(self)
        self.c = c

    def __del__(self):
        self.wait()

    def run(self):

        while True:
            self.c.forward()

            if self.c.SAFETY:
                self.c.stop()
                break

def Main():
    ard = Arduino()
    ard.run()
    print 'Exiting'

if __name__ == '__main__':
    try:
        Main()
    except KeyboardInterrupt:
        print 'Interrupted'
        sys.exit(0)
