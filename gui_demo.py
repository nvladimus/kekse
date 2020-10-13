"""
Demo of launching several modules from a python program.
Copyright Nikita Vladimirov, @nvladimus 2020
"""
import kekse
import sys
from PyQt5 import QtWidgets
from functools import partial
import devices


def load_device(dev_title: str):
    if dev_title == "template":
        dev = devices.device_template.Device()
    elif dev_title == "camera":
        dev = devices.hamamatsu_camera.CamController()
    elif dev_title == "thorlabs motion":
        dev = devices.motion_controller_Thorlabs_MCM3000.MotionController()
    elif dev_title == "asi motion":
        dev = devices.stage_ASI_MS2000.MotionController()
    elif dev_title == "lightsheet":
        dev = devices.lightsheet_generator.LightsheetGenerator()
    elif dev_title == "etl":
        dev = devices.etl_controller_Optotune.ETLController()
    elif dev_title == "dm":
        dev = devices.deformable_mirror_Mirao52e.DmController()
    dev.gui.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui = kekse.ProtoKeks("GUI demo")
    gui.add_button("Device template", func=partial(load_device, "template"))
    gui.add_button("Camera Hamamatsu", func=partial(load_device, "camera"))
    gui.add_button("Thorlabs motion MCM3000", func=partial(load_device, "thorlabs motion"))
    gui.add_button("ASI motion MS2000", func=partial(load_device, "asi motion"))
    gui.add_button("Lightsheet DAQ generator", func=partial(load_device, "lightsheet"))
    gui.add_button("Optotune ETL", func=partial(load_device, "etl"))
    gui.add_button("Deformable mirror Mirao52e", func=partial(load_device, "dm"))
    gui.show()
    app.exec_()
