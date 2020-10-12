'''This is a template for device adapter.
Copyright @nvladimus, 2020
'''

from PyQt5 import QtCore, QtWidgets
import sys
import logging
import kekse
from functools import partial
logging.basicConfig()

config = {
    'Parameter 0': [1.0, [0, 100, 1]],  # [value, [min, max, step]]
    'Parameter 1': [2.0, [-1e6, 1e6, 0.01]],  # [value, [min, max, step]]
    'Parameter String': ['a string', True],  # a string parameter: [value, editable]
    'Param Checkbox': True,  # a checkbox
    'Param Combobox': ['option0', ['option0', 'option1']]  # a combobox: selected option and list of all options
}


class Device(QtCore.QObject):
    sig_update_gui = QtCore.pyqtSignal()

    def __init__(self, dev_name='Device name', gui_on=True, logger_name='dev logger'):
        super().__init__()
        self.config = config
        self.initialized = False
        self._status = 'not initialized'
        # logger setup
        self.logger_name = logger_name
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)
        # GUI setup
        self.gui_on = gui_on
        if self.gui_on:
            self.logger.info("GUI activated")
            self.gui = kekse.ProtoKeks(dev_name)
            self._setup_gui()
            self.sig_update_gui.connect(self._update_gui)

    def initialize(self):
        if not self.initialized:
            self.initialized = True
            self._status = 'connected'
            self.logger.info('Initialized')
        if self.gui_on:
            self.sig_update_gui.emit()

    def close(self):
        self._status = 'closed'
        self.initialized = False
        self.logger.info('Closed')
        if self.gui_on:
            self.sig_update_gui.emit()

    def do_something(self):
        self.logger.info('Did something')

    def update_config(self, key, value):
        if key in self.config.keys():
            self.config[key] = value
            self.logger.info(f"changed {key} to {value}")
        else:
            self.logger.error("Parameter name not found in config file")
        if self.gui_on:
            self.sig_update_gui.emit()

    def _setup_gui(self):
        self.gui.add_tabs("Control Tabs", tabs=['Tab 0', 'Tab 1'])
        self.gui.add_button('Initialize', 'Tab 0', func=self.initialize)
        self.gui.add_string_field('Status', 'Tab 0', value=self._status, enabled=False)
        self.gui.add_groupbox("Groupbox 0", 'Tab 0')
        container_title = "Groupbox 0"
        self.gui.add_label("This is just a label", container_title)
        self.gui.add_numeric_field('Parameter 0', container_title,
                                   value=self.config['Parameter 0'][0], # Initial value
                                   vrange=self.config['Parameter 0'][1], # [min, max, step]
                                   func=partial(self.update_config, 'Parameter 0'))
        self.gui.add_numeric_field('Parameter 1', container_title,
                                   value=self.config['Parameter 1'][0], # Initial value
                                   vrange=self.config['Parameter 1'][1], # [min, max, step]
                                   func=partial(self.update_config, 'Parameter 1'))
        self.gui.add_string_field('Parameter String', container_title,
                                  value=config['Parameter String'][0], # Text
                                  enabled=config['Parameter String'][1], # Editable?
                                  func=partial(self.update_config, 'Parameter String'))
        self.gui.add_checkbox('Param Checkbox', container_title,
                              value=self.config['Param Checkbox'], # Checked?
                              func=partial(self.update_config, 'Param Checkbox'))
        self.gui.add_combobox('Param Combobox', container_title,
                              value=self.config['Param Combobox'][0], # initial value
                              items=self.config['Param Combobox'][1], # available options
                              func=partial(self.update_config, 'Param Combobox'))
        self.gui.add_button('Do something', container_title, func=self.do_something)
        self.gui.add_button('Disconnect', 'Tab 0', func=self.close)

    @QtCore.pyqtSlot()
    def _update_gui(self):
        self.gui.update_param('Status', self._status)
        self.logger.info('GUI updated')


# executed if the module is launched as a standalone program
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dev = Device()
    dev.gui.show()
    app.exec_()
