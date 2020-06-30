# kekse
PyQt interface for quick building of instrument control software, with optional GUI frontend. Implied to be as simple as keks :cookie:

Design principles: 
* Each device has 1 module: 1 file, 1 main class, 1 (optional) GUI window. 
* Modules are independent from each other and self-contained, 
similar to LabView virtual instruments. Each module can be run on it's own, 
or envoked from a higher-level code (eg. from `gui_demo.py`)
* GUI is minimal but extendable, abstracted via `widget.py` (PyQt5).

### Installation
The code requires Python 3.6 and a few other libraries:

```
pip install PyQt5 
pip install pyserial
```
 
Once there, clone this repo and run 

```
python gui_demo.py
```

This will launch all currenly available modules, and give a basic usage example inside a program.
To launch an individual module, you can also run it from command line, for example

```
python stage_ASI_MS2000.py
```

To be continued...
