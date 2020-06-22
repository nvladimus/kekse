"""
Demo of launching several modules from a python program.
Copyright Nikita Vladimirov, @nvladimus 2020
"""
import sys
from PyQt5 import QtWidgets
import motion_controller_Thorlabs_MCM3000 as Controller
import etl_controller_Optotune as Etl
import stage_ASI_MS2000 as stage_ASI
import deformable_mirror_Mirao52e as def_mirror
import hamamatsu_camera as cam
import lightsheet_generator as lsg

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    # Thorlabs stage controller:
    dev1 = Controller.MotionController()
    dev1.gui.show()

    # Optotune ETL:
    dev2 = Etl.ETL_controller()
    dev2.gui.show()

    #ASI MS2000:
    dev3 = stage_ASI.MotionController()
    dev3.gui.show()

    # DM Mirao52e:
    dev4 = def_mirror.DmController()
    dev4.gui.show()
    
    # Hamamatsu Orca4.0 control:
    dev5 = cam.CamController()
    dev5.gui.show()
    
    # Light-sheet DAQmx waveform generator, with optional Arduino device:
    dev6 = lsg.LightsheetGenerator()
    dev6.gui.show()

    app.exec_()
