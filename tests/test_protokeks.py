import unittest
import kekse
import numpy as np
import sys
from PyQt5.QtWidgets import (QGroupBox, QLineEdit, QPushButton, QTabWidget, QCheckBox, QComboBox,
                             QVBoxLayout, QWidget, QDoubleSpinBox, QFormLayout, QApplication)


class TestInputFields(unittest.TestCase):
    def test_decimals(self):
        """
        Numeric field: Computation of decimals from the step.
        """
        print("Numeric field: Computation of decimals from the step:")
        app = QApplication(sys.argv)
        self.gui = kekse.ProtoKeks("Simple Keks")
        self.gui.add_tabs("Control Tabs", tabs=['Tab 1'])
        self.gui.add_label('Representation of Pi: from step to decimals', 'Tab 1')
        self.gui.add_numeric_field('Step=1, Decimals=0', 'Tab 1', value=np.pi, vrange=[0, 100, 1])
        self.assertEqual(self.gui.get_param('Step=1, Decimals=0').decimals(), 0)
        self.gui.add_numeric_field('Step=2, Decimals=0', 'Tab 1', value=np.pi, vrange=[0, 100, 2])
        self.assertEqual(self.gui.get_param('Step=2, Decimals=0').decimals(), 0)
        self.gui.add_numeric_field('Step=0.1, Decimals=1', 'Tab 1', value=np.pi, vrange=[0, 100, 0.1])
        self.assertEqual(self.gui.get_param('Step=0.1, Decimals=1').decimals(), 1)
        self.gui.add_numeric_field('Step=0.01, Decimals=2', 'Tab 1', value=np.pi, vrange=[0, 100, 0.01])
        self.assertEqual(self.gui.get_param('Step=0.01, Decimals=2').decimals(), 2)
        self.gui.add_numeric_field('Step=0.03, Decimals=2', 'Tab 1', value=np.pi, vrange=[0, 100, 0.03])
        self.assertEqual(self.gui.get_param('Step=0.03, Decimals=2').decimals(), 2)
        self.gui.show()
        app.exec_()


if __name__ == '__main__':
    unittest.main()
