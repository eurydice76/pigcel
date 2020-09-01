"""This module implements the following classes and functions:
    - DroppableListView
"""

import abc

from PyQt5 import QtCore, QtGui, QtWidgets


class DroppableListView(QtWidgets.QListView):
    """This class implements an interface for listviews onto which data can be dropped in.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, pigs_model, *args, **kwargs):
        super(DroppableListView, self).__init__(*args, **kwargs)

        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

    def dragMoveEvent(self, event):
        """Event triggered when the dragged item is moved above the target widget.
        """

        event.accept()

    def dragEnterEvent(self, event):
        """Event triggered when the dragged item enter into this widget.
        """

        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            event.accept()
        else:
            event.ignore()

    @abc.abstractmethod
    def dropEvent(self, event):
        """Event triggered when the dragged item is dropped into this widget.
        """
