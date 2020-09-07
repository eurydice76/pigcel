"""This module implements the following class:
    - PreMortemStatisticsDialog
"""

import logging

import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets

from pylab import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT

from pigcel.gui.models.pvalues_data_model import PValuesDataModel
from pigcel.gui.views.copy_pastable_tableview import CopyPastableTableView
from pigcel.kernel.readers.excel_reader import ExcelWorkbookReader


class PremortemTimeEffectDialog(QtWidgets.QDialog):
    """This class implements the dialog for premortem time effect analysis.

    It will perform the analysis on a groups of animals pool.
    """

    def __init__(self, groups_model, selected_property, parent=None):
        """Constructor.

        Args:
            groups_model (pigcel.gui.models.animals_groups_model.AnimalsGroupsModel): the group model
            selected_property (str): the selected property
            parent (QtCore.QObject): the parent widget
        """

        super(PremortemTimeEffectDialog, self).__init__(parent)

        self._groups_model = groups_model

        self._selected_property = selected_property

        self.init_ui()

    def build_events(self):
        """Build signal/slots
        """

        self._compute_premortem_statistics_button.clicked.connect(self.on_compute_premortem_time_effect)
        self._selected_group.currentIndexChanged.connect(self.on_select_group)
        self._pairwise_effect_tableview.customContextMenuRequested.connect(self.on_show_pairwise_effect_table_menu)

    def build_layout(self):
        """Build the layout.
        """

        main_layout = QtWidgets.QVBoxLayout()

        hlayout = QtWidgets.QHBoxLayout()

        hlayout.addWidget(self._n_target_times_label)
        hlayout.addWidget(self._n_target_times_spinbox)
        hlayout.addWidget(self._compute_premortem_statistics_button)
        main_layout.addLayout(hlayout)

        global_effect_groupbox_layout = QtWidgets.QVBoxLayout()
        global_effect_groupbox_layout.addWidget(self._global_effect_tableview)
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
        """Build the widgets.
        """

        self.setWindowTitle('Time effect statistics for {} property'.format(self._selected_property))

        self._n_target_times_label = QtWidgets.QLabel('Number of target times')

        self._n_target_times_spinbox = QtWidgets.QSpinBox()
        self._n_target_times_spinbox.setMinimum(1)
        self._n_target_times_spinbox.setMaximum(len(ExcelWorkbookReader.times)-1)
        self._n_target_times_spinbox.setValue(6)

        self._compute_premortem_statistics_button = QtWidgets.QPushButton('Run')

        self._global_effect_groupbox = QtWidgets.QGroupBox('Global effect')

        self._global_effect_tableview = CopyPastableTableView()

        self._pairwise_effect_groupbox = QtWidgets.QGroupBox('Pairwise effect')

        self._selected_group = QtWidgets.QComboBox()
        selected_groups = []
        for i in range(self._groups_model.rowCount()):
            index = self._groups_model.index(i)
            checkstate = self._groups_model.data(index, QtCore.Qt.CheckStateRole)
            group = self._groups_model.data(index, QtCore.Qt.DisplayRole)
            if checkstate == QtCore.Qt.Checked:
                selected_groups.append(group)
        self._selected_group.addItems(selected_groups)

        self._pairwise_effect_tableview = CopyPastableTableView()
        self._pairwise_effect_tableview.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        # self._friedman_figure = Figure()
        # self._friedman_axes = self._friedman_figure.add_subplot(111)
        # self._friedman_canvas = FigureCanvasQTAgg(self._friedman_figure)
        # self._friedman_toolbar = NavigationToolbar2QT(self._friedman_canvas, self)

        # self._dunn_groupbox = QtWidgets.QGroupBox('Pairwise effect')

        # self._selected_group_label = QtWidgets.QLabel('Selected group')

        # self._selected_group_combo = QtWidgets.QComboBox()

        # selected_groups = self._groups_model.selected_groups

        # self._selected_group_combo.addItems(selected_groups)

        # self._dunn_table = CopyPastableTableView()
        # self._dunn_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        # self._dunn_table.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        # self._dunn_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

    def on_compute_premortem_time_effect(self):
        """Event fired when the user click on the 'Run' button.

        It will compute the premortem statistics and update the friedman and dunn widgets accordingly.
        """

        n_target_times = self._n_target_times_spinbox.value()

        self._friedman_p_values, self._dunn_matrices = self._groups_model.evaluate_premortem_time_effect(
            self._selected_property, n_target_times=n_target_times)

        self.update()

    def update(self):
        """Display the global time effect and the pairwise time effect.
        """

        model = PValuesDataModel(self._friedman_p_values, self)
        self._global_effect_tableview.setModel(model)
        for col in range(model.columnCount()):
            self._global_effect_tableview.horizontalHeader().setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)

        self.on_select_group(0)

    def init_ui(self):
        """Initializes the ui.
        """

        self.build_widgets()

        self.build_layout()

        self.build_events()

    def on_select_group(self, index):
        """Event handler called when the user select a different group from the group selection combo box.

        Args:
            index (int): the index of the newly selected time
        """

        selected_group = self._selected_group.currentText()

        model = PValuesDataModel(self._dunn_matrices[selected_group], self)
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
