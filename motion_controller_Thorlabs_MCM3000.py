"""
Module for motion controller Thorlabs MCM3000
Communication via binary serial protocol.
To launch as a standalone app, run `python stage_ASI_MS2000.py`.
To launch inside another program, see `gui_demo.py`
Copyright Nikita Vladimirov, @nvladimus 2020
"""
import serial
import struct
import sys
import kekse
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal


class MotionController(QtCore.QObject):
    """Basic class for motion controller.
    Currently only 1 model of stage implemented, with X-axis control (axis 0).
    Note: Don't change the class name to keep uniform namespace between modules.
    """
    sig_update_gui = pyqtSignal()

    def __init__(self):
        super().__init__()
        # internal parameters
        self.model_controller = "Thorlabs_MCM3000"
        self.model_stage = 'ZFM2020'
        self.protocol = 'serial'
        self.port = 'COM32'
        self.baud = self.timeout_s = None
        self.max_range_um = self.encoder_offset = self.position_encoder = self.position_um = None
        self.connected = False
        self.__ser_object = None
        self.um_per_count = None
        self.step_size_um = 100
        self.target_um = 0.0
        self.set_stage_model(self.model_stage)
        # GUI
        self.gui = kekse.ProtoKeks(self.model_controller)
        self._setup_gui()
        # signals
        self.sig_update_gui.connect(self._update_gui)

    def set_stage_model(self, model):
        if model == 'ZFM2020':
            self.um_per_count = 0.21166666
            self.max_range_um = 25.4 * 1000
            self.position_encoder = self.encoder_offset = int(self.max_range_um / self.um_per_count)
            self.position_um = 0
            self.sig_update_gui.emit()
        else:
            print("Error: stage model unknown \n")

    def set_step_um(self, step, echo=False):
        self.step_size_um = step
        if echo:
            print('step set to: ' + str(step) + 'um\n')

    def set_target_um(self, pos, echo=True):
        self.target_um = pos
        if echo:
            print('Target (abs position) set to: ' + str(pos) + 'um\n')

    def connect(self, port='COM32', baud=460800, timeout_s=2):
        self.port = port
        self.baud = baud
        self.timeout_s = timeout_s
        try:
            if self.__ser_object is None:
                self.__ser_object = serial.Serial(self.port, self.baud, timeout=self.timeout_s)
                print("Connected to " + self.port + "\n")
            elif self.__ser_object.open():
                print("Port already open: " + self.port + "\n")
        except Exception as e:
            print("Error:" + str(e) + "\n")
        self.set_ini_position()

    def get_current_position(self, unit='count', echo=False):
        """Get the current reading of encoder position.
        Parameters
        unit: str
            'count' for encoder count, 'um' for microns.

        Note: encoder values can be only positive. Negative values are forbidden in this controller.
        """
        command = b'\x0A\x04\x00\x00\x00\x00'
        try:
            self.__ser_object.flushInput()
            self.__ser_object.flushOutput()
            self.__ser_object.write(command)
        except Exception as e:
            print("Error:" + str(e) + "\n")
        try:
            response = self.__ser_object.read(size=12)
            if echo:
                print('response: ' + str(response) + '\n')
            if response[:6] == b'\x0B\x04\x06\x00\x00\x00':
                self.position_encoder = int.from_bytes(response[-4:], 'little')
                self.position_um = self.__counts2um(self.position_encoder - self.encoder_offset)
        except Exception as e:
            print("Error:" + str(e) + "\n")
        if unit == 'count':
            pos = self.position_encoder
        else:
            pos = self.position_um
        self.sig_update_gui.emit()
        return pos

    def set_port(self, port, echo=False):
        self.port = port
        if echo:
            print('Port set:' + port)

    def set_ini_position(self):
        """Avoid setting the encoder count to zero, because after that it cannot be negative.
        So, a workaround is setting the encoder count to max count."""
        command = b'\x09\x04\x06\x00\x00\x00\x00\x00' + struct.pack("<l", self.encoder_offset)
        try:
            self.__ser_object.flushInput()
            self.__ser_object.flushOutput()
            self.__ser_object.write(command)
        except Exception as e:
            print("Error:" + str(e) + "\n")

    def move_abs(self, pos_um=0):
        distance_um = pos_um - self.get_current_position('um')
        self.move_rel(distance_um)

    def move_rel(self, pos_um, echo=False):
        self.position_encoder = self.get_current_position('count')
        counts_int = self.position_encoder + self.__um2counts(pos_um)
        if echo:
            print('New target (encoder counts):' + str(counts_int) + '\n')
        counts_binary = struct.pack("<l", counts_int)
        command = b'\x53\x04\x06\x00\x00\x00\x00\x00' + counts_binary
        try:
            self.__ser_object.flushInput()
            self.__ser_object.flushOutput()
            self.__ser_object.write(command)
            # motor status should be polled here, but it's not implemented by Thorlabs.
        except Exception as e:
            print("Error:" + str(e) + "\n")

    def is_axis_busy(self):
        """Dummy placeholder, this function is not implemented by Thorlabs"""
        command = b'\x80\x04\x00\x00\x00\x00'
        try:
            self.__ser_object.flushInput()
            self.__ser_object.flushOutput()
            self.__ser_object.write(command)
        except Exception as e:
            print("Error:" + str(e) + "\n")
        try:
            response = self.__ser_object.read(size=16)
            print(response)
        except Exception as e:
            print("Error:" + str(e) + "\n")

    def stop(self):
        command = b'\x65\x04\x00\x01\x00\x00'
        try:
            self.__ser_object.flushInput()
            self.__ser_object.flushOutput()
            self.__ser_object.write(command)
        except Exception as e:
            print("Error:" + str(e) + "\n")

    def __um2counts(self, micron):
        return int(micron / self.um_per_count)

    def __counts2um(self, counts):
        return counts * self.um_per_count

    def _setup_gui(self):
        self.gui.add_groupbox('Position control')
        self.gui.add_string_field('Port',
                                  'Position control',
                                  value=self.port, func=self.set_port)
        self.gui.add_numeric_field('Position, encoder',  # widget name
                                   'Position control',  # parent name
                                   value=self.position_encoder,
                                   vmin=-1e6, vmax=1e6, enabled=False, decimals=0)
        self.gui.add_numeric_field('Position, um',  # widget name
                                   'Position control',  # parent name
                                   value=self.position_um,
                                   vmin=-25000, vmax=25000, enabled=False, decimals=2)
        self.gui.add_numeric_field('Step size, um',  # widget name
                                   'Position control',  # parent name
                                   value=self.step_size_um, vmin=-25000, vmax=25000, decimals=1,
                                   func=self.set_step_um)
        self.gui.add_numeric_field('Target position, um',  # widget name
                                   'Position control',  # parent name
                                   value=self.target_um, vmin=-25000, vmax=25000, decimals=1,
                                   func=self.set_target_um)
        self.gui.add_button('Connect',  # widget name
                            'Position control',  # parent name
                            lambda: self.connect('COM32'))
        self.gui.add_button('Move one step',  # widget name
                            'Position control',  # parent name
                            lambda: self.move_rel(self.step_size_um))
        self.gui.add_button('Move to target',  # widget name
                            'Position control',  # parent name
                            lambda: self.move_abs(self.target_um))
        self.gui.add_button('Update position',  # widget name
                            'Position control',  # parent name
                            lambda: self.get_current_position())
        self.gui.add_button('Stop',  # widget name
                            'Position control',  # parent name
                            lambda: self.stop())
        self.gui.add_button('Close connection',  # widget name
                            'Position control',  # parent name
                            lambda: self.close())

    @QtCore.pyqtSlot()
    def _update_gui(self):
        self.gui.update_numeric_field('Position, encoder', self.position_encoder)
        self.gui.update_numeric_field('Position, um', self.position_um)

    def close(self):
        try:
            self.__ser_object.close()
            if not self.__ser_object.open():
                print("Disconnected from " + self.port + "\n")
        except Exception as e:
            print("Error:" + str(e) + "\n")

# run if the module is launched as a standalone program
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dev = MotionController()
    dev.gui.show()
    app.exec_()