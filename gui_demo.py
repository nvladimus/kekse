import sys
from PyQt5 import QtWidgets
import motion_controller_Thorlabs_MCM3000 as Controller
import etl_controller_Optotune as Etl
import laser_Cobolt_Skyra as Laser

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # Thorlabs stage controller demo:
    dev1 = Controller.MotionController()
    dev1.gui.show()
    # Optotune ETL demo:
    dev2 = Etl.ETL_controller("COM3")
    dev2.gui.show()
    # Cobolt Skyra:
    dev3 = Laser.laser_controller("COM11")
    dev3.gui.show()

    app.exec_()
