import collections
import logging

from PyQt5 import QtCore


class AnimalsGroupsModel(QtCore.QAbstractListModel):
    """This model describes groups of pigs.
    """

    def __init__(self, parent):
        """Constructor.

        Args:
            parent (PyQt5.QtWidgets.QObject): the parent object
        """

        super(AnimalsGroupsModel, self).__init__(parent)

        self._groups = collections.OrderedDict()

    def data(self, index, role):
        """Return the data for a given index and a given role

        Args:
            index (QtCore.QModelIndex): the index
            role (int): the role

        Returns:
            QtCore.QVariant: the data
        """

        if not index.isValid():
            return QtCore.QVariant()

        row = index.row()

        group_names = list(self._groups.keys())

        group = group_names[row]

        if role == QtCore.Qt.DisplayRole:
            return group
        elif role == QtCore.Qt.CheckStateRole:
            return QtCore.Qt.Checked if self._groups[group][1] else QtCore.Qt.Unchecked
        else:
            return QtCore.QVariant()

    def flags(self, index):
        """Return the flag for specified item.

        Returns:
            int: the flag
        """

        default_flags = super(AnimalsGroupsModel, self).flags(index)

        return QtCore.Qt.ItemIsUserCheckable | default_flags

    def setData(self, index, value, role):
        """Set the data for a given index and given role.

        Args:
            value (QtCore.QVariant): the data
        """

        if not index.isValid():
            return QtCore.QVariant()

        row = index.row()

        group_names = list(self._groups.keys())

        group = group_names[row]

        if role == QtCore.Qt.CheckStateRole:
            self._groups[group][1] = True if value == QtCore.Qt.Checked else False
            return True

        return super(AnimalsGroupsModel, self).setData(index, value, role)

    def rowCount(self, parent=None):
        """Returns the number of row of the model.

        Returns:
            int: the number of rows
        """

        return len(self._groups)

    def add_monitoring_pool_model(self, name, model):
        """Add a new monitoring pool model to this model.

        Args:
            name (str): the name of the model to add
            model (pigcel.gui.models.monitoring_pool_model.MonitoringPoolModel): the model
        """

        if name in self._groups:
            return

        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())

        self._groups[name] = (model, True)

        self.endInsertRows()
