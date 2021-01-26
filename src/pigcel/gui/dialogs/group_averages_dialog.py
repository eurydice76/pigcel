import datetime
import logging

from PyQt5 import QtCore, QtWidgets

import matplotlib.ticker as ticker
from pylab import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.dates import DateFormatter

from pigcel.gui.utils.navigation_toolbar import NavigationToolbarWithExportButton
from pigcel.kernel.utils.time_io import add_time


class GroupAveragesDialog(QtWidgets.QDialog):
    """This class implements a dialog that will show the averages of a given property for the groups defined so far.
    """

    def __init__(self, selected_property, reduced_data_per_group, parent):

        super(GroupAveragesDialog, self).__init__(parent)

        self._selected_property = selected_property

        self._reduced_data_per_group = reduced_data_per_group

        self.init_ui()

    def build_events(self):
        """Set the signal/slots of the main window
        """

        self._selected_group_combo.currentIndexChanged.connect(self.on_select_group)

    def build_layout(self):
        """Build the layout.
        """

        main_layout = QtWidgets.QVBoxLayout()

        main_layout.addWidget(self._canvas)
        main_layout.addWidget(self._toolbar)

        main_layout.addWidget(self._selected_group_combo)

        self.setGeometry(0, 0, 400, 400)

        self.setLayout(main_layout)

    def build_widgets(self):
        """Build and/or initialize the widgets of the dialog.
        """

        self.setWindowTitle('Group averages for {} property'.format(self._selected_property))

        # Build the matplotlib imsho widget
        self._figure = Figure()
        self._canvas = FigureCanvasQTAgg(self._figure)
        self._toolbar = NavigationToolbarWithExportButton(self._canvas, self)

        self._selected_group_combo = QtWidgets.QComboBox()
        group_names = ['all'] + list(self._reduced_data_per_group.keys())
        self._selected_group_combo.addItems(group_names)

    def init_ui(self):
        """Initialiwes the dialog.
        """

        self.build_widgets()

        self.build_layout()

        self.build_events()

        self.on_select_group(0)

    def on_select_group(self, row):
        """Plot the averages and standard deviations over record intervals for a selected group.

        Args:
            row (int): the selected group
        """

        selected_group_model = self._selected_group_combo.model()
        if selected_group_model.rowCount() == 0:
            return

        group = selected_group_model.item(row, 0).data(QtCore.Qt.DisplayRole)
        if group == 'all':
            selected_groups = list(self._reduced_data_per_group.keys())
        else:
            selected_groups = [group]

        self._figure.clear()

        self._axes = self._figure.add_subplot(111)
        self._axes.set_xlabel('time')
        self._axes.set_ylabel(self._selected_property)

        x_axis_format = DateFormatter('%Hh%M')
        self._axes.xaxis.set_major_formatter(x_axis_format)

        for group in selected_groups:

            times = self._reduced_data_per_group[group]['mean'].index

            y = self._reduced_data_per_group[group]['mean']
            yerr = self._reduced_data_per_group[group]['std']

            self._axes.errorbar(times, y, yerr=yerr, fmt='o')

        group_names = selected_groups

        # self._axes.set_xticks(sorted(all_dates))
        self._axes.set_xticklabels(times, rotation=25)

        for tick in self._axes.xaxis.get_major_ticks():
            tick.label.set_fontsize(8)
            tick.label.set_rotation('vertical')

        self._axes.legend(group_names)

        self._canvas.draw()
