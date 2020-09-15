"""This module implements the following classes:
    - WorkbookDataModel
"""

from PyQt5 import QtCore, QtGui

import numpy as np


class WorkbookDataModel(QtCore.QAbstractTableModel):
    """This class implements a model for storing the data of a monitoring workbook. 
    """

    def __init__(self, dataframe):
        """Constructor.

        Args:
            dataframe (pandas.DataFrame): the data
        """

        super(WorkbookDataModel, self).__init__()
        self._dataframe = dataframe

    def rowCount(self, parent=None):
        """Return the number of rows of the model.

        Returns:
            int: the number of rows
        """

        return len(self._dataframe.index)

    def columnCount(self, parent=None):
        """Return the number of columns of the model.

        Returns:
            int: the number of columns
        """

        return len(self._dataframe.columns)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """Return the data for a given index and for a given role.

        Args:
            index (QtCore.QModelIndex): the index
            role (int): the role

        Returns:
            QtCore.Qvariant: the data
        """

        if not index.isValid():
            return QtCore.QVariant()

        value = self._dataframe.iloc[index.row(), index.column()]

        if role == QtCore.Qt.DisplayRole:
            return str(value)
        elif role == QtCore.Qt.BackgroundRole:
            return QtGui.QColor('red') if np.isnan(value) else QtGui.QColor('white')
        else:
            return QtCore.QVariant()

    def headerData(self, index, orientation, role):
        """Returns the header data for a given index, role and orientation

        Args:
            index (QtCore.QModelIndex): the index
            orientation (int): the orientation
            role (int): the role

        Returns:
            QtCore.QVariant: the data
        """

        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                properties = self._dataframe.columns
                return properties[index]
            else:
                times = self._dataframe.index
                return times[index]
