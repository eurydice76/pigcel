"""This module implements the following classes:
    - TimeEffectDialog
"""

import logging
import os

import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets

from pylab import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT

from pigcel.gui.models.pvalues_data_model import PValuesDataModel
from pigcel.gui.models.valid_times_model import ValidTimesModel
from pigcel.gui.utils.navigation_toolbar import NavigationToolbarWithExportButton
from pigcel.gui.views.copy_pastable_tableview import CopyPastableTableView


class TimeEffectDialog(QtWidgets.QDialog):
    """This class implements the dialog that shows the group effect. It is made of three plots which plots respectively the
    number of groups used to perform the statistical test, the p value resulting from the kruskal-wallis or Mann-Whitney
    statistical test and the group-pairwise p values resulting from the Dunn test.
    """

    def __init__(self, selected_property, global_effect, pairwise_effect, times_per_group, parent=None):
        """
        """

        super(TimeEffectDialog, self).__init__(parent)

        self._selected_property = selected_property

        self._global_effect = global_effect

        self._pairwise_effect = pairwise_effect

        self._times_per_group = times_per_group

        self.init_ui()

    def build_events(self):
        """Build the signal/slots
        """

        self._global_effect_tableview.selectionModel().selectionChanged.connect(self.on_select_group)
        self._selected_group.currentIndexChanged.connect(self.on_select_pairwise_effect)
        self._pairwise_effect_tableview.customContextMenuRequested.connect(self.on_show_pairwise_effect_table_menu)

    def build_layout(self):
        """Build the layout.
        """

        main_layout = QtWidgets.QVBoxLayout()

        global_effect_groupbox_layout = QtWidgets.QHBoxLayout()
        global_effect_groupbox_layout.addWidget(self._global_effect_tableview)
        global_effect_groupbox_layout.addWidget(self._valid_times_listview)
        self._global_effect_groupbox.setLayout(global_effect_groupbox_layout)
        main_layout.addWidget(self._global_effect_groupbox)

        pairwise_effect_groupbox_layout = QtWidgets.QVBoxLayout()
        pairwise_effect_groupbox_layout.addWidget(self._selected_group)
        pairwise_effect_groupbox_layout.addWidget(self._pairwise_effect_tableview)
        self._pairwise_effect_groupbox.setLayout(pairwise_effect_groupbox_layout)
        main_layout.addWidget(self._pairwise_effect_groupbox)

        self.setGeometry(0, 0, 600, 600)

        self.setLayout(main_layout)

    def build_widgets(self):
        """Build and/or initialize the widgets of the dialog.
        """

        self.setWindowTitle('Time effect statistics for {} property'.format(self._selected_property))

        self._global_effect_groupbox = QtWidgets.QGroupBox('Global effect (Friedman test)')

        self._global_effect_tableview = CopyPastableTableView()
        self._global_effect_tableview.setSelectionMode(QtWidgets.QTableView.SingleSelection)
        model = PValuesDataModel(self._global_effect, self)
        self._global_effect_tableview.setModel(model)
        for col in range(model.columnCount()):
            self._global_effect_tableview.horizontalHeader().setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)

        self._valid_times_listview = QtWidgets.QListView()

        self._pairwise_effect_groupbox = QtWidgets.QGroupBox('Pairwise effect (Dunn test)')

        self._selected_group = QtWidgets.QComboBox()
        self._selected_group.addItems(self._pairwise_effect.keys())

        self._pairwise_effect_tableview = CopyPastableTableView()
        self._pairwise_effect_tableview.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

    def init_ui(self):
        """Initialiwes the dialog.
        """

        self.build_widgets()

        self.build_layout()

        self.build_events()

        self.on_select_pairwise_effect(0)

    def on_select_group(self, indexes):
        """Event handler called when the user select a different group from the global effect group table view.

        Args:
            indexes (PyQt5.QtCore.QItemSelection): the selected indexes
        """

        selected_row = [index.row() for index in indexes.indexes()][0]

        group = self._global_effect_tableview.model().headerData(selected_row, QtCore.Qt.Vertical, QtCore.Qt.DisplayRole)

        valid_times_model = ValidTimesModel(self._times_per_group[group], self)

        self._valid_times_listview.setModel(valid_times_model)

    def on_select_pairwise_effect(self, index):
        """Event handler called when the user select a different group from the group selection combo box.

        Args:
            index (int): the index of the newly selected time
        """

        selected_group = self._selected_group.currentText()

        model = PValuesDataModel(self._pairwise_effect[selected_group], self)
        self._pairwise_effect_tableview.setModel(model)

        for col in range(model.columnCount()):
            self._pairwise_effect_tableview.horizontalHeader().setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)

    def on_export_dunn_table(self):
        """Export the current Dunn table to a csv file.
        """

        model = self._pairwise_effect_tableview.model()
        if model is None:
            return

        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, caption='Export statistics as ...', filter="Excel files (*.xls *.xlsx)")
        if not filename:
            return

        filename_noext, ext = os.path.splitext(filename)
        if ext not in ['.xls', '.xlsx']:
            logging.warning('Bad file extension for output excel file {}. It will be replaced by ".xlsx"'.format(filename))
            filename = filename_noext + '.xlsx'

        model.export(filename)

    def on_show_dunn_matrix(self):
        """Show the current Dunn matrix.
        """

        model = self._pairwise_effect_tableview.model()
        if model is None:
            return

        plot_dialog = QtWidgets.QDialog(self)

        plot_dialog.setGeometry(0, 0, 300, 300)

        plot_dialog.setWindowTitle('Dunn matrix')

        figure = Figure()
        axes = figure.add_subplot(111)
        canvas = FigureCanvasQTAgg(figure)
        toolbar = NavigationToolbar2QT(canvas, self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(canvas)
        layout.addWidget(toolbar)
        plot_dialog.setLayout(layout)

        n_rows = model.rowCount()
        n_cols = model.columnCount()

        matrix = np.empty((n_rows, n_cols), dtype=np.float)
        for r in range(n_rows):
            for c in range(n_cols):
                index = model.index(r, c)
                matrix[r, c] = model.data(index, QtCore.Qt.DisplayRole)

        times = [model.headerData(row, QtCore.Qt.Vertical, role=QtCore.Qt.DisplayRole) for row in range(model.rowCount())]

        axes.clear()
        plot = axes.imshow(matrix, aspect='equal', origin='lower', interpolation='nearest')
        axes.set_xlabel('time')
        axes.set_ylabel('time')
        axes.set_xticks(range(0, n_rows))
        axes.set_yticks(range(0, n_cols))
        axes.set_xticklabels(times)
        axes.set_yticklabels(times)
        figure.colorbar(plot)

        canvas.draw()

        plot_dialog.show()

    def on_show_pairwise_effect_table_menu(self, point):
        """Pops up the contextual menu of the pairwise effect table.

        Args:
            point(PyQt5.QtCore.QPoint) : the position of the contextual menu
        """

        menu = QtWidgets.QMenu()

        export_action = menu.addAction('Export')
        show_matrix_action = menu.addAction('Show matrix')

        export_action.triggered.connect(self.on_export_dunn_table)
        show_matrix_action.triggered.connect(self.on_show_dunn_matrix)

        menu.exec_(QtGui.QCursor.pos())
