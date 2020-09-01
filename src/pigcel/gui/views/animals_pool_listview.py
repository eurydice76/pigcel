"""This module implements the following classes:
    - AnimalsPoolListView
"""

from PyQt5 import QtCore, QtGui, QtWidgets

from pigcel.gui.views.droppable_listview import DroppableListView


class AnimalsPoolListView(DroppableListView):
    """This class implments the listview used to drop in animal names.
    """

    def dropEvent(self, event):
        """Event triggered when the dragged item is dropped into this widget.

        Args:
            event (PyQt5.QtGui.QDropEvent): the drop event
        """

        # Copy the mime data into a source model to get their underlying value
        source_model = QtGui.QStandardItemModel()
        source_model.dropMimeData(event.mimeData(), QtCore.Qt.CopyAction, 0, 0, QtCore.QModelIndex())

        target_model = self.model()
        if target_model is None:
            return

        # Drop only those items which are not present in this widget
        current_items = [target_model.data(target_model.index(i), QtCore.Qt.DisplayRole) for i in range(target_model.rowCount())]
        dragged_items = [source_model.item(i, 0).text() for i in range(source_model.rowCount())]
        for name in dragged_items:
            if name in current_items:
                continue

            target_model.add_animal(name)

    def keyPressEvent(self, event):
        """Event handler for keyboard interaction.

        Args:
            event (PyQt5.QtGui.QKeyEvent): the keyboard event
        """

        if event.key() == QtCore.Qt.Key_Delete:

            animals_pool_model = self.model()
            if animals_pool_model is None:
                return

            for sel_index in reversed(self.selectedIndexes()):
                animals_pool_model.remove_animal(sel_index.data(QtCore.Qt.DisplayRole))
                if animals_pool_model.rowCount() > 0:
                    index = animals_pool_model.index(animals_pool_model.rowCount()-1)
                    self.setCurrentIndex(index)

        else:
            super(AnimalsPoolListView, self).keyPressEvent(event)
