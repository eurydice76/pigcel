import collections
import logging

from PyQt5 import QtCore

import openpyxl

from pigcel.kernel.utils.stats import statistical_functions
from pigcel.gui.models.animals_pool_model import InvalidPoolData


class AnimalsGroupsModel(QtCore.QAbstractListModel):
    """This model describes groups of pigs.
    """

    AnimalsPoolModel = QtCore.Qt.UserRole + 1

    def __init__(self, parent):
        """Constructor.

        Args:
            parent (PyQt5.QtWidgets.QObject): the parent object
        """

        super(AnimalsGroupsModel, self).__init__(parent)

        self._groups = collections.OrderedDict()

    def add_model(self, name, model):
        """Add a new monitoring pool model to this model.

        Args:
            name (str): the name of the model to add
            model (pigcel.gui.models.animals_pool_model.AnimalsPoolModel): the model
        """

        if name in self._groups:
            return

        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())

        self._groups[name] = [model, True]

        self.endInsertRows()

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
        elif role == AnimalsGroupsModel.AnimalsPoolModel:
            return self._groups[group][0]
        else:
            return QtCore.QVariant()

    def export_statistics(self, filename, selected_property='APs', selected_groups=None, interval_indexes=None):
        """Export basic statistics (average, median, std, quartile ...) for each group and interval to an excel file.

        Args:
            filename (str): the output excel filename
            selected_property (str): the selected property
            selected_groups (list of str): the selected group. if None all the groups of the model will be used.
        """

        if selected_groups is None:
            selected_groups = list(self._groups.keys())
        else:
            all_groups = set(self._groups.keys())
            selected_groups = list(all_groups.intersection(selected_groups))

        workbook = openpyxl.Workbook()
        # Remove the first empty sheet created by default
        workbook.remove_sheet(workbook.get_sheet_by_name('Sheet'))

        for group in self._groups:
            animals_pool_model, selected = self._groups[group]
            if not selected:
                continue

            try:
                reduced_data = animals_pool_model.get_reduced_data(selected_property)
            except InvalidPoolData:
                logging.error('Could not get reduced pool data for group {}. Skip it.'.format(group))
                continue

            # Create the excel worksheet
            workbook.create_sheet(group)
            worksheet = workbook.get_sheet_by_name(group)

            worksheet.cell(row=1, column=1).value = 'time'
            worksheet.cell(row=1, column=12).value = 'selected property'
            worksheet.cell(row=2, column=12).value = selected_property
            worksheet.cell(row=1, column=14).value = 'animals'

            # Add titles
            for col, func in enumerate(statistical_functions.keys()):
                worksheet.cell(row=1, column=col+2).value = func

                values = reduced_data[func]
                for row, value in enumerate(values):
                    worksheet.cell(row=row+2, column=1).value = values.index[row]
                    worksheet.cell(row=row+2, column=col+2).value = value

            animals = self._groups[group][0].animals
            for row, animal in enumerate(animals):
                worksheet.cell(row=row+2, column=14).value = animal

        try:
            workbook.save(filename)
        except PermissionError as error:
            logging.error(str(error))
            return

        logging.info('Exported successfully groups statistics in {} file'.format(filename))

    def flags(self, index):
        """Return the flag for specified item.

        Returns:
            int: the flag
        """

        default_flags = super(AnimalsGroupsModel, self).flags(index)

        return QtCore.Qt.ItemIsUserCheckable | default_flags

    def get_animals_pool_model(self, name):
        """Get the animals pool model with a given name.

        Args:
            name (str): the model name

        Returns:
            pigcell.gui.models.animals_pool_model.AnimalsPoolModel: the animals pool model
        """

        if name in self._groups:
            return self._groups[name][0]
        else:
            return None

    def get_data_per_group(self, selected_property):
        """Reduced the pool data for each group for a given property according a given statistics.

        Args:
            selected_property (str): the property
            selected_statistics (str): the statistics

        Returns:
            collections.OrderedDict: the reduced data per group
        """

        data_per_group = collections.OrderedDict()

        groups = list(self._groups.keys())

        for group in groups:
            animals_pool_model, selected = self._groups[group]
            # If the group is selected, compute the reduced stastitics
            if selected:
                data = animals_pool_model.get_pool_data(selected_property)
                data_per_group[group] = data

        return data_per_group

    def get_reduced_data_per_group(self, selected_property, selected_statistics=None):
        """Reduced the pool data for each group for a given property according a given statistics.

        Args:
            selected_property (str): the property
            selected_statistics (str): the statistics

        Returns:
            collections.OrderedDict: the reduced data per group
        """

        reduced_data_per_group = collections.OrderedDict()

        groups = list(self._groups.keys())

        for group in groups:
            animals_pool_model, selected = self._groups[group]
            # If the group is selected, compute the reduced stastitics
            if selected:
                reduced_data = animals_pool_model.get_reduced_data(selected_property, selected_statistics)
                reduced_data_per_group[group] = reduced_data

        return reduced_data_per_group

    def remove_animals_pool_model(self, model):
        """
        """

        for i, v in enumerate(self._groups.items()):
            name, current_model = v
            if current_model[0] == model:
                self.beginRemoveRows(QtCore.QModelIndex(), i, i)
                del self._groups[name]
                self.endRemoveRows()
                break

    def rowCount(self, parent=None):
        """Returns the number of row of the model.

        Returns:
            int: the number of rows
        """

        return len(self._groups)

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
