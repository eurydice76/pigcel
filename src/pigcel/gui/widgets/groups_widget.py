import logging

from PyQt5 import QtGui, QtWidgets

from pigcel.gui.models.animals_groups_model import AnimalsGroupsModel
from pigcel.gui.views.animals_pool_listview import AnimalsPoolListView


class GroupsWidget(QtWidgets.QWidget):
    """This class implements the widget that will store all the statistics related widgets.
    """

    def __init__(self, animals_model, main_window):
        """Constructor.

        Args:
            pigs_model (pigcel.gui.models.pigs_data_model.PigsDataModel): the underlying model for the registered pigs
            main_window (PyQt5.QtWidgets.QMainWindow): the main window
        """
        super(GroupsWidget, self).__init__(main_window)

        self._main_window = main_window

        self._animals_model = animals_model

        self.init_ui()

    def build_events(self):
        """Build the signal/slots
        """

    def build_layout(self):
        """Build the layout.
        """

        main_layout = QtWidgets.QVBoxLayout()

        hlayout = QtWidgets.QHBoxLayout()

        hlayout.addWidget(self._groups_list)
        hlayout.addWidget(self._individuals_list)
        self._groups_groupbox.setLayout(hlayout)

        hlayout.addWidget(self._groups_groupbox)

        main_layout.addLayout(hlayout)

        self.setLayout(main_layout)

    def build_widgets(self):
        """Build the widgets.
        """

        self._groups_list = QtWidgets.QListView(self)
        self._groups_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._groups_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        groups_model = AnimalsGroupsModel(self)
        self._groups_list.setModel(groups_model)

        self._animals_list = AnimalsPoolListView(self)
        self._animals_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._animals_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self._groups_groupbox = QtWidgets.QGroupBox('Groups')

    def init_ui(self):
        """Initializes the ui
        """

        self.build_widgets()

        self.build_layout()

        self.build_events()

    def on_add_group(self, group):
        """Event fired when a new group is added to the group list.
        """

        groups_model = self._groups_list.model()
        groups_model.add_group(group)
        last_index = groups_model.index(groups_model.rowCount()-1, 0)
        self._groups_list.setCurrentIndex(last_index)

    def on_select_group(self, index):
        """Updates the individuals list view.

        Args:
            index (PyQt5.QtCore.QModelIndex): the group index
        """

        groups_model = self._groups_list.model()

        current_pig_pool = groups_model.data(index, groups_model.PigsPool)

        pigs_pool_model = PigsPoolModel(self, current_pig_pool)

        self._individuals_list.setModel(pigs_pool_model)
