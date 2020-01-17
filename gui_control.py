import sys
from PyQt5 import QtWidgets
import motion_controller_Thorlabs_MCM3000 as controller

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    dev1 = controller.MotionController()
    dev1.gui.show()
    app.exec_()
