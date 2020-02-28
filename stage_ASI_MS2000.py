"""
ASI XY stage interface for MS-2000 controller.
To launch as a standalone app, run `python stage_ASI_MS2000.py`.
To launch inside another program, see `gui_demo.py`
Copyright Nikita Vladimirov @nvladimus 2020
"""
import serial
import widget as wd
import logging
import sys
import time
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal

config = {'port': "COM18",
          'baud': 9600,
          'timeout_s': 2,
          'units_mm': 1e-4,
          'speed_mm/s': 7.5}


class MotionController(QtCore.QObject):
    """
    Note: Don't change the class name to keep uniform namespace between modules.
    """
    sig_update_gui = pyqtSignal()

    def __init__(self, dev_name='ASI MS2000', gui_on=True, logger_name='ASI stage'):
        super().__init__()
        self.port = config['port']
        self.baud = config['baud']
        self.timeout_s = config['timeout_s']
        self.units = config['units_mm']
        self.speed_x = self.speed_y = config['speed_mm/s']
        self._ser = None
        self.position_x_mm = self.position_y_mm = None
        self.target_pos_x_mm = self.target_pos_y_mm = 0
        # logger setup
        logging.basicConfig()
        self.logger_name = logger_name
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)
        # GUI setup
        self.gui_on = gui_on
        if self.gui_on:
            self.logger.info("GUI activated")
            self.gui = wd.widget(dev_name)
            self._setup_gui()
            self.sig_update_gui.connect(self._update_gui)

    def connect(self, port, baud=9600, timeout_s=2):
        self.port = port
        self.baud = baud
        self.timeout_s = timeout_s
        try:
            self._ser = serial.Serial(self.port, self.baud, timeout=self.timeout_s)
            self.logger.info(f"Connected to port {self.port}")
            self.get_position()
            self.get_speed()
        except Exception as e:
            self.logger.error(f"Could not connect to stage: {e}")

    def get_position(self):
        response = self.write_with_response(b'W X Y')
        if response[:2] == ":A" and len(response) >= 3:
            words = response.split(" ")
            if len(words) >= 3:
                self.position_x_mm = float(words[1]) * self.units
                self.position_y_mm = float(words[2]) * self.units
        if self.gui_on:
            self.sig_update_gui.emit()

    def get_speed(self):
        response = self.write_with_response(b"s x? y?")
        if response[:2] == ":A" and len(response) >= 3:
            words = response.split(" ")
            if len(words) >= 3:
                self.speed_x = float(words[1][2:])
                self.speed_y = float(words[2][2:])
                self.logger.info(f'speed: ({self.speed_x}, {self.speed_y})')
        if self.gui_on:
            self.sig_update_gui.emit()

    def write_with_response(self, command, terminator=b'\r'):
        try:
            self._flush()
            self._ser.write(command + terminator)
            response = self._ser.read_until(terminator=b'\r\n').decode('utf-8')
            return response[:-2]
        except Exception as e:
            self.logger.error(f"write_with_response() {e}")
            return None

    def _flush(self):
        if self._ser is not None:
            self._ser.reset_input_buffer()
            self._ser.reset_output_buffer()
        else:
            self.logger.error("_flush(): serial port not initialized")

    def disconnect(self):
        try:
            self._ser.close()
            self.logger.info("closed")
        except Exception as e:
            self.logger.error(f"Could not disconnect {e}")

    def _set_port(self, port):
        self.port = port
        self.logger.info(f"Port {self.port}")

    def _set_baud(self, baud):
        self.baud = baud
        self.logger.info(f"Port {int(self.baud)}")

    def set_target_x(self, target_x_mm): self.target_pos_x_mm = target_x_mm

    def set_target_y(self, target_y_mm): self.target_pos_y_mm = target_y_mm

    def set_speed(self, speed_mms, **kwargs):
        if 'axis' in kwargs.keys():
            axis = kwargs['axis']
        else:
            self.logger.error("set_speed(): keyword /'axis/' is missing")
        if axis == 'X':
            self.speed_x = speed_mms
        elif axis == 'Y':
            self.speed_y = speed_mms
        else:
            self.logger.error("set_speed(): argument axis must be /'X/' or /'Y/'")
        response = self.write_with_response(f"S {axis}={speed_mms}".encode())
        if response[:2] != ":A":
            self.logger.warning(f"set_speed() unexpected response: {response}")
        else:
            self.get_speed()

    def move_abs(self, pos_mm, sleep_s=0.05):
        assert len(pos_mm) == 2, "move_abs(): argument pos_mm should be 2-element array-like"
        command = f'M X={pos_mm[0]/self.units} Y={pos_mm[1]/self.units}'.encode()
        _ = self.write_with_response(command)
        response = self.write_with_response(b'/')
        while response[0] != 'N':
            response = self.write_with_response(b'/')
            time.sleep(sleep_s)
        self.logger.info(f"move complete")
        self.get_position()

    def _setup_gui(self):
        parent_widget_name = 'XY control'
        self.gui.add_groupbox(parent_widget_name)
        self.gui.add_string_field('Port', parent_widget_name, value=self.port, func=self._set_port)
        self.gui.add_numeric_field('Baud', parent_widget_name, value=self.baud, func=self._set_baud,
                                   vmin=9600, vmax=115200, enabled=True, decimals=0)
        self.gui.add_numeric_field('X pos., mm',  parent_widget_name,
                                   value=-1, vmin=-1e6, vmax=1e6, enabled=False, decimals=5)
        self.gui.add_numeric_field('Y pos., mm', parent_widget_name,
                                   value=-1, vmin=-1e6, vmax=1e6, enabled=False, decimals=5)
        self.gui.add_numeric_field('Target X, mm', parent_widget_name,
                                   value=0, vmin=-25., vmax=25., decimals=5,
                                   enabled=True, func=self.set_target_x)
        self.gui.add_numeric_field('Target Y, mm', parent_widget_name,
                                   value=0, vmin=-25., vmax=25., decimals=5,
                                   enabled=True, func=self.set_target_y)
        self.gui.add_numeric_field('Speed X, mm/s', parent_widget_name,
                                   value=self.speed_x, vmin=0, vmax=7.5, decimals=5,
                                   enabled=True, func=self.set_speed, **{'axis': 'X'})
        self.gui.add_numeric_field('Speed Y, mm/s', parent_widget_name,
                                   value=self.speed_y, vmin=0, vmax=7.5, decimals=5,
                                   enabled=True, func=self.set_speed, **{'axis': 'Y'})
        self.gui.add_button('Connect', parent_widget_name,
                            lambda: self.connect(self.port, self.baud, self.timeout_s))
        self.gui.add_button('Update position', parent_widget_name,
                            lambda: self.get_position())
        self.gui.add_button('Move to target', parent_widget_name,
                            lambda: self.move_abs((self.target_pos_x_mm, self.target_pos_y_mm)))
        self.gui.add_button('Disconnect', parent_widget_name,
                            lambda: self.disconnect())

    @QtCore.pyqtSlot()
    def _update_gui(self):
        self.gui.update_numeric_field('X pos., mm', self.position_x_mm)
        self.gui.update_numeric_field('Y pos., mm', self.position_y_mm)
        self.gui.update_numeric_field('Speed X, mm/s', self.speed_x)
        self.gui.update_numeric_field('Speed Y, mm/s', self.speed_y)


# run if the module is launched as a standalone program
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dev = MotionController()
    dev.gui.show()
    app.exec_()
