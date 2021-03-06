import socket
import sys, time, datetime
import threading
from commands import Commands
from PyQt4.QtCore import *

#Simple socket server that listens to one single client
#inherits from threading to be able to be executed on extra thread
class TcpServer(QThread):

    def __init__(self, c):
        QThread.__init__(self)
        """ Initialize the server with a host and port to listen to. """
        # Create a TCP/IP socket
        #AF_INET specifies the protocol family used for the communication.
        #In most cases, you will want to use AF_INET for IPv4 internet protocols
        #SOCK_STREAM is used for a TCP communication
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #if host is 127.0.0.1, limits connections to clients running on the local machine.
        #you can use 0.0.0.0, and it will be accessible from other machines on your local network.
        self.host = '0.0.0.0'
        #port that server will be listening to
        self.port = 12345
        #buffer size
        self.buf_size = 1024
        #controller object
        self.c = c

    def __del__(self):
        self.wait()

    def stopTCPServer(self):
        pass
        try:
			self.connection.close()
        except Exception ,  e:
			print "Client close Error",e
        self.sock.shutdown(2)
        self.sock.close()

    def run(self):
        """ Accept and handle an incoming connection. """
        #setsockopt() is used to specify options on the socket.
        #Here, we set the option SO_REUSEADDR, which indicates that the system can reuse this socket
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            #associate the socket with the server address and port
            self.sock.bind((self.host, self.port))

        except socket.error as e:
            print "Bind Error : ", e

        #puts the socket into server mode, The number you give to listen()
        #specifies how many connections can be queued for this socket
        self.sock.listen(1)

        #print socket listening state
        print('Starting socket server (host {}, port {})'.format(self.host, self.port))

        #loop to wait for connection
        while True:

            #wait for connection
            print("Wating for connection ... ")

            try:
                #accept waits for an incoming connection, returning the open connection between
                #the server and client and the address of the client
                #The connection is actually a different socket on another port (assigned by the kernel)
                self.connection, self.client_address = self.sock.accept()
                #print client connected
                print('Client {} connected'.format(self.client_address))

            except Exception, e:
				print "sock closed! Error: ",e

            #if connection successful, enter second loop where data exchange is done
            while True:
                #receive data
                try:
                    data = self.connection.recv(self.buf_size).decode('utf-8')
                #close if exeception
                except Exception, e:
                    print "error", e

                #if not data, continue receiving data
                if not data:
                    print('no data')
                    break
                #split data by ">" to get commands
                data_array = data.split(">")
                #act depending on command received
                for data_command in data_array:
                    if data_command == "":
                        continue

                    #GO BACKWARDS
                    if Commands.CMD_FORWARD[1:] in data_command:
                        print data_command + " at " + datetime.datetime.now().strftime("%H:%M:%S")
                        #move forward
                        self.c.forward()

                    #GO FORWARD
                    elif Commands.CMD_BACKWARD[1:] in data_command:
                        print data_command + " at " + datetime.datetime.now().strftime("%H:%M:%S")
                        #set the direction in which motors will spin
                        self.c.writeBlock(self.c.MOTOR_LEFT_DIR,1)
                        self.c.writeBlock(self.c.MOTOR_RIGHT_DIR,1)
                        #increase power (PWM) supplied to the motor
                        for i in range(0,500,10):
                            self.c.writeBlock(self.c.MOTOR_LEFT,i)
                            self.c.writeBlock(self.c.MOTOR_RIGHT,i)
                            time.sleep(0.005)

                    #TURN RIGHT
                    elif Commands.CMD_TURN_RIGHT[1:] in data_command:
                        #log the info
                        print data_command + " " + str(self.c.WHEELS_ORIENTATION) + " at " + datetime.datetime.now().strftime("%H:%M:%S")
                        #turn to the right the direction
                        self.c.turn_right()
                        #update the UI
                        self.emit( SIGNAL('update_wheel_orientation_lcd(QString)'), str(self.c.WHEELS_ORIENTATION))

                    #TURN LEFT
                    elif Commands.CMD_TURN_LEFT[1:] in data_command:
                        #log the info
                        print data_command + " " + str(self.c.WHEELS_ORIENTATION) + " at " + datetime.datetime.now().strftime("%H:%M:%S")
                        #turn to the right the direction
                        self.c.turn_left()
                        #update the UI
                        self.emit( SIGNAL('update_wheel_orientation_lcd(QString)'), str(self.c.WHEELS_ORIENTATION))

                    #STOP
                    elif Commands.CMD_STOP[1:] in data_command:

                        #print command and timestamp
                        print data_command + " at " + datetime.datetime.now().strftime("%H:%M:%S")
                        #stop
                        self.c.stop()

                    #ULTRASONIC TURN RIGHT
                    elif Commands.CMD_ULTRASONIC_TURN_RIGHT[1:] in data_command:
                        #log the info
                        print data_command + " " + str(self.c.ULTRASONIC_ORIENTATION) + " at " + datetime.datetime.now().strftime("%H:%M:%S")
                        #turn to the right the direction
                        self.c.ultrasonic_right()
                        #update the UI
                        self.emit( SIGNAL('update_ultrasonic_orientation_lcd(QString)'), str(self.c.ULTRASONIC_ORIENTATION))

                    #ULTRASONIC TURN RIGHT
                    elif Commands.CMD_ULTRASONIC_TURN_LEFT[1:] in data_command:
                        #log the info
                        print data_command + " " + str(self.c.ULTRASONIC_ORIENTATION) + " at " + datetime.datetime.now().strftime("%H:%M:%S")
                        #turn to the right the direction
                        self.c.ultrasonic_left()
                        #update the UI
                        self.emit( SIGNAL('update_ultrasonic_orientation_lcd(QString)'), str(self.c.ULTRASONIC_ORIENTATION))

                    #RED LED
                    elif Commands.CMD_RGB_R[1:] in data_command:
                        #print command and timestamp
                        print data_command + " at " + datetime.datetime.now().strftime("%H:%M:%S")
                        #turn red led ON
                        self.c.turn_red_led_on()
                        #update server UI
                        self.emit( SIGNAL('update_led_label(QString, QString)'), "red", "background-color: red")

                    #GREEN LED
                    elif Commands.CMD_RGB_G[1:] in data_command:
                        #print command and timestamp
                        print data_command + " at " + datetime.datetime.now().strftime("%H:%M:%S")
                        #turn green led ON
                        self.c.turn_green_led_on()
                        #update server UI
                        self.emit( SIGNAL('update_led_label(QString, QString)'), "green" ,"background-color: green")

                    #BLUE LED
                    elif Commands.CMD_RGB_B[1:] in data_command:
                        #print command and timestamp
                        print data_command + " at " + datetime.datetime.now().strftime("%H:%M:%S")
                        #turn blue led ON
                        self.c.turn_blue_led_on()
                        #update server UI
                        self.emit( SIGNAL('update_led_label(QString, QString)'), "blue" ,"background-color: blue")

                    #OFF LED
                    elif Commands.CMD_RGB_OFF[1:] in data_command:
                        #print command and timestamp
                        print data_command + " at " + datetime.datetime.now().strftime("%H:%M:%S")
                        #turn blue led ON
                        self.c.turn_led_off()
                        #update server UI
                        self.emit( SIGNAL('update_led_label(QString, QString)'), "off", "background-color: white")
            self.connection.close()
            break

def main():
    server = TcpServer()
    server.run()
    print 'Exiting'

if __name__ == "__main__":
    main()
