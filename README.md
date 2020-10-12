# kekse :cookie:
Kekse is a PyQt5 interface for quick building of GUI, e.g. for instrument control.  

Python 3.6

## Design principles
* minimalism: 
    - each device is represented by one module, contained in one file
    - GUI is ascetic but easy to build and extend
* independence: modules are independent from each other and self-contained, 
similar to LabView virtual instruments. 
* *what you see is what you get:* widget labels in the GUI are actual widget names in the code, so you always know how to access any parameter you see on the panel.
* versatility: a module can be run on it's own (from command line), or envoked from a master python program

### Installation

(optional) Create and activate local environment from the command line, to keep things tidy
```
C:\Users\user\kekse> cd kekse
C:\Users\user\kekse> python -m venv venv
C:\Users\user\kekse> venv\Scripts\activate.bat
(venv) C:\Users\user\kekse>
```
Install dependencies 
```
pip install --upgrade pip
pip install -r requirements.txt
```
Launch a demo program
```
python gui_demo.py
```
Explore the code and make your own kekse.


## Making your own keks
Kekse allows simplified GUI generation via thin abstraction class `keks.ProtoKeks()` that hides the full details of PyQt5 API. 

To create your own keks, a good starting point is looking into the template code in [device_template.py](device_template.py). The basic steps are:
- Create a device class that contains functionality (opening/closing, communication, etc): `class Device(QtCore.QObject):`
- Create the main GUI widget: `self.gui = kekse.ProtoKeks()`
- Populate the GUI with containers (tabs, groupboxes) and controls (numeric fields, buttons, labels, etc)
```
self.gui.add_tabs('Control Tabs', tabs=['Tab 0', 'Tab 1'])
self.gui.add_button('Initialize', parent='Tab 0', func=self.initialize) 
self.gui.add_string_field('Status', parent='Tab 0', value=self._status, enabled=False)
self.gui.add_groupbox('Groupbox 0', parent='Tab 0')
self.gui.add_label('This is just a label', parent='Groupbox 0')
self.gui.add_numeric_field('Parameter 0', parent='Groupbox 0',
                           value=3.14, # Initial value
                           vrange=[0, 100, 0.01], # [min, max, step]
                           func=self.do_something)
```
In the code above, `add_button('Initialize', 'Tab 0', func=self.initialize)` creates a button named *and* labeled `Initialize`, which belongs to parent widget `Tab 0`, and when the button is clicked, function `self.initialize()` is executed.

Every new widget is added to the main window (if `parent=None`), or to the `parent` container. Again, all containers and widgets are referred by their titles (strings), e.g. as `Tab 0`. So, keep an eye on the blank spaces in th titles.

![Device template GUI](./images/dev_template.png)

### Keks usage
Keks is just a Python class, and all its methods are accessible from a master program that created the keks object. So, the master program can call any keks function:
```
dev0 = dev_template.Device()
dev0.gui.show()
dev0.do_something()
```

## Limitations
- Kekse provide only a simplified interface to PyQt for rapid GUI building. The number of widget types and their formatting are very limited for simplicity. If you would like more advanced and professionally looking GUI, consider using full PyQt or [pyqtgraph](http://www.pyqtgraph.org/).
- Only `QFormLayout()` is supported: widgets added in one column, in the order they are written in the code.
- There are no assumptions about device functionality, it is entirely upon the user.

## Advanced control
The [daoSPIM](https://github.com/nvladimus/daoSPIM/tree/master/microscope_control) project uses kekse connected together for microscope control, with signals/slots and multithreading.
