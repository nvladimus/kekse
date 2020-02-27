# pytroller
An attempt to make modular GUI software for microscope control, 
where individual modules can be mixed and matched (relatively) easily.

Design principles: 
* Per device: 1 module, 1 file, 1 main class, 1 (optional) GUI panel. 
* Device modules are independent from each other and self-contained, 
similar to LabView virtual instruments. Each module can be run on it's own, 
or envoked from a higher-level code (eg. from `gui_demo.py`)
* GUI panel can be (optionally) launched when initializing a module.
* GUI is minimal but extendable, abstracted via `widget.py` (PyQt5).

In development...

Python 3.6
