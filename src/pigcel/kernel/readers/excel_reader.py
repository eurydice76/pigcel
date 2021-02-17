"""This module implements the following classes and functions:
    - InvalidExcelWorkbookError
    - UnknownPropertyError
    - InvalidTimeError
    - ExcelWorkbookReader
"""

import collections
import logging
import os
import sys

import openpyxl

import pandas as pd

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
    """This class implements the reader for the data stored in excel file. To be valid the excel file must contain respectively
    'Suivi', 'Data', 'Gaz du sang' and 'NFS' sheets.
    """

    times = set(['-0h30', '0h00', '0h10', '0h20', '0h30', '1h00', '1h30', '2h00', '3h00', '4h00', '5h00', '6h00'])

    def __init__(self, filename):
        """Constructor

        Args:
            filename (str): the path to the workbook
        """

        self._workbook = openpyxl.load_workbook(filename, data_only=True)

        self._filename = filename

        sheet_names = set(self._workbook.get_sheet_names())

        for sheet_name in sheet_names:
            ss_sheet = self._workbook[sheet_name]
            # You have to proceed in two steps to change the sheet title as it it case insensitive
            ss_sheet.title = sheet_name.lower().strip() + '1'
            ss_sheet.title = sheet_name.lower().strip()

        sheet_names = set(self._workbook.get_sheet_names())
        
        if len(sheet_names.intersection(['suivi', 'data', 'gaz du sang', 'nfs'])) != 4:
            raise InvalidExcelWorkbookError('One or more compulsory sheets are missing in {} file.'.format(self._filename))

        self._data = self.parse_data_worksheet()
        self._data = pd.concat([self._data, self.parse_blood_gas_worksheet()], axis=1)
        self._data = pd.concat([self._data, self.parse_nfs_worksheet()], axis=1)
        self._data = self._data.reindex(sorted(self._data.columns), axis=1)

        if set(self._data.index) != ExcelWorkbookReader.times:
            raise InvalidExcelWorkbookError('Times not properly defined in {}.'.format(filename))


    @property
    def basename(self):
        """Returns the basename of the excel file.

        Returns:
            str: the basename
        """

        return os.path.splitext(os.path.basename(self._filename))[0]

    @property
    def data(self):
        """Returns the data.

        Returns:
            pandas.DataFrame: the data
        """

        return self._data

    @property
    def filename(self):
        """Returns the workbook's filename.

        Returns:
            str: the filename
        """

        return self._filename

    def get_property_slice(self, selected_property):
        """Return a slice of the data according to a given property and selected times.

        Args:
            selected_property (str): the selected property

        Returns:
            pd.DataFrame: the slice
        """

        if selected_property in self._data.columns:
            property_slice = self._data[selected_property]
        else:
            property_slice = pd.Series(np.nan, index=self._data.index)
            logging.warning('Property {} could not be found in {} workbook'.format(selected_property, self._filename))

        property_slice = pd.DataFrame(property_slice.to_numpy(), index=property_slice.index, columns=[self._filename])

        return property_slice

    def get_time_slice(self, selected_time):
        """Return a slice of the data according to a given time.

        Args:
            selected_time (str): the time

        Returns:
            pd.DataFrame: the slice. pandas.DataFrame whose single index is the selected time and columns are the properties of the workbook
        """

        if selected_time in self._data.index:
            time_slice = pd.DataFrame(self._data.loc[selected_time], columns=[selected_time], index=self._data.columns).T
        else:
            time_slice = pd.DataFrame(np.nan, index=[selected_time], columns=self._data.columns)
            logging.warning('Time {} could not be found in the {} workbook'.format(selected_time, self._filename))

        return time_slice

    @ property
    def information(self):
        """Parse the sheet 'Suivi' and stringify the data stored in it.

        Returns:
            str: the general information about the animal
        """

        data_sheet = self._workbook.get_sheet_by_name('suivi')

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

        data_sheet = self._workbook['gaz du sang']

        times_row = [cell.value for cell in data_sheet[4]]
        row_indexes = []
        for i, v in enumerate(times_row):
            if v is None:
                continue
            if v.lower().strip() in ['temps', 'remarque']:
                continue
            row_indexes.append(i)
        first_time = row_indexes[0]
        last_time = row_indexes[-1]

        properties_col = [cell.value for cell in data_sheet['A']]
        properties_col = [v.lower().strip() if v is not None else v for v in properties_col]
        col_indexes = []
        for i, v in enumerate(properties_col):
            if i < 5:
                continue
            if v is None:
                continue
            if v.lower().strip() in ['temps', 'remarque']:
                continue
            col_indexes.append(i)
        first_property = col_indexes[0]
        last_property = col_indexes[-1]

        data_by_rows = tuple(data_sheet.rows)

        data = []
        for row in range(first_property, last_property+1):
            columns = []
            for col in range(first_time, last_time+1):
                value = data_by_rows[row][col].value
                columns.append(float(value) if value is not None else np.nan)
            data.append(columns)

        data = list(zip(*data))
        data = pd.DataFrame(data, columns=properties_col[first_property:last_property+1], index=times_row[first_time:last_time+1])

        return data

    def parse_data_worksheet(self):
        """Parse the sheet 'Data' and fetch the data stored in it.

        Returns:
            collections.OrderedDict: the data
        """

        data_sheet = self._workbook.get_sheet_by_name('data')

        time_column = [cell.value for cell in data_sheet['A']]
        row_indexes = [i for i, v in enumerate(time_column) if v is not None]
        first_time = row_indexes[0]
        last_time = row_indexes[-1]

        properties_row = [cell.value for cell in data_sheet[6]]
        properties_row = [v.lower().strip() if v is not None else v for v in properties_row]
        col_indexes = []
        for i, v in enumerate(properties_row):
            if v is None:
                continue
            if v.lower().strip() in ['temps', 'remarque']:
                continue
            col_indexes.append(i)
        first_property = col_indexes[0]
        last_property = col_indexes[-1]

        data_by_rows = tuple(data_sheet.rows)

        data = []
        for row in range(first_time, last_time+1):
            columns = []
            for col in range(first_property, last_property+1):
                value = data_by_rows[row][col].value
                columns.append(float(value) if value is not None else np.nan)
            data.append(columns)

        data = pd.DataFrame(data, columns=properties_row[first_property:last_property+1], index=time_column[first_time:last_time+1])

        return data

    def parse_nfs_worksheet(self):
        """Parse the sheet 'NFS' and fetch the data stored in it.

        Returns:
            collections.OrderedDict: the data
        """

        data_sheet = self._workbook.get_sheet_by_name('nfs')

        times_row = [cell.value for cell in data_sheet[2]]
        row_indexes = []
        for i, v in enumerate(times_row):
            if v is None:
                continue
            if v.lower().strip() in ['temps', 'remarque']:
                continue
            row_indexes.append(i)
        first_time = row_indexes[0]
        last_time = row_indexes[-1]

        properties_col = [cell.value for cell in data_sheet['C']]
        properties_col = [v.lower().strip() if v is not None else v for v in properties_col]
        col_indexes = []
        for i, v in enumerate(properties_col):
            if v is None:
                continue
            if v.lower().strip() in ['temps', 'remarque']:
                continue
            col_indexes.append(i)
        first_property = col_indexes[0]
        last_property = col_indexes[-1]

        data_by_rows = tuple(data_sheet.rows)

        data = []
        for row in range(first_property, last_property+1):
            columns = []
            for col in range(first_time, last_time+1):
                value = data_by_rows[row][col].value
                columns.append(float(value) if value is not None else np.nan)
            data.append(columns)

        data = list(zip(*data))
        data = pd.DataFrame(data, columns=properties_col[first_property:last_property+1], index=times_row[first_time:last_time+1])

        return data


if __name__ == '__main__':

    workbook = sys.argv[1]

    mwb = ExcelWorkbookReader(workbook)

    print(mwb.information)

    print(mwb.data)

    print(mwb.get_property_slice('AchE'))

    print(mwb.get_time_slice('0h00'))
