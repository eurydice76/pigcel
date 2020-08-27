import collections
import os
import sys

import openpyxl

import numpy as np


class InvalidExcelWorkbookError(Exception):
    """This class implements an exception raised when the workbook is invalid.
    """


class UnknownPropertyError(Exception):
    """This class implements an exception raised when a requested property is unknown.
    """


class InvalidTimeError(Exception):
    """This class implements an exception raised when a requested time is not valid.
    """


class ExcelWorkbookReader:

    times = ['T-30', 'T0', 'T10', 'T20', 'T30', 'T1H', 'T1H30', 'T2H', 'T3H', 'T4H', 'T5H', 'T6H']

    def __init__(self, filename):
        """Constructor

        Args:
            filename (str): the path to the workbook
        """

        self._workbook = openpyxl.load_workbook(filename)

        sheet_names = set(self._workbook.get_sheet_names())

        if len(sheet_names.intersection(['Suivi', 'Data', 'Gaz du sang', 'NFS'])) != 4:
            raise InvalidExcelWorkbookError('One or more compulsory sheets are missing.')

        self._filename = filename

    @property
    def properties(self):
        """Returns the properties stored in the workbook. Only the sheet 'Data', 'Gaz du sang' and 'NFS' are considered.

        Returns:
            list of str: the properties
        """

        properties = []

        data_sheet = self._workbook.get_sheet_by_name('Data')
        properties.extend([data_sheet.cell(row=6, column=col).value for col in range(3, 22)])

        blood_gas_sheet = self._workbook.get_sheet_by_name('Gaz du sang')
        properties.extend([blood_gas_sheet.cell(row=row, column=1).value for row in range(6, 31)])

        nfs_sheet = self._workbook.get_sheet_by_name('NFS')
        properties.extend([nfs_sheet.cell(row=row, column=3).value for row in range(3, 17)])

        return properties

    @property
    def basename(self):

        return os.path.splitext(os.path.basename(self._filename))[0]

    @property
    def filename(self):
        """Returns the workbook's filename.

        Returns:
            str: the filename
        """

        return self._filename

    def get_data(self, selected_property=None, selected_time=None):
        """Returns the data stored in the workbook. Only the sheet 'Data', 'Gaz du sang' and 'NFS' are considered.

        Returns:
            collections.OrderedDict: the data
        """

        data = collections.OrderedDict()

        data.update(self.parse_data_worksheet())
        data.update(self.parse_blood_gas_worksheet())
        data.update(self.parse_nfs_worksheet())

        if selected_property is not None:
            if selected_property not in data:
                raise UnknownPropertyError('The property {} is unknown'.format(selected_property))
            else:
                data = collections.OrderedDict([(selected_property, data[selected_property])])

        if selected_time is not None:
            try:
                selected_time_index = ExcelWorkbookReader.times.index(selected_time)
            except ValueError:
                raise InvalidTimeError('The time {} is not a valid time'.format(selected_time))
            else:
                for k in data:
                    data[k] = [data[k][selected_time_index]]

        return data

    @ property
    def information(self):
        """Parse the sheet 'Suivi' and stringify the data stored in it.

        Returns:
            str: the general information about the animal
        """

        data_sheet = self._workbook.get_sheet_by_name('Suivi')

        cells = data_sheet['A1':'B13']

        info = []
        for cell1, cell2 in cells:
            info.append(': '.join([str(cell1.value), str(cell2.value)]))

        info = '\n'.join(info)

        return info

    def parse_blood_gas_worksheet(self):
        """Parse the sheet 'Gaz du sang' and fetch the data stored in it.

        Returns:
            collections.OrderedDict: the data
        """

        data_sheet = self._workbook.get_sheet_by_name('Gaz du sang')

        properties = [data_sheet.cell(row=row, column=1).value for row in range(6, 31)]

        cells = data_sheet['B6':'M30']

        data = collections.OrderedDict()

        for row, prop in enumerate(properties):
            data[prop] = [cell.value if cell.value is not None else np.nan for cell in cells[row]]

        return data

    def parse_data_worksheet(self):
        """Parse the sheet 'Data' and fetch the data stored in it.

        Returns:
            collections.OrderedDict: the data
        """

        data_sheet = self._workbook.get_sheet_by_name('Data')

        properties = [data_sheet.cell(row=6, column=col).value for col in range(3, 22)]

        cells = data_sheet['C7':'U18']

        cells = list(zip(*cells))

        data = collections.OrderedDict()

        for col, prop in enumerate(properties):
            data[prop] = [cell.value if cell.value is not None else np.nan for cell in cells[col]]

        return data

    def parse_nfs_worksheet(self):
        """Parse the sheet 'NFS' and fetch the data stored in it.

        Returns:
            collections.OrderedDict: the data
        """

        data_sheet = self._workbook.get_sheet_by_name('NFS')

        properties = [data_sheet.cell(row=row, column=3).value for row in range(3, 17)]

        cells = data_sheet['D3':'M16']

        data = collections.OrderedDict()

        selected_times = [0, 1, 5, 8, 11]
        selected_values = [0, 2, 4, 6, 8]

        for row, prop in enumerate(properties):

            values = [cell.value for cell in cells[row]]

            data[prop] = [np.nan]*len(self.times)

            for i in range(len(selected_values)):
                data[prop][selected_times[i]] = values[selected_values[i]]

        return data


if __name__ == '__main__':

    workbook = sys.argv[1]

    mwb = ExcelWorkbookReader(workbook)

    mwb.parse_data_worksheet()

    mwb.parse_blood_gas_worksheet()

    mwb.parse_nfs_worksheet()

    mwb.get_data()

    mwb.get_general_information()
