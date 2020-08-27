
"""This module implements the following classes:
    - MonitoringDataModel
"""

from PyQt5 import QtCore

from pigcel.gui.models.animals_data_model import AnimalsDataModel


class AnimalsPoolModel(QtCore.QAbstractListModel):
    """This class implemenents a model for storing anials that belong to the same pool for further statistical analysis.
    """

    Workbook = QtCore.Qt.UserRole + 1

    def __init__(self, monitoring_data_model, *args, **kwargs):

        super(AnimalsPoolModel, self).__init__(*args, **kwargs)

        self._monitoring_data_model = monitoring_data_model

        self._animals = []

    def add_animal(self, animal):
        """Add a new animal to the pool.

        Args:
            animal (str): the animal
        """

        # Only new animals can be added
        if animal in self._animals:
            return

        # The animal must have been loaded before
        for i in range(self._monitoring_data_model.rowCount()):
            index = self._monitoring_data_model.index(i)
            text = self._monitoring_data_model.data(index, QtCore.Qt.DisplayRole)
            if text == animal:
                break
        else:
            return

        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())

        self._animals.append(animal)

        self.endInsertRows()

    def data(self, index, role):
        """Get the data at a given index for a given role.

        Args:
            index (QtCore.QModelIndex): the index
            role (int): the role

        Returns:
            QtCore.QVariant: the data
        """

        if not self._indexes:
            return QtCore.QVariant()

        if not index.isValid():
            return QtCore.QVariant()

        row = index.row()

        animal = self._animals[row]

        if role == QtCore.Qt.DisplayRole:

            return animal

        elif role == AnimalsPoolModel.Workbook:

            for i in range(self._monitoring_data_model.rowCount()):
                index = self._monitoring_data_model.index(i)
                text = self._monitoring_data_model.data(index, QtCore.Qt.DisplayRole)
                if text == animal:
                    return self._monitoring_data_model.data(index, AnimalsDataModel.Workbook)

        return QtCore.QVariant()

    def rowCount(self, parent=QtCore.QModelIndex()):
        """Returns the number of rows.

        Returns:
            int: the number of rows
        """

        return len(self._animals)
