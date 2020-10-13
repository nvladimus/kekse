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
    if dev_title == "Device template":
        dev = devices.device_template.Device()
    elif dev_title == "Camera Hamamatsu":
        dev = devices.hamamatsu_camera.CamController()
    #
    # motion_controller_Thorlabs_MCM3000,
    # etl_controller_Optotune,
    # stage_ASI_MS2000,
    # deformable_mirror_Mirao52e,
    # hamamatsu_camera,
    # lightsheet_generator

    dev.gui.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui = kekse.ProtoKeks("GUI demo")
    gui.add_button("Device template", func=partial(load_device, "Device template"))
    gui.add_button("Camera Hamamatsu", func=partial(load_device, "Camera Hamamatsu"))
    gui.show()
    app.exec_()
