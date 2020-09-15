
"""This module implements the following classes:
    - ValidTimesModel
"""

import collections
import logging
import os

from PyQt5 import QtCore, QtGui


class ValidTimesModel(QtCore.QAbstractListModel):
    """This class implemenents a model for storing anials that belong to the same pool for further statistical analysis.
    """

    def __init__(self, times, *args, **kwargs):

        super(ValidTimesModel, self).__init__(*args, **kwargs)

        self._times = times

    def data(self, index, role):
        """Get the data at a given index for a given role.

        Args:
            index (QtCore.QModelIndex): the index
            role (int): the role

        Returns:
            QtCore.QVariant: the data
        """

        if not self._times:
            return QtCore.QVariant()

        if not index.isValid():
            return QtCore.QVariant()

        row = index.row()

        time = self._times[row]

        if role == QtCore.Qt.DisplayRole:

            return time[0]

        elif role == QtCore.Qt.ForegroundRole:

            return QtGui.QColor('black') if time[1] else QtGui.QColor('red')

        return QtCore.QVariant()

    def rowCount(self, parent=QtCore.QModelIndex()):
        """Returns the number of rows.

        Returns:
            int: the number of rows
        """

        return len(self._times)
