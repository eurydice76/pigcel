
"""This module implements the following classes:
    - MonitoringDataModel
"""

import collections

from PyQt5 import QtCore

import pandas as pd

from pigcel.kernel.readers.excel_reader import UnknownPropertyError
from pigcel.kernel.utils.stats import statistical_functions
from pigcel.gui.models.animals_data_model import AnimalsDataModel


class InvalidPoolData(Exception):
    """This class implements an exception which is raised when the data stored in the pool is invalid.
    """


class AnimalsPoolModel(QtCore.QAbstractListModel):
    """This class implemenents a model for storing anials that belong to the same pool for further statistical analysis.
    """

    Workbook = QtCore.Qt.UserRole + 1

    def __init__(self, animals_data_model, *args, **kwargs):

        super(AnimalsPoolModel, self).__init__(*args, **kwargs)

        self._animals_data_model = animals_data_model

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
        for i in range(self._animals_data_model.rowCount()):
            index = self._animals_data_model.index(i)
            text = self._animals_data_model.data(index, QtCore.Qt.DisplayRole)
            if text == animal:
                break
        else:
            return

        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())

        self._animals.append(animal)

        self.endInsertRows()

    @property
    def animals(self):
        """Returns the animals in the pool.

        Returns:
            list of str: the animals of the pool
        """

        return self._animals

    def data(self, index, role):
        """Get the data at a given index for a given role.

        Args:
            index (QtCore.QModelIndex): the index
            role (int): the role

        Returns:
            QtCore.QVariant: the data
        """

        if not self._animals:
            return QtCore.QVariant()

        if not index.isValid():
            return QtCore.QVariant()

        row = index.row()

        animal = self._animals[row]

        if role == QtCore.Qt.DisplayRole:

            return animal

        elif role == AnimalsPoolModel.Workbook:

            for i in range(self._animals_data_model.rowCount()):
                index = self._animals_data_model.index(i)
                text = self._animals_data_model.data(index, QtCore.Qt.DisplayRole)
                if text == animal:
                    return self._animals_data_model.data(index, AnimalsDataModel.Workbook)

        return QtCore.QVariant()

    def get_pool_data(self, selected_property):
        """Get the data stored in the pool for a given property.

        Args:
            selected_property (str): the property

        Returns:
            pandas.DataFrame: the pool data
        """

        data = pd.DataFrame()
        valid_animals = []
        for animal in self._animals:
            wb = self._animals_data_model.get_workbook(animal)
            if wb is None:
                continue

            try:
                property_slice = wb.get_property_slice(selected_property)
            except UnknownPropertyError:
                continue
            else:
                valid_animals.append(animal)
                data = pd.concat([data, property_slice], axis=1)

        if not valid_animals:
            raise InvalidPoolData('No valid animal was found for this pool')

        data.columns = valid_animals

        return data

    def get_reduced_data(self, selected_property, selected_statistics=None):
        """Reduced the pool data for a given property according a set of given statistics.

        Args:
            selected_property (str): the property
            selected_statistics (list): the statistics

        Returns:
            pandas.Series: the reduced data
        """

        if selected_statistics is None:
            selected_statistics = list(statistical_functions.keys())
        else:
            available_statistics_functions = set(statistical_functions.keys())
            selected_statistics = list(available_statistics_functions.intersection(selected_statistics))

        if not selected_statistics:
            raise InvalidPoolData('Invalid statistics for reducing the pool data')

        pool_data = self.get_pool_data(selected_property)

        reduced_pool_data = collections.OrderedDict()
        for func in selected_statistics:
            reduced_pool_data[func] = pd.Series(statistical_functions[func](pool_data.to_numpy(), axis=1), index=pool_data.index)

        return reduced_pool_data

    def remove_animal(self, animal):
        """Remove an animal from the model.

        Args:
            animal (str): the name of the animal
        """

        if animal not in self._animals:
            return

        index = self._animals.index(animal)

        self.beginRemoveRows(QtCore.QModelIndex(), index, index)

        self._animals.remove(animal)

        self.endRemoveRows()

    def rowCount(self, parent=QtCore.QModelIndex()):
        """Returns the number of rows.

        Returns:
            int: the number of rows
        """

        return len(self._animals)
