"""This module implements the following classes:
    - GroupsWidget
"""


import logging
import os

from PyQt5 import QtCore, QtGui, QtWidgets

from pigcel.gui.dialogs.group_averages_dialog import GroupAveragesDialog
from pigcel.gui.dialogs.group_effect_dialog import GroupEffectDialog
from pigcel.gui.dialogs.group_medians_dialog import GroupMediansDialog
from pigcel.gui.dialogs.time_effect_dialog import TimeEffectDialog
from pigcel.gui.models.animals_pool_model import AnimalsPoolModel
from pigcel.gui.models.animals_groups_model import AnimalsGroupsModel
from pigcel.gui.views.animals_groups_listview import AnimalsGroupsListView
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

        self._groups_list.double_clicked_empty.connect(self._main_window.on_add_new_group)
        self._groups_list.selectionModel().currentChanged.connect(self.on_select_group)
        self._main_window.add_new_group.connect(self.on_add_group)
        self._main_window.display_group_averages.connect(self.on_display_group_averages)
        self._main_window.display_group_effect_statistics.connect(self.on_display_group_effect_statistics)
        self._main_window.display_group_medians.connect(self.on_display_group_medians)
        self._main_window.display_time_effect_statistics.connect(self.on_display_time_effect_statistics)
        self._main_window.export_group_statistics.connect(self.on_export_group_statistics)
        self._main_window.import_groups_from_directories.connect(self.on_import_groups)

    def build_layout(self):
        """Build the layout.
        """

        main_layout = QtWidgets.QVBoxLayout()

        hlayout = QtWidgets.QHBoxLayout()

        groupbox_layout = QtWidgets.QHBoxLayout()
        groupbox_layout.addWidget(self._groups_list)
        groupbox_layout.addWidget(self._animals_list)
        self._groups_groupbox.setLayout(groupbox_layout)

        hlayout.addWidget(self._groups_groupbox)

        main_layout.addLayout(hlayout)

        self.setLayout(main_layout)

    def build_widgets(self):
        """Build the widgets.
        """

        self._groups_list = AnimalsGroupsListView(self)
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

    def model(self):
        """Returns the groups model underlying this widget.
        """

        return self._groups_list.model()

    def on_add_group(self, group):
        """Event fired when a new group is added to the group list.
        """

        groups_model = self._groups_list.model()
        animals_model = AnimalsPoolModel(self._animals_model)
        groups_model.add_model(group, animals_model)
        last_index = groups_model.index(groups_model.rowCount()-1, 0)
        self._groups_list.setCurrentIndex(last_index)

    def on_display_group_averages(self):
        """Display the group averages.
        """

        # No animals loaded, return
        n_animals = self._animals_model.rowCount()
        if n_animals == 0:
            logging.warning('No animal loaded yet')
            return

        # No group defined, return
        groups_model = self._groups_list.model()
        if groups_model.rowCount() == 0:
            logging.warning('No group defined yet')
            return

        selected_property = self._main_window.selected_property

        reduced_data_per_group = groups_model.get_reduced_data_per_group(selected_property, selected_statistics=['mean', 'std'])
        if not reduced_data_per_group:
            return

        dialog = GroupAveragesDialog(self._main_window.selected_property, reduced_data_per_group, self)
        dialog.show()

    def on_display_group_effect_statistics(self):
        """Display the group effect statistics.
        """

        # No animals loaded, return
        n_animals = self._animals_model.rowCount()
        if n_animals == 0:
            logging.warning('No animal loaded yet')
            return

        # No group defined, return
        groups_model = self._groups_list.model()
        if groups_model.rowCount() == 0:
            logging.warning('No group defined yet')
            return

        selected_property = self._main_window.selected_property

        data_per_group = groups_model.get_data_per_group(selected_property)
        if not data_per_group:
            logging.warning('No group selected')
            return

        global_effect = groups_model.evaluate_global_group_effect(selected_property)
        if global_effect is None:
            return

        pairwise_effect = groups_model.evaluate_pairwise_group_effect(selected_property)

        dialog = GroupEffectDialog(selected_property, global_effect, pairwise_effect, self)
        dialog.show()

    def on_display_group_medians(self):
        """Display the group medians.
        """

        # No animals loaded, return
        n_animals = self._animals_model.rowCount()
        if n_animals == 0:
            logging.warning('No animal loaded yet')
            return

        # No group defined, return
        groups_model = self._groups_list.model()
        if groups_model.rowCount() == 0:
            logging.warning('No group defined yet')
            return

        selected_property = self._main_window.selected_property

        data_per_group = groups_model.get_data_per_group(selected_property)
        if not data_per_group:
            logging.warning('No group selected')
            return

        dialog = GroupMediansDialog(self._main_window.selected_property, data_per_group, self)
        dialog.show()

    def on_display_time_effect_statistics(self):
        """Display the group effect statistics.
        """

        # No animals loaded, return
        n_animals = self._animals_model.rowCount()
        if n_animals == 0:
            logging.warning('No animal loaded yet')
            return

        # No group defined, return
        groups_model = self._groups_list.model()
        if groups_model.rowCount() == 0:
            logging.warning('No group defined yet')
            return

        selected_property = self._main_window.selected_property

        times_per_group, global_effect = groups_model.evaluate_global_time_effect(selected_property)

        pairwise_effect = groups_model.evaluate_pairwise_time_effect(selected_property)

        dialog = TimeEffectDialog(selected_property, global_effect, pairwise_effect, times_per_group, self)
        dialog.show()

    def on_export_group_statistics(self, selected_property, filename):
        """Event fired when the user clicks on the 'Export statistics' menu button.
        """

        # No animals loaded, return
        n_animals = self._animals_model.rowCount()
        if n_animals == 0:
            logging.warning('No animal loaded yet')
            return

        # No group defined, return
        groups_model = self._groups_list.model()
        if groups_model.rowCount() == 0:
            logging.warning('No group defined yet')
            return

        groups_model.export_statistics(filename, selected_property=selected_property)

    def on_import_groups(self, groups):
        """Event fired when the user click on Groups -> Import from directories menu button.

        Args:
            groups (collections.OrderedDict): the imported groups
        """

        for group, files in groups.items():
            self.on_add_group(group)
            for filename in files:
                animals_pool_model = self._groups_list.model().get_animals_pool_model(group)
                if animals_pool_model is not None:
                    animals_pool_model.add_animal(filename)

    def on_select_group(self, index):
        """Updates the individuals list view.

        Args:
            index (PyQt5.QtCore.QModelIndex): the group index
        """

        groups_model = self._groups_list.model()

        animals_pool_model = groups_model.data(index, groups_model.AnimalsPoolModel)
        if animals_pool_model == QtCore.QVariant():
            return

        self._animals_list.setModel(animals_pool_model)
