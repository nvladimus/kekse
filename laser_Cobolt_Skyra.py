import serial
import widget as wd
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal

class laser_controller(QtCore.QObject):
    """
    Class for serial control of Cobolt Skyra laser head.
    by @nvladimus
    """
    sig_update_gui = pyqtSignal()

    def __init__(self, port=None):
        """ Constuctor method.
        Parameters
        :param port: str, name of the port (e.g. "COM11"o on Windows)
        """
        super().__init__()
        self.port = port
        self.ser = None
        self._status = "Unknown"
        # GUI
        self.gui = wd.widget("Cobolt Skyra laser")
        self.__setup_gui()
        # signals
        self.sig_update_gui.connect(self.__update_gui)

    def handshake(self):
        """Are you there?"""
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        self.ser.write(b'?\r')
        self._status = self.ser.read_until(terminator=b'\r')
        return self._status

    def connect(self):
        """
        Open the serial port and connect
        """
        self.ser = serial.Serial()
        self.ser.baudrate = 115200
        self.ser.port = self.port
        self.ser.timeout = 0.2
        try:
            self.ser.open()
            if self.handshake() != b'OK':
                raise serial.SerialException('Handshake failed')
            self.sig_update_gui.emit()
        except serial.SerialException as e:
            self.ser.close()
            print("Cobolt connect() error:" + str(e) + "\n")

    def set_port(self, port):
        self.port = port

    def close(self):
        """
        Close the serial port.
        """
        if self.ser:
            self.ser.close()
            del self.ser
            self._status = 'Disconnected'
            self.sig_update_gui.emit()
        else:
            raise ValueError("Port not found")

    ############
    # GUI part #
    ############
    def __setup_gui(self):
        groupbox_name = 'Laser control'
        self.gui.add_groupbox(groupbox_name)
        self.gui.add_string_field('Port', groupbox_name,
                                  value=self.port, func=self.set_port)
        self.gui.add_string_field('Status', groupbox_name,
                                  value=self._status, enabled=False)
        self.gui.add_button('Connect', groupbox_name,
                            lambda: self.connect())

        self.gui.add_button('Close connection',  groupbox_name,
                            lambda: self.close())

    @QtCore.pyqtSlot()
    def __update_gui(self):
        self.gui.update_string_field('Status', self._status)
