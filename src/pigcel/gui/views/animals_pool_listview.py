"""
"""

from PyQt5 import QtCore, QtGui, QtWidgets

from pigcel.gui.views.droppable_listview import DroppableListView


class AnimalsPoolListView(DroppableListView):

    def dropEvent(self, event):
        """Event triggered when the dragged item is dropped into this widget.
        """

        # Copy the mime data into a source model to get their underlying value
        source_model = QtGui.QStandardItemModel()
        source_model.dropMimeData(event.mimeData(), QtCore.Qt.CopyAction, 0, 0, QtCore.QModelIndex())

        # Drop only those items which are not present in this widget
        current_items = [self.model().data(self.model().index(i), QtCore.Qt.DisplayRole) for i in range(self.model().rowCount())]
        dragged_items = [source_model.item(i, 0).text() for i in range(source_model.rowCount())]
        for name in dragged_items:
            if name in current_items:
                continue

            self.model().add_animal(name)
