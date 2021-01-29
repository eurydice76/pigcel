"""This module implements the following classes:
    - GroupEffectDialog
"""

import logging

from PyQt5 import QtWidgets

from pylab import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from pigcel.gui.models.pandas_data_model import PandasDataModel
from pigcel.gui.models.pvalues_data_model import PValuesDataModel
from pigcel.gui.utils.navigation_toolbar import NavigationToolbarWithExportButton
from pigcel.gui.views.copy_pastable_tableview import CopyPastableTableView


class GroupEffectDialog(QtWidgets.QDialog):
    """This class implements the dialog that shows the group effect. It is made of three plots which plots respectively the
    number of groups used to perform the statistical test, the p value resulting from the kruskal-wallis or Mann-Whitney
    statistical test and the group-pairwise p values resulting from the Dunn test.
    """

    def __init__(self, selected_property, global_effect, pairwise_effect,  parent=None):
        """Constructor.

        Args:
            selected_property (str): the selected property
            global_effect (pandas.DataFrame): the global group effect data
            pairwise_effect (collections.OrderedDict): the pairwise group effect data
            parent (QtCore.QObject): the parent widget
        """

        super(GroupEffectDialog, self).__init__(parent)

        self._selected_property = selected_property

        self._global_effect = global_effect

        self._pairwise_effect = pairwise_effect

        self.init_ui()

    def build_events(self):
        """Build the signal/slots
        """

        self._selected_time.currentIndexChanged.connect(self.on_select_time)
        self._plot_button.clicked.connect(self.on_display_p_value_plot)

    def build_layout(self):
        """Build the layout.
        """

        main_layout = QtWidgets.QVBoxLayout()

        global_effect_groupbox_layout = QtWidgets.QVBoxLayout()
        global_effect_groupbox_layout.addWidget(self._global_effect_tableview)
        self._global_effect_groupbox.setLayout(global_effect_groupbox_layout)
        main_layout.addWidget(self._global_effect_groupbox)

        pairwise_effect_groupbox_layout = QtWidgets.QVBoxLayout()
        pairwise_effect_groupbox_layout.addWidget(self._selected_time)
        pairwise_effect_groupbox_layout.addWidget(self._pairwise_effect_tableview)
        plot_layout = QtWidgets.QHBoxLayout()
        plot_layout.addWidget(self._selected_group_1)
        plot_layout.addWidget(self._selected_group_2)
        plot_layout.addWidget(self._plot_button)
        pairwise_effect_groupbox_layout.addLayout(plot_layout)
        self._pairwise_effect_groupbox.setLayout(pairwise_effect_groupbox_layout)
        main_layout.addWidget(self._pairwise_effect_groupbox)

        self.setGeometry(0, 0, 600, 600)

        self.setLayout(main_layout)

    def build_widgets(self):
        """Build and/or initialize the widgets of the dialog.
        """

        self.setWindowTitle('Group effect statistics for {} property'.format(self._selected_property))

        self._global_effect_groupbox = QtWidgets.QGroupBox('Global effect (Mann-Whitney/Kruskal-Wallis test)')

        self._global_effect_tableview = CopyPastableTableView()
        model = PValuesDataModel(self._global_effect, self)
        self._global_effect_tableview.setModel(model)
        for col in range(model.columnCount()):
            self._global_effect_tableview.horizontalHeader().setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)

        self._pairwise_effect_groupbox = QtWidgets.QGroupBox('Pairwise effect (Dunn test)')

        self._selected_time = QtWidgets.QComboBox()
        self._selected_time.addItems(self._pairwise_effect.keys())

        self._pairwise_effect_tableview = CopyPastableTableView()

        self._selected_group_1 = QtWidgets.QComboBox()
        self._selected_group_1.addItems(self._pairwise_effect['-0h30'].columns)

        self._selected_group_2 = QtWidgets.QComboBox()
        self._selected_group_2.addItems(self._pairwise_effect['-0h30'].columns)

        self._plot_button = QtWidgets.QPushButton('Plot')

    def init_ui(self):
        """Initialiwes the dialog.
        """

        self.build_widgets()

        self.build_layout()

        self.build_events()

        self.on_select_time(0)

    def on_display_p_value_plot(self):
        """Event handler fired when the user click on the plot button of the dialog.
        """

        group1 = self._selected_group_1.currentText()
        group2 = self._selected_group_2.currentText()

        x = list(self._pairwise_effect.keys())
        y = []
        for data_frame in self._pairwise_effect.values():
            y.append(data_frame.loc[group1, group2])

        plot_widget = QtWidgets.QDialog(self)

        plot_widget.setGeometry(0, 0, 300, 300)

        plot_widget.setWindowTitle('p-values vs time for {} vs {} for {} property'.format(group1, group2, self._selected_property))

        figure = Figure()
        axes = figure.add_subplot(111)
        canvas = FigureCanvasQTAgg(figure)
        toolbar = NavigationToolbarWithExportButton(canvas, plot_widget)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(canvas)
        layout.addWidget(toolbar)
        plot_widget.setLayout(layout)

        axes.set_xlabel('time')
        axes.set_ylabel('p_value')
        axes.plot(x, y, 'o')
        canvas.draw()

        plot_widget.show()

    def on_select_time(self, index):
        """Event handler called when the user select a different time from the time selection combo box.

        Args:
            index (int): the index of the newly selected time
        """

        selected_time = self._selected_time.currentText()

        model = PValuesDataModel(self._pairwise_effect[selected_time], self)
        self._pairwise_effect_tableview.setModel(model)

        for col in range(model.columnCount()):
            self._pairwise_effect_tableview.horizontalHeader().setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)
