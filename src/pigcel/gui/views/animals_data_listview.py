"""This module implements the following classes:
    - AnimalsDataListView
"""

from PyQt5 import QtCore, QtGui, QtWidgets

from pigcel.gui.models.animals_data_model import AnimalsDataModel
from pigcel.gui.views.double_clickable_listview import DoubleClickableListView


class AnimalsDataListView(DoubleClickableListView):
    """This class implments the listview used to drop in animal names.
    """

    def keyPressEvent(self, event):
        """Event handler for keyboard interaction.

        Args:
            event (PyQt5.QtGui.QKeyEvent): the keyboard event
        """

        if event.key() == QtCore.Qt.Key_Delete:

            animals_data_model = self.model()
            if animals_data_model is None:
                return

            for sel_index in reversed(self.selectedIndexes()):
                animals_data_model.remove_workbook(sel_index.data(AnimalsDataModel.Workbook))
                if animals_data_model.rowCount() > 0:
                    index = animals_data_model.index(animals_data_model.rowCount()-1)
                    self.setCurrentIndex(index)

        else:
            super(AnimalsDataListView, self).keyPressEvent(event)
