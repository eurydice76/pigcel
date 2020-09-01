"""This module implements the following classes:
    - AnimalsGroupsListView
"""

from PyQt5 import QtCore, QtGui, QtWidgets

from pigcel.gui.models.animals_groups_model import AnimalsGroupsModel
from pigcel.gui.views.double_clickable_listview import DoubleClickableListView


class AnimalsGroupsListView(DoubleClickableListView):
    """This class implments the listview used to drop in animal names.
    """

    def keyPressEvent(self, event):
        """Event handler for keyboard interaction.

        Args:
            event (PyQt5.QtGui.QKeyEvent): the keyboard event
        """

        if event.key() == QtCore.Qt.Key_Delete:

            animals_groups_model = self.model()
            if animals_groups_model is None:
                return

            for sel_index in reversed(self.selectedIndexes()):
                animals_groups_model.remove_animals_pool_model(sel_index.data(AnimalsGroupsModel.AnimalsPoolModel))
                if animals_groups_model.rowCount() > 0:
                    index = animals_groups_model.index(animals_groups_model.rowCount()-1)
                    self.setCurrentIndex(index)

        else:
            super(AnimalsGroupsListView, self).keyPressEvent(event)
