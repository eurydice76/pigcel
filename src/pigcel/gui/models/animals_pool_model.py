
"""This module implements the following classes:
    - InvalidPoolData
    - AnimalsPoolModel
"""

import collections
import logging
import os

from PyQt5 import QtCore

import numpy as np

import pandas as pd

import scipy.stats as stats

import scikit_posthocs as sk

from pigcel.kernel.readers.excel_reader import ExcelWorkbookReader, InvalidTimeError, UnknownPropertyError
from pigcel.kernel.utils.stats import statistical_functions
from pigcel.gui.models.animals_data_model import AnimalsDataModel


class InvalidPoolData(Exception):
    """This class implements an exception which is raised when the data stored in the pool is invalid.
    """


class AnimalsPoolModel(QtCore.QAbstractListModel):
    """This class implemenents a model for storing anials that belong to the same pool for further statistical analysis.
    """

    Workbook = QtCore.Qt.UserRole + 1

    def __init__(self, animals_data_model, *args, **kwargs):

        super(AnimalsPoolModel, self).__init__(*args, **kwargs)

        self._animals_data_model = animals_data_model

        self._animals = []

    def add_animal(self, animal):
        """Add a new animal to the pool.

        Args:
            animal (str): the animal
        """

        # Only new animals can be added
        if animal in self._animals:
            return

        # The animal must have been loaded before
        for i in range(self._animals_data_model.rowCount()):
            index = self._animals_data_model.index(i)
            text = self._animals_data_model.data(index, QtCore.Qt.DisplayRole)
            if text == animal:
                break
        else:
            return

        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())

        self._animals.append(animal)

        self.endInsertRows()

    @property
    def animals(self):
        """Returns the animals in the pool.

        Returns:
            list of str: the animals of the pool
        """

        return self._animals

    def data(self, index, role):
        """Get the data at a given index for a given role.

        Args:
            index (QtCore.QModelIndex): the index
            role (int): the role

        Returns:
            QtCore.QVariant: the data
        """

        if not self._animals:
            return QtCore.QVariant()

        if not index.isValid():
            return QtCore.QVariant()

        row = index.row()

        animal = self._animals[row]

        if role == QtCore.Qt.DisplayRole:

            return animal

        elif role == AnimalsPoolModel.Workbook:

            for i in range(self._animals_data_model.rowCount()):
                index = self._animals_data_model.index(i)
                text = self._animals_data_model.data(index, QtCore.Qt.DisplayRole)
                if text == animal:
                    return self._animals_data_model.data(index, AnimalsDataModel.Workbook)

        return QtCore.QVariant()

    def evaluate_global_time_effect(self, selected_property):
        """Evaluate the global time effect for a given property for the pool.

        Args:
            selected_property (str): the selected property

        Returns:
            float: the p value resulting from the Friedmann test
        """

        pool_data = self.get_pool_data(selected_property)

        data = []
        for _, v in pool_data.iterrows():
            # If there is any undefined value for this time, skip it
            if np.isnan(v).any():
                continue
            data.append(v)

        try:
            return stats.friedmanchisquare(*data).pvalue
        except ValueError:
            return np.nan

    def evaluate_pairwise_time_effect(self, selected_property):
        """Evaluate the time effect pairwisely for a given property for the pool.

        Args:
            selected_property (str): the selected property

        Returns:
            pandas.DataFrame: the p-values resulting from the Dunn posthocs test
        """

        pool_data = self.get_pool_data(selected_property)

        data = []
        valid_times = []
        for row, v in pool_data.iterrows():
            # If there is any undefined value for this time, skip it
            if np.isnan(v).any():
                continue
            data.append(v)
            valid_times.append(row)

        if not data:
            raise InvalidPoolData('No valid times found for building the data used by Dunn posthoc test')

        try:
            df = sk.posthoc_dunn(data)
            df.columns = valid_times
            df.index = valid_times
        except ValueError as error:
            logging.error(str(error))
            df = pd.DataFrame(np.nan, index=valid_times, columns=valid_times)

        return df

    def evaluate_premortem_time_effect(self, selected_property, *, n_target_times=6):
        """Compute the premortem time effect for the pool. The premortem statistics is a special kind of time effect statistics 
        used for animals for which the time of death differ. In such case, the standard time effect statistics can not be performed 
        because the time samples will be of different length. In premortem statistics, we only consider the n last times before the death. 
        In doing so, we insure that the samples used for performing Friedman chi square statistics will be of equal length.

        Args:
            selected_property (str): the property
            n_target_times (int): the number of times before the animal's death for evaluating the time effect

        Returns:
            2-tuple: a tuple whose 1st element is the p_value resulting from Friedman chi square test and the 2nd element is the Dunn matrix
            stored as a pandas.DataFrame
        """

        if n_target_times not in range(1, len(ExcelWorkbookReader.times)-1):
            raise InvalidTimeError('Invalid target times.')

        data = pd.DataFrame()

        selected_animals = []
        for animal in self._animals:
            wb = self._animals_data_model.get_workbook(animal)
            if wb is None:
                continue

            try:
                property_slice = wb.get_property_slice(selected_property)
            except (UnknownPropertyError, InvalidTimeError) as error:
                logging.error(str(error))
                continue

            reference_value = property_slice['T-30']
            if np.isnan(reference_value):
                logging.error('The reference time is undefined for animal {}'.format(animal))
                continue

            # Search for the first nan element (if any) starting from the end
            last_non_nan_index = len(property_slice) - 1
            while property_slice[last_non_nan_index] == np.nan:
                last_non_nan_index -= 1
                if last_non_nan_index < 0:
                    last_non_nan_index = len(property_slice) - 1
                    break

            first_index = last_non_nan_index - n_target_times
            if first_index < 0:
                logging.error('Less data than targets for animal {}'.format(animal))
                continue

            selected_animals.append(animal)
            times = ['T-30'] + list(property_slice.index[first_index:last_non_nan_index+1])
            data_per_animal = [reference_value] + list(property_slice.iloc[first_index:last_non_nan_index+1])
            data_per_animal = pd.Series(data_per_animal, index=times)

            data = pd.concat([data, data_per_animal], axis=1)

        data.columns = selected_animals

        try:
            friedman_statistics = stats.friedmanchisquare(*data.to_numpy()).pvalue
        except ValueError:
            friedman_statistics = np.nan

        try:
            dunn_matrix = sk.posthoc_dunn(data.to_numpy().tolist())
            dunn_matrix.columns = times
            dunn_matrix.index = times
        except ValueError as error:
            logging.error(str(error))
            dunn_matrix = pd.DataFrame(np.nan, index=times, columns=times)

        return friedman_statistics, dunn_matrix

    def get_pool_data(self, selected_property):
        """Get the data stored in the pool for a given property.

        Args:
            selected_property (str): the property

        Returns:
            pandas.DataFrame: the pool data
        """

        data = pd.DataFrame()
        valid_animals = []
        for animal in self._animals:
            wb = self._animals_data_model.get_workbook(animal)
            if wb is None:
                continue

            try:
                property_slice = wb.get_property_slice(selected_property)
            except (UnknownPropertyError, InvalidTimeError) as error:
                logging.error(str(error))
                continue
            else:
                valid_animals.append(animal)
                data = pd.concat([data, property_slice], axis=1)

        if not valid_animals:
            raise InvalidPoolData('No valid animal was found for this pool')

        data.columns = valid_animals

        return data

    def get_reduced_data(self, selected_property, selected_statistics=None):
        """Reduced the pool data for a given property according a set of given statistics.

        Args:
            selected_property (str): the property
            selected_statistics (list): the statistics

        Returns:
            pandas.DataFrame: the reduced data stored stored as pandas.DataFrame where the columns are the statistics and the row the time
        """

        if selected_statistics is None:
            selected_statistics = list(statistical_functions.keys())
        else:
            available_statistics_functions = set(statistical_functions.keys())
            selected_statistics = list(available_statistics_functions.intersection(selected_statistics))

        if not selected_statistics:
            raise InvalidPoolData('Invalid statistics for reducing the pool data')

        pool_data = self.get_pool_data(selected_property)

        reduced_pool_data = pd.DataFrame()
        for func in selected_statistics:
            reduced_pool_data = pd.concat([reduced_pool_data, pd.Series(
                statistical_functions[func](pool_data.to_numpy(), axis=1), index=pool_data.index)], axis=1)

        reduced_pool_data.columns = selected_statistics

        return reduced_pool_data

    def remove_animal(self, animal):
        """Remove an animal from the model.

        Args:
            animal (str): the name of the animal
        """

        if animal not in self._animals:
            return

        index = self._animals.index(animal)

        self.beginRemoveRows(QtCore.QModelIndex(), index, index)

        self._animals.remove(animal)

        self.endRemoveRows()

    def rowCount(self, parent=QtCore.QModelIndex()):
        """Returns the number of rows.

        Returns:
            int: the number of rows
        """

        return len(self._animals)
