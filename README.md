# kekse
PyQt interface for quick building of instrument control software, with GUI frontend. Implied to be as simple as keks :cookie:

Design principles: 
* minimalism: 
    - each device has one module which is one file containing one main class
    - minimum external dependencies
    - GUI is simple (no fancy styles), but easy to build and extend, and can be turned on/off
* independence: modules are independent from each other and self-contained, 
similar to LabView virtual instruments. 
* *what you see is what you get:* widget labels in the GUI are actual widget names in the code, so you know exactly how to access anything.
* versatility: a module can be run on it's own (from command line), or envoked from a master python program

### Installation
The current code requires Python 3.6 and a few other libraries:

```
pip install PyQt5 
pip install pyserial
```
 
Once there, clone this repo and run 

```
python gui_demo.py
```

This will launch several available modules as independent windows.

## Making your own keks
GUI generation is abstracted via local library file `widget.py` to hide the unnecessary details of PyQt5 API. 
To create your own keks, a good starting point is looking into the template code in [device_template.py](device_template.py). Adding a new GUI widget is a one liner:
```
self.gui.add_numeric_field('Parameter 1', tab_name, value=self.config['param1'], vmin=0.1, vmax=100, decimals=1, func=partial(self.update_config, 'param1'))
```
This creates an input field `Parameter 1`, initiates it from `config` dictionary, sets limits and precision, and defines which function is called when the input value is changed. Launching it from command line `python device_template.py` displays the GUI. 

![Device template GUI](./images/dev_template.png)

The whole GUI code is shown below
```
    def _setup_gui(self):
        self.gui.add_tabs("Control Tabs", tabs=['Tab 1', 'Tab 2'])
        tab_name = 'Tab 1'
        self.gui.add_button('Initialize', tab_name, func=self.initialize)
        self.gui.add_numeric_field('Parameter 1', tab_name, value=self.config['param1'],
                                   vmin=0.1, vmax=100, decimals=1,
                                   func=partial(self.update_config, 'param1'))
        self.gui.add_string_field('Parameter 2', tab_name, value=self.config['param2'], enabled=False)
        self.gui.add_checkbox('Parameter 3', tab_name,  value=self.config['param3_check'],
                              func=partial(self.update_config, 'param3_check'))
        self.gui.add_combobox('Parameter 4', tab_name, items=['option1', 'option2'],
                              value=self.config['param4combo'], func=partial(self.update_config, 'param4combo'))
        self.gui.add_button('Disconnect', tab_name, lambda: self.close())
```
### GUI labels as widget names
Note the *what you see is what you get* principle, so `Parameter 1` is both the label on the GUI panel and the name of numeric field widget in the code. For example, function `_update_gui()` will call it `Parameter 1` to update it's value from the `config` dictionary:
```
    def _update_gui(self):
        self.gui.update_param('Parameter 1', self.config['param1'])
        ...
```
So, keep an eye on the blank space between label words.

### Keks usage
Keks is just a Python class, so all its methods are accessible from a master program that created the keks object. So, the master program can call any keks function:
```
dev0 = dev_template.Device()
dev0.gui.show()
dev0.do_something()
```

## Advanced control
The [daoSPIM](https://github.com/nvladimus/daoSPIM/tree/master/microscope_control) project uses kekse connected together for microscope control, with signals/slots and multithreading on top.

To be continued...
