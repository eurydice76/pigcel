"""This module implements the following classes and functions:
    - EnhancedTextEdit
    - QTextEditLogger
"""

import logging

from PyQt5 import QtCore, QtWidgets


class EnhancedTextEdit(QtWidgets.QPlainTextEdit):
    """This class implements a text edit bound to a contexttual menu.
    """

    def contextMenuEvent(self, event):
        popup_menu = self.createStandardContextMenu()

        popup_menu.addSeparator()
        popup_menu.addAction('Clear', self.on_clear_logger)
        popup_menu.addSeparator()
        popup_menu.addAction('Save as ...', self.on_save_logger)
        popup_menu.exec_(event.globalPos())

    def on_clear_logger(self):
        """Clear the logger
        """

        self.clear()

    def on_save_logger(self):
        """Save the logger contents to a file
        """

        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')
        if not filename:
            return

        with open(filename, 'w') as fin:
            fin.write(self.toPlainText())


class QTextEditLogger(logging.Handler):
    """This class implements a QTextEdit based handler for the application's logger.

    Every logging call will be written in the QTextEdit. The logbook can be saved to a text file or cleared.
    """

    def __init__(self, parent):

        super().__init__()
        self._widget = EnhancedTextEdit(parent)
        self._widget.setReadOnly(True)

    def emit(self, record):
        """
        """

        msg = self.format(record)
        self._widget.appendPlainText(msg)
        self._widget.repaint()

    @property
    def widget(self):
        """Return the underlying widget used for displaying the log.
        """

        return self._widget
