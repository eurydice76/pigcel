"""This modules implements the following classes:
    _ MainWindow
"""

import collections
import logging
import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets

import pigcel
from pigcel.__pkginfo__ import __version__
from pigcel.gui.models.animals_data_model import AnimalsDataModel
from pigcel.gui.models.workbook_data_model import WorkbookDataModel
from pigcel.gui.views.copy_pastable_tableview import CopyPastableTableView
from pigcel.gui.views.double_clickable_listview import DoubleClickableListView
from pigcel.gui.widgets.logger_widget import QTextEditLogger
from pigcel.gui.widgets.plots_widget import PlotsWidget
from pigcel.kernel.readers.excel_reader import ExcelWorkbookReader
from pigcel.kernel.utils.progress_bar import progress_bar


class MainWindow(QtWidgets.QMainWindow):
    """This class implements the main window of the monitoring application.
    """

    update_property_plot = QtCore.pyqtSignal(tuple)

    update_time_plot = QtCore.pyqtSignal(tuple)

    def __init__(self, parent=None):
        """Constructor.

        Args:
            parent (QtCore.QObject): the parent window
        """

        super(MainWindow, self).__init__(parent)

        self.init_ui()

    def build_events(self):
        """Build the signal/slots.
        """

        self._workbooks_list.double_clicked_empty.connect(self.on_load_monitoring_file)
        self._selected_property_combo.currentTextChanged.connect(self.on_update_property_plot)
        self._selected_property_combo.currentTextChanged.connect(self.on_update_time_plot)
        self._selected_time_combo.currentTextChanged.connect(self.on_update_time_plot)

    def build_layout(self):
        """Build the layout.
        """

        main_layout = QtWidgets.QVBoxLayout()

        hlayout = QtWidgets.QHBoxLayout()

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(self._workbooks_list)

        property_layout = QtWidgets.QHBoxLayout()
        property_layout.addWidget(self._selected_property_label)
        property_layout.addWidget(self._selected_property_combo)
        vlayout.addLayout(property_layout)

        time_layout = QtWidgets.QHBoxLayout()
        time_layout.addWidget(self._selected_time_label)
        time_layout.addWidget(self._selected_time_combo)
        vlayout.addLayout(time_layout)

        hlayout.addLayout(vlayout, stretch=1)

        hlayout.addWidget(self._tabs, stretch=4)

        main_layout.addLayout(hlayout, stretch=4)

        main_layout.addWidget(self._data_table, stretch=2)

        main_layout.addWidget(self._logger.widget, stretch=1)

        self._main_frame.setLayout(main_layout)

    def build_menu(self):
        """Build the menu.
        """

        menubar = self.menuBar()

        file_menu = menubar.addMenu('&File')

        file_action = QtWidgets.QAction('&Open monitoring file', self)
        file_action.setShortcut('Ctrl+O')
        file_action.setStatusTip('Open monitoring (xlsx) file')
        file_action.triggered.connect(self.on_load_monitoring_file)
        file_menu.addAction(file_action)

        file_menu.addSeparator()

        exit_action = QtWidgets.QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit pigcel')
        exit_action.triggered.connect(self.on_quit_application)
        file_menu.addAction(exit_action)

    def build_widgets(self):
        """Build the widgets.
        """

        self._main_frame = QtWidgets.QFrame(self)

        self._workbooks_list = DoubleClickableListView()
        self._workbooks_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self._workbooks_list.setDragEnabled(True)
        workbooks_model = AnimalsDataModel(self)
        self._workbooks_list.setModel(workbooks_model)
        self._workbooks_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self._workbooks_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self._selected_property_label = QtWidgets.QLabel('Property')
        self._selected_property_combo = QtWidgets.QComboBox()

        self._selected_time_label = QtWidgets.QLabel('Time')
        self._selected_time_combo = QtWidgets.QComboBox()
        self._selected_time_combo.addItems(ExcelWorkbookReader.times)

        self._data_table = CopyPastableTableView()
        self._data_table.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self._data_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self._logger = QTextEditLogger(self)
        self._logger.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(self._logger)
        logging.getLogger().setLevel(logging.INFO)

        self._tabs = QtWidgets.QTabWidget()

        self._monitoring_plots_widget = PlotsWidget(self)

        self._tabs.addTab(self._monitoring_plots_widget, 'Plots')

        self.setCentralWidget(self._main_frame)

        self.setGeometry(0, 0, 1200, 1100)

        self.setWindowTitle("monitorpig {}".format(__version__))

        self._progress_label = QtWidgets.QLabel('Progress')
        self._progress_bar = QtWidgets.QProgressBar()
        progress_bar.set_progress_widget(self._progress_bar)
        self.statusBar().showMessage("monitorpig {}".format(__version__))
        self.statusBar().addPermanentWidget(self._progress_label)
        self.statusBar().addPermanentWidget(self._progress_bar)

        icon_path = os.path.join(pigcel.__path__[0], "icons", "pigcel.png")
        self.setWindowIcon(QtGui.QIcon(icon_path))

        self.show()

    def init_ui(self):
        """Initializes the ui.
        """

        self.build_widgets()

        self.build_layout()

        self.build_menu()

        self.build_events()

    def on_load_monitoring_file(self):
        """Event called when the user clicks on 'Load monitoring file' menu button.
        """

        # Pop up a file browser for selecting the workbooks
        xlsx_files = QtWidgets.QFileDialog.getOpenFileNames(self, 'Open data files', '', 'Data Files (*.xls *.xlsx)')[0]
        if not xlsx_files:
            return

        workbooks_model = self._workbooks_list.model()

        n_xlsx_files = len(xlsx_files)
        progress_bar.reset(n_xlsx_files)

        n_loaded_files = 0

        # Loop over the pig directories
        for progress, xlsx_file in enumerate(xlsx_files):

            # Any error at reading must be caught here
            try:
                reader = ExcelWorkbookReader(xlsx_file)
            except Exception as error:
                logging.error(str(error))
                continue
            else:
                workbooks_model.add_workbook(reader)
                n_loaded_files += 1
            finally:
                self._selected_property_combo.clear()
                self._selected_property_combo.addItems(reader.properties)
                progress_bar.update(progress+1)

        # Create a signal/slot connexion for row changed event
        self._workbooks_list.selectionModel().selectionChanged.connect(self.on_select_workbook)

        self._workbooks_list.setCurrentIndex(workbooks_model.index(0, 0))

        logging.info('Loaded successfully {} files out of {}'.format(n_loaded_files, n_xlsx_files))

    def on_quit_application(self):
        """Event handler when the application is exited.
        """

        choice = QtWidgets.QMessageBox.question(self, 'Quit', "Do you really want to quit?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            sys.exit()

    def on_update_property_plot(self, selected_property=None):
        """
        """

        selected_property = self._selected_property_combo.currentText()
        if not selected_property:
            return

        selected_indexes = self._workbooks_list.selectionModel().selectedIndexes()
        if not selected_indexes:
            return

        workbooks_model = self._workbooks_list.model()

        selected_workbooks = [workbooks_model.data(index, AnimalsDataModel.Workbook) for index in selected_indexes]

        selected_data = []
        for wb in selected_workbooks:
            wb_data = wb.get_data(selected_property=selected_property)
            selected_data.append((wb.basename, wb_data[selected_property]))

        selected_data = (selected_property, selected_data)
        self.update_property_plot.emit(selected_data)

    def on_update_time_plot(self, selected_time=None):
        """
        """

        selected_property = self._selected_property_combo.currentText()
        if not selected_property:
            return

        selected_time = self._selected_time_combo.currentText()
        if not selected_time:
            return

        selected_indexes = self._workbooks_list.selectionModel().selectedIndexes()
        if not selected_indexes:
            return

        workbooks_model = self._workbooks_list.model()

        selected_workbooks = [workbooks_model.data(index, AnimalsDataModel.Workbook) for index in selected_indexes]

        selected_data = []
        for wb in selected_workbooks:
            wb_data = wb.get_data(selected_property=selected_property, selected_time=selected_time)
            selected_data.append((wb.basename, wb_data[selected_property]))
        selected_data = (selected_property, selected_time, selected_data)

        self.update_time_plot.emit(selected_data)

    def on_select_workbook(self, index):
        """Event fired when a workbook is selected.

        Args:
            index (PyQt5.QtCore.QModelIndex): the index of the workbook in the corresponding list view
        """

        selected_indexes = index.indexes()

        if not selected_indexes:
            return

        data = self._workbooks_list.model().data(selected_indexes[0], AnimalsDataModel.Workbook).get_data()

        workbook_data_model = WorkbookDataModel(data)

        self._data_table.setModel(workbook_data_model)

        self.on_update_property_plot()

        self.on_update_time_plot()
