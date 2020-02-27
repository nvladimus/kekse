"""
Demo of launching several modules from a python program.
Copyright Nikita Vladimirov, @nvladimus 2020
"""
import sys
from PyQt5 import QtWidgets
import motion_controller_Thorlabs_MCM3000 as Controller
import etl_controller_Optotune as Etl
import stage_ASI_MS2000 as stage_ASI

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # Thorlabs stage controller demo:
    dev1 = Controller.MotionController()
    dev1.gui.show()
    # Optotune ETL demo:
    dev2 = Etl.ETL_controller()
    dev2.gui.show()
    #ASI MS2000:
    dev3 = stage_ASI.MotionController(dev_name="ASI MS2000")
    dev3.gui.show()

    app.exec_()
