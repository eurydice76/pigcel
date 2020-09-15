"""This modules implements the following classes:
    - PlotsWidget
"""

import datetime
import logging

from PyQt5 import QtWidgets

from pylab import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.dates import DateFormatter

from pigcel.kernel.readers.excel_reader import ExcelWorkbookReader
from pigcel.kernel.utils.time_io import add_time
from pigcel.gui.utils.navigation_toolbar import NavigationToolbarWithExportButton


class PlotsWidget(QtWidgets.QWidget):
    """This class implements the widget that will store the monitoring plots.
    """

    def __init__(self, main_window):
        """Constructor.

        Args:
            main_window (PyQt5.QtWidgets.QMainWindow): the main window
        """
        super(PlotsWidget, self).__init__(main_window)

        self._main_window = main_window

        self.init_ui()

    def build_events(self):
        """Build the signal/slots
        """

        self._main_window.update_property_plot.connect(self.on_update_property_plot)
        self._main_window.update_time_plot.connect(self.on_update_time_plot)

    def build_layout(self):
        """Build the layout.
        """

        main_layout = QtWidgets.QHBoxLayout()

        property_plot_layout = QtWidgets.QVBoxLayout()
        property_plot_layout.addWidget(self._property_plot_canvas)
        property_plot_layout.addWidget(self._property_plot_toolbar)
        main_layout.addLayout(property_plot_layout)

        time_plot_layout = QtWidgets.QVBoxLayout()
        time_plot_layout.addWidget(self._time_plot_canvas)
        time_plot_layout.addWidget(self._time_plot_toolbar)
        main_layout.addLayout(time_plot_layout)

        self.setLayout(main_layout)

    def build_widgets(self):
        """Build the widgets.
        """

        self._property_plot_figure = Figure()
        self._property_plot_axes = self._property_plot_figure.add_subplot(111)
        self._property_plot_canvas = FigureCanvasQTAgg(self._property_plot_figure)
        self._property_plot_toolbar = NavigationToolbarWithExportButton(self._property_plot_canvas, self)

        self._time_plot_figure = Figure()
        self._time_plot_axes = self._time_plot_figure.add_subplot(111)
        self._time_plot_canvas = FigureCanvasQTAgg(self._time_plot_figure)
        self._time_plot_toolbar = NavigationToolbarWithExportButton(self._time_plot_canvas, self)

    def init_ui(self):
        """Initializes the ui
        """

        self.build_widgets()

        self.build_layout()

        self.build_events()

    def on_update_property_plot(self, data):
        """Updates the plot showing a given property against time.

        Args:
            data (tuple): the data to plot
        """

        selected_property, data_per_animal = data

        animals = [v[0] for v in data_per_animal]

        all_animals_values = [v[1] for v in data_per_animal]

        self._property_plot_axes.clear()
        self._property_plot_axes.set_xlabel('time')
        self._property_plot_axes.set_ylabel(selected_property)

        x_axis_format = DateFormatter('%Hh%M')
        self._property_plot_axes.xaxis.set_major_formatter(x_axis_format)

        all_dates = set()
        real_times = set()
        for values_per_animal in all_animals_values:

            times = [add_time(t, 30) for t in values_per_animal.index]
            dates = [datetime.datetime.strptime(t, '%Hh%M') for t in times]

            all_dates.update(dates)
            real_times.update(values_per_animal.index)
            self._property_plot_axes.plot(dates, values_per_animal, '.')

        self._property_plot_axes.set_xticks(sorted(all_dates))
        self._property_plot_axes.set_xticklabels(sorted(real_times), rotation=25)
        self._property_plot_axes.legend(animals)

        self._property_plot_canvas.draw()

    def on_update_time_plot(self, data):
        """Updates the plot showing a given property at a given time against animals.

        Args:
            data (tuple): the data to plot
        """

        selected_property, selected_time, data_per_animal = data

        animals = [v[0] for v in data_per_animal]

        all_animals_values = [v[1] for v in data_per_animal]

        self._time_plot_axes.clear()
        self._time_plot_axes.set_xlabel('Animal')
        self._time_plot_axes.set_ylabel('{} @ {}'.format(selected_property, selected_time))

        self._time_plot_axes.plot(animals, all_animals_values, 'o')

        self._time_plot_canvas.draw()
