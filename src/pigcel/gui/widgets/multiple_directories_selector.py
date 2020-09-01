"""This module implements the following classes and functions:
    - MultipleDirectoriesSelector
"""

from PyQt5 import QtWidgets


class MultipleDirectoriesSelector(QtWidgets.QFileDialog):
    """This class implements a widget that mimics a file selector but for selecting several directories.
    """

    def __init__(self, *args):

        super(MultipleDirectoriesSelector, self).__init__(*args)

        self.setOption(self.DontUseNativeDialog, True)
        self.setFileMode(self.DirectoryOnly)

        self.tree = self.findChild(QtWidgets.QTreeView)
        self.tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.list = self.findChild(QtWidgets.QListView)
        self.list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
