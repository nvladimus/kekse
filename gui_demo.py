import sys
from PyQt5 import QtWidgets
import motion_controller_Thorlabs_MCM3000 as controller
import etl_controller_Optotune as etl

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # Thorlabs stage controller demo:
    dev1 = controller.MotionController()
    dev1.gui.show()
    #Optotune ETL demo:
    dev2 = etl.ETL_controller("COM3")
    dev2.gui.show()

    app.exec_()
