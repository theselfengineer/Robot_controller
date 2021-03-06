from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSignature
from PyQt4.QtGui import QWidget
import sys, time, datetime
import socket
import threading
from server_ui import Ui_Form
from controller import Controller
from tcpserver import TcpServer
from arduino_thread import Arduino_Thread
from controller_thread import Controller_Thread
from auto_thread import Auto_Thread

#PYQT USER INTERFACE ==> MAIN THREAD
class Main(QWidget, Ui_Form):

    """---------------CLASS CONSTRUCTOR---------------------"""
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        #method to setup the UI, defined in server_ui.py
        self.setupUi(self)
        #controller is instantiated here so it can be accessible
        #for arduino thread, controler thread
        #and tcpServer thread
        self.c = Controller()
        #start arduino thread
        self.start_arduino_thread()
        #auto thread status
        self.auto_status = False
        #server thread status
        self.server_status = False

    """---------------INSTANCE METHODS---------------------"""

    """SLOT FUNCTIONS"""
    #UPDATE UI LED INDICATOR
    def update_led_indicator(self, led, text):
        if led == "red":
            self.red_label.setStyleSheet(text)
            self.green_label.setStyleSheet("background-color: white")
            self.blue_label.setStyleSheet("background-color: white")
        elif led == "green":
            self.red_label.setStyleSheet("background-color: white")
            self.green_label.setStyleSheet(text)
            self.blue_label.setStyleSheet("background-color: white")
        elif led == "blue":
            self.red_label.setStyleSheet("background-color: white")
            self.green_label.setStyleSheet("background-color: white")
            self.blue_label.setStyleSheet(text)
        elif led == "off":
            self.red_label.setStyleSheet(text)
            self.green_label.setStyleSheet(text)
            self.blue_label.setStyleSheet(text)

    #UPDATE ULTRASONIC SENSOR LCD SCREEN
    def update_ultrasonic_distance_lcd(self, text):
        self.ultrasonic_distance_lcd.display(text)

    #UPDATE ULTRASONIC ORIENTATION LCD SCREEN
    def update_ultrasonic_orientation_lcd(self, text):
        self.ultrasonic_orientation_lcd.display(text)

    #UPDATE CAR ORIENTATION LCD SCREEN
    def update_wheel_orientation_lcd(self, text):
        self.wheel_orientation_lcd.display(text)

    #SERVER STARTED NOTIFICATION AND UI UPDATE
    def server_started(self):
        self.controller_label.setStyleSheet("background-color: green")
        QtGui.QMessageBox.information(self, "Started!", "Server thread started")
        self.server_status = True

    #SERVER FINISHED NOTIFICATINO AND UI UPDATE
    def server_finished(self):
        self.controller_label.setStyleSheet("background-color: white")
        QtGui.QMessageBox.information(self, "Finished!", "Server thread finished")
        self.server_status = False

    #AUTONOMOUS MODE STARTED NOTIFICATION AND UI UPDATE
    def auto_started(self):
        self.auto_label.setStyleSheet("background-color: green")
        QtGui.QMessageBox.information(self, "Started!", "Autonomous mode thread started")
        self.auto_status = True

    #AUTONOMOUS MODE FINISHED NOTIFICATINO AND UI UPDATE
    def auto_finished(self):
        self.auto_label.setStyleSheet("background-color: white")
        QtGui.QMessageBox.information(self, "Finished!", "Autonomous mode thread finished")
        self.auto_status = False

    """PyQt BUTTON LISTENERS MANAGING THREADS"""
    #START TCP SERVER THREAD
    @pyqtSignature("")
    def on_server_start_btn_pressed(self):
        if not self.auto_status:
            #pass controller object as tcp server receives commands to execute functions that will interact with
            #the robot that are defined in the controller
            self.ServerThread = TcpServer(self.c)
            #connect signal (emit in this workthread) and slot (function add)
            self.connect( self.ServerThread, QtCore.SIGNAL("update_led_label(QString, QString)"), self.update_led_indicator )
            self.connect( self.ServerThread, QtCore.SIGNAL("update_ultrasonic_orientation_lcd(QString)"), self.update_ultrasonic_orientation_lcd )
            self.connect( self.ServerThread, QtCore.SIGNAL("update_wheel_orientation_lcd(QString)"), self.update_wheel_orientation_lcd )
            self.connect(self.ServerThread, QtCore.SIGNAL("started()"), self.server_started)
            self.connect(self.ServerThread, QtCore.SIGNAL("finished()"), self.server_finished)
            #start thread
            self.ServerThread.start()
        else:
            QtGui.QMessageBox.information(self, "Unauthorized!", "Please terminate autonomous thread before turning on controller mode")

    #START AUTONOMOUS MODE
    @pyqtSignature("")
    def on_auto_on_btn_pressed(self):
        if not self.server_status:
            self.AutoThread = Auto_Thread(self.c)
            self.connect(self.AutoThread, QtCore.SIGNAL("started()"), self.auto_started)
            self.connect(self.AutoThread, QtCore.SIGNAL("finished()"), self.auto_finished)
            #start thread
            self.AutoThread.start()
        else:
            QtGui.QMessageBox.information(self, "Unauthorized!", "Please disconnect client before turning on autonomous mode")


    #START AUTONOMOUS MODE
    @pyqtSignature("")
    def on_auto_off_btn_pressed(self):
        self.AutoThread.finish_thread()


    """THREAD FUNCTIONS AUTOMATICALLY TRIGGERED"""
    #START ARDUINO SENSING THREAD
    def start_arduino_thread(self):

        #pass the controllet object so it can upload the sensor data to the controller instance
        #pass the Main object, inheriting from Ui_Form, to be able to upload sensor values in PyQt
        #using a QThread that will be able to talk to this thread (main one)
        #through signals and slots
        self.ArduinoThread = Arduino_Thread(self.c)
        #connect signal (emit in this workthread) and slot (function add)
        self.connect( self.ArduinoThread, QtCore.SIGNAL("update_led_label(QString, QString)"), self.update_led_indicator )
        self.connect( self.ArduinoThread, QtCore.SIGNAL("update_ultrasonic_distance_lcd(QString)"), self.update_ultrasonic_distance_lcd )

        #start thread
        self.ArduinoThread.start()

"""----------------------MAIN PROGRAM---------------------------"""
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    dlg = Main()
    dlg.show()
    sys.exit(app.exec_())
