
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

    def flags(self, index):
        if index.isValid():
            return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsEnabled

    def get_workbook(self, filename):
        """Retrieve the workbook with a given filename.

        Args:
            filename (str): the workbook's filename

        Returns:
            openpyxl.workbook.workbook.Workbook: the workbook
        """

        for wb in self._workbooks:
            if wb.filename == filename:
                return wb

        return None

    def remove_workbook(self, workbook):
        """Remove a workbook from the model.

        Args:
            workbook (openpyxl.workbook.workbook.Workbook): the workbook
        """

        if workbook not in self._workbooks:
            return

        index = self._workbooks.index(workbook)

        self.beginRemoveRows(QtCore.QModelIndex(), index, index)

        self._workbooks.remove(workbook)

        self.endRemoveRows()

    def rowCount(self, parent=QtCore.QModelIndex()):
        """Returns the number of rows.

        Returns:
            int: the number of rows
        """

        return len(self._workbooks)
