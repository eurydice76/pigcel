
"""This module implements the following classes:
    - AnimalsDataModel
"""

from PyQt5 import QtCore


class AnimalsDataModel(QtCore.QAbstractListModel):
    """This class implemenents a model for storing a list of monitoring workbooks.
    """

    Workbook = QtCore.Qt.UserRole + 1

    def __init__(self, *args, **kwargs):

        super(AnimalsDataModel, self).__init__(*args, **kwargs)

        self._workbooks = []

    def add_workbook(self, workbook):
        """Add a workbook to the model.

        Args:
            workbook (openpyxl.workbook.workbook.Workbook): the workbook to add
        """

        filenames = [wb.filename for wb in self._workbooks]
        if workbook.filename in filenames:
            return

        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())

        self._workbooks.append(workbook)

        self.endInsertRows()

    def data(self, index, role):
        """Get the data at a given index for a given role.

        Args:
            index (QtCore.QModelIndex): the index
            role (int): the role

        Returns:
            QtCore.QVariant: the data
        """

        if not self._workbooks:
            return QtCore.QVariant()

        if not index.isValid():
            return QtCore.QVariant()

        row = index.row()
        workbook = self._workbooks[row]

        if role == QtCore.Qt.DisplayRole:

            return workbook.filename

        elif role == QtCore.Qt.ToolTipRole:

            return workbook.information

        elif role == AnimalsDataModel.Workbook:

            return workbook

        else:

            return QtCore.QVariant()

    def rowCount(self, parent=QtCore.QModelIndex()):
        """Returns the number of rows.

        Returns:
            int: the number of rows
        """

        return len(self._workbooks)
