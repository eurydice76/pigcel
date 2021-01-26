import logging

import numpy as np

from PyQt5 import QtCore, QtWidgets

import matplotlib.ticker as ticker
from pylab import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.dates import DateFormatter

from pigcel.kernel.utils.time_io import add_time


class GroupMediansDialog(QtWidgets.QDialog):
    """This class implements a dialog that will show the averages of a given property for the groups defined so far.
    """

    def __init__(self, selected_property, data_per_group, parent):

        super(GroupMediansDialog, self).__init__(parent)

        self._selected_property = selected_property

        self._data_per_group = data_per_group

        self.init_ui()

    def build_events(self):
        """Set the signal/slots.
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

        self.setWindowTitle('Group medians for {} property'.format(self._selected_property))

        # Build the matplotlib imsho widget
        self._figure = Figure()
        self._canvas = FigureCanvasQTAgg(self._figure)
        self._toolbar = NavigationToolbar2QT(self._canvas, self)

        self._selected_group_combo = QtWidgets.QComboBox()
        group_names = list(self._data_per_group.keys())
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

        data = self._data_per_group[group]

        data.sort_index(inplace=True)

        nan_filtered_data = [[v for v in row if not np.isnan(v)] for _, row in data.iterrows()]

        self._figure.clear()
        self._axes = self._figure.add_subplot(111)
        self._axes.set_xlabel('time')
        self._axes.set_ylabel(self._selected_property)

        self._plot = self._axes.boxplot(nan_filtered_data, showfliers=True)

        self._axes.set_xticklabels(data.index)

        for tick in self._axes.xaxis.get_major_ticks():
            tick.label.set_fontsize(8)
            tick.label.set_rotation('vertical')

        self._canvas.draw()
