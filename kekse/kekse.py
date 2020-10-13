"""
Interface for abstraction of several PyQt widgets, to speed up GUI development in new modules.
Copyright Nikita Vladimirov, @nvladimus 2020
"""

from PyQt5.QtWidgets import (QGroupBox, QLineEdit, QPushButton, QTabWidget, QCheckBox, QComboBox,
                             QVBoxLayout, QWidget, QDoubleSpinBox, QFormLayout, QLabel)
import PyQt5.QtCore
import numpy as np


class ProtoKeks(QWidget):
    """Base class for GUI widgets."""
    def __init__(self, title='Control window'):
        """
        Parameters:
        :param title: str
        """
        super().__init__()
        self.setWindowTitle(title)
        self.containers = {}
        self.params = {}
        self.layouts = {}
        self.layout_window = QVBoxLayout(self)

    def _insert_widget(self, title, parent, container=False):
        if parent is None:
            if container:
                self.layout_window.addWidget(self.containers[title])
            else:
                self.layout_window.addWidget(self.params[title])
        else:
            assert parent in self.layouts, f"Parent container name not found: {parent}"
            if container:
                self.layouts[parent].addWidget(self.containers[title])
            else:
                self.layouts[parent].addRow(self.params[title])

    def add_tabs(self, title, tabs=['Tab1', 'Tab2'], parent=None):
        """Add a tabs container.
        Parameters:
            :param title: str
                A unique string ID for this group of tabs
            :param tabs: list of str,
                Names of tabs, e.g. ['Tab1', 'Tab2']
        """
        assert len(tabs) > 0, "Define the list of tab names (len > 1)"
        assert title not in self.containers, f"Container name already exists:{title}"
        for tab_name in tabs:
            assert tab_name not in self.containers, f"Container name already exists:{tab_name}"
        self.containers[title] = QTabWidget()
        self._insert_widget(title, parent, container=True)
        for i in range(len(tabs)):
            new_tab = QWidget()
            self.containers[title].addTab(new_tab, tabs[i])
            self.containers[tabs[i]] = new_tab
            self.layouts[tabs[i]] = QFormLayout()
            self.containers[tabs[i]].setLayout(self.layouts[tabs[i]])

    def add_groupbox(self, title='Group 1', parent=None):
        """ Add a groupbox container.
        Parameters
        :param title: str
        :param parent: str
                Name of the existing parent container. If None (default), the widget is added directly
                to the main window.
        """
        assert title not in self.containers, "Container name already exists"
        self.containers[title] = QGroupBox(title)
        self.layouts[title] = QFormLayout()
        self.containers[title].setLayout(self.layouts[title])
        self._insert_widget(title, parent, container=True)

    def add_numeric_field(self, title, parent=None,
                          value=0, vrange=[-1e6, 1e6, 1],
                          enabled=True, max_width=100,
                          func=None, **func_args):
        """Add a QDoubleSpinBox() widget to the parent container widget.
        Parameters
            :param title: str
                Label of the parameter. Also, serves as system name of the widget. Beware of typos!
            :param parent: str
                Name of the parent container
            :param value: float
                Initial value.
            :param: vrange: list of 3 scalars
                List of [minimum, maximum, step] values, e.g. [0, 100, 1]. Default [-1e6, 1e6, 1].
            :param enabled: Boolean
                If True, the value can be edited. If False, it is grayed out.
            :param func: function reference
                Name of the function which must be called every time the value is changed.
            :param: **func_args:
                Function's additional key-value parameters (dictionary), besides the field value.
            :return: None
        """
        assert title not in self.params, "Widget name already exists: {title}"
        assert len(vrange) == 3, "The vrange parameter must be a list of 3 scalars: [min, max, step]."
        assert vrange[0] <= value <= vrange[1], "Value lies outside of (min,max) range."
        self.params[title] = QDoubleSpinBox()
        self.params[title].setLocale(PyQt5.QtCore.QLocale(PyQt5.QtCore.QLocale.English, PyQt5.QtCore.QLocale.UnitedStates)) # comma -> period: 0,1 -> 0.1
        step = vrange[2]
        self.params[title].setSingleStep(step)
        decimals = int(max(-np.floor(np.log10(step)), 0))
        self.params[title].setDecimals(decimals)
        self.params[title].setRange(vrange[0], vrange[1])
        self.params[title].setValue(value)
        self.params[title].setEnabled(enabled)
        self.params[title].setMaximumWidth(int(max_width))
        self.params[title].setAlignment(PyQt5.QtCore.Qt.AlignRight)
        self._insert_widget(title, parent)
        if enabled and func is not None:
            self.params[title].editingFinished.connect(lambda: func(self.params[title].value(), **func_args))
            # editingFinished() preferred over valueChanged() because the latter is too jumpy, doesn't let finish input.

    def add_string_field(self, title, parent=None, value='', enabled=True, func=None, max_width=100):
        """ Add a QLineEdit() widget to the parent container widget (groupbox or tab).
        :param title: str
                Label of the parameter. Also, serves as system name of the widget. Beware of typos!
        :param parent: str
                Name of the parent container
        :param value: str
                Initial value of the field.
        :param enabled: bool
            If True, user can edit value.
        :param func: function reference
                Name of the function which must be called every time the value is changed.
        :param nchars: int
            min number of characters to display
        :return: None
        """
        assert parent in self.layouts, f"Parent container name not found: {parent}"
        assert title not in self.params, f"Widget name already exists: {title}"
        self.params[title] = QLineEdit(value)
        self.params[title].setEnabled(enabled)
        self.params[title].setMaximumWidth(int(max_width))
        self.params[title].setAlignment(PyQt5.QtCore.Qt.AlignRight)
        self._insert_widget(title, parent)
        if enabled and func is not None:
            self.params[title].editingFinished.connect(lambda: func(self.params[title].text()))

    def add_label(self, title, parent=None):
        assert title not in self.params, f"Widget name already exists: {title}"
        self.params[title] = QLabel(title)
        self._insert_widget(title, parent)

    def add_button(self, title, parent=None, func=None):
        """Add a button to a parent container widget (groupbox or tab).
            Parameters
            :param title: str
                Name of the button. Also, serves as system name of the widget. Beware of typos!
            :param parent: str
                Name of the parent container.
            :param: func: function reference
                Name of the function that is executed on button click.
        """
        assert title not in self.params, "Widget name already exists: {title}"
        self.params[title] = QPushButton(title)
        if func is not None:
            self.params[title].clicked.connect(func)
        self._insert_widget(title, parent)

    def add_checkbox(self, title, parent=None, value=False, enabled=True, func=None):
        """Add a checkbox to a parent container widget (groupbox or tab).
            Parameters
            :param title: str
                Name of the checkbox. Also, serves as system name of the widget. Beware of typos!
            :param parent: str
                Name of the parent container.
            :param value: Boolean
            :param: enabled: Boolean
            :param: func: function reference
                Name of the function that is executed on button click.
        """
        assert parent in self.layouts.keys(), "Parent container name not found: " + parent + "\n"
        assert title not in self.params.keys(), "Button name already exists: " + title + "\n"
        self.params[title] = QCheckBox(title)
        self.params[title].setChecked(value)
        self.params[title].setEnabled(enabled)
        if enabled and func is not None:
            self.params[title].stateChanged.connect(lambda: func(self.params[title].isChecked()))
        self._insert_widget(title, parent)

    def add_combobox(self, title, parent=None, items=['Item1', 'Item2'], value='Item1', enabled=True, func=None):
        """Add a combobox to a parent container widget.
            Parameters
            :param title: str
                Name of the checkbox. Also, serves as system name of the widget. Beware of typos!
            :param parent: str
                Name of the parent container.
            :param items: list of strings (available options)
            :param value: currently selected option
            :param: enabled: Boolean
            :param: func: function reference
                Ref to the function executed when an item is changed.
        """
        assert parent in self.layouts.keys(), f"Parent container name not found: {parent}"
        assert title not in self.params.keys(), f"Widget name already exists: {title}"
        assert value in items, f"Parameter value {value} does not match available options: {items}"
        self.params[title] = QComboBox()
        self.params[title].addItems(items)
        self.params[title].setEnabled(enabled)
        self.params[title].setCurrentText(value)
        if enabled and func is not None:
            self.params[title].currentTextChanged.connect(lambda: func(self.params[title].currentText()))
        self._insert_widget(title, parent)

    def update_param(self, title, value):
        """"Update parameter value, for numeric or string parameter."""
        assert title in self.params, f"{title} field not found"
        if isinstance(self.params[title], QDoubleSpinBox):
            self.params[title].setValue(value)
        elif isinstance(self.params[title], QLineEdit):
            self.params[title].setText(value)

    def get_param(self, title):
        """"Get direct access to the parameter widget using its title"""
        assert title in self.params, f"{title} parameter not found"
        return self.params[title]

