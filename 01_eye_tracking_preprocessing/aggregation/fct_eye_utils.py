#####################################################################
# Copyright (C) 2024 HIDDEN UNIVERSITY
# HIDDEN WEBSITE
# HIDDEN SUBTEXT
# HIDDEN INSTITUTE
# 
# Authors: AUTHORS CURRENTLY HIDDEN DUE TO ONGOING PEER REVIEW PROCESS
# 
# Licensed under the MIT License (the "License");
# you may only use this file in compliance with the License.
# You may obtain a copy of the License at
# 
#         https://mit-license.org/
# 
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
####################################################################

import multiprocessing
import pandas as pd
from datetime import timedelta
from joblib import Parallel, delayed

from aggregation.fct_stats import (
    get_stats,
    get_binary_stats,
    got_binary_event_stats,
    get_target_zone_stats,
    get_eventspec_stats,
    get_all_eye_movement_stats,
)
# from aggregation.fct_stats import get_single_eye_movement_stats
#

# This file has been copied from the master thesis of Andreas Marxer and has been adapted afterwards


# get_input_times returns a pd.DatetimeIndex corresponding to the step_size and epoch_width
def get_input_times(input_data, step_size, epoch_width) -> pd.DatetimeIndex:
    epoch_width = timedelta(seconds=epoch_width)
    date_range = pd.date_range(
        start=input_data.index[0].floor("s"),
        #end=input_data.index[-1].ceil("s") - epoch_width,
        end=input_data.index[-1].ceil("s"),
        freq=f"{step_size}s",
    )

    # only take timestamps where data is available
    filtered = date_range.to_series().apply(
        lambda i: ((input_data.index > i) & (input_data.index < i + epoch_width)).any()
    )

    return pd.DatetimeIndex(date_range.to_series()[filtered])


def get_features(
    data: pd.DataFrame,
    epoch_width: int = 60,
    num_cores: int = 0,
    step_size: float = 1,
    numerical_features: list[str]=None,
    binary_features: list[str]=None,
    single_eye_movement_features: list[str]=None,
    all_eye_movement_features: str = "event+eye_movement_type+eventspec",
    target_zone_names: list[str]=None,
) -> pd.DataFrame:
    """
    Function to get aggregated features in parallel implementation
    data: (pd.DataFrame) data of whole dataframe to aggregate (no columns 'id', 'label', 'scenario')
    epoch_width: (int) time window in [s] to aggregate
    num_cores: (int) number of CPU cores to be used
    :return: (pd.DataFrame) data of aggregated features with column 'num_samples'
    """
    if numerical_features is None:
        numerical_features = []
    if binary_features is None:
        binary_features = []
    if single_eye_movement_features is None:
        single_eye_movement_features = []
    if target_zone_names is None:
        target_zone_names = {}

    if not num_cores >= 1:
        num_cores = min(32, multiprocessing.cpu_count())
    print("using # cores: ", num_cores)

    input_data = data.copy()
    inputs = get_input_times(input_data, step_size, epoch_width)

    '''
    results = []
    for k in inputs:
        result = get_sliding_window(input_data, epoch_width=epoch_width, i=k,
                                     numerical_features=numerical_features, binary_features=binary_features,
                                     single_eye_movement_features=single_eye_movement_features,
                                     all_eye_movement_features=all_eye_movement_features,
                                     target_zone_names=target_zone_names)
        results.append(result)
    '''

    results = Parallel(n_jobs=num_cores, verbose=1)(
        delayed(get_sliding_window)(
            input_data,
            epoch_width=epoch_width,
            i=k,
            numerical_features=numerical_features,
            binary_features=binary_features,
            single_eye_movement_features=single_eye_movement_features,
            all_eye_movement_features=all_eye_movement_features,
            target_zone_names=target_zone_names,
        )
        for k in inputs
    )

    results = pd.DataFrame(list(filter(None, results)))  # filter out None values
    results.set_index("datetime", inplace=True)
    results.sort_index(inplace=True)

    return results


# data is whole dataframe
def get_sliding_window(
    data: pd.DataFrame,
    epoch_width: int,
    i: int,
    feature_type: str = "numerical",
    numerical_features: list[str]=None,
    binary_features: list[str]=None,
    single_eye_movement_features: list[str]=None,
    all_eye_movement_features: str = "event+eye_movement_type+eventspec",
    target_zone_names: list[str]=None,
) -> pd.DataFrame:
    """
    Function to get aggregated features in parallel implementation
    data: (pd.DataFrame) data of whole dataframe to aggregate (no columns 'id', 'label', 'scenario')
    epoch_width: (int) time window in [s] to aggregate
    i: (int) index of start frame of aggregation
    :return: (pd.DataFrame) data of aggregated features with column 'num_samples'
    """
    min_timestamp = i
    max_timestamp = min_timestamp + timedelta(seconds=epoch_width)
    results = {
        "datetime": min_timestamp,
    }

    relevant_data = data.loc[
        (data.index >= min_timestamp) & (data.index < max_timestamp)
    ]
    for column in relevant_data.columns:

        if column in numerical_features:
            column_results = get_stats(relevant_data[column], column, epoch_width=epoch_width)
            results.update(column_results)
        
        if column in binary_features:
            column_results = get_binary_stats(relevant_data[column], column, epoch_width=epoch_width)
            results.update(column_results)
        
        if column == all_eye_movement_features:
            column_results = get_all_eye_movement_stats(
                relevant_data[column], column, epoch_width=epoch_width
            )
            results.update(column_results)
        
        if column in binary_features:
            column_results = got_binary_event_stats(
                relevant_data[[column, "aoi+target_zone+", 'event+eye_movement_type+eventspec',
                               'gaze+angle_change+velocity']], target_zone_names, column, epoch_width=epoch_width
            )
            results.update(column_results)
        if column in ["aoi+target_zone+"]:
            column_results = get_target_zone_stats(relevant_data[[column, 'gaze+angle_change+velocity', 'event+FIXA+onehot',
                                                                  'event+eye_movement_type+eventspec']], target_zone_names)
            results.update(column_results)

        if column in ["event+eye_movement_peak_vel+eventspec",
                      "event+eye_movement_avg_vel+eventspec",
                      "event+eye_movement_med_vel+eventspec",
                      "event+eye_movement_amp_given+eventspec",
                      "event+eye_movement_amp_calc+eventspec",
                      "event+eye_movement_duration+eventspec"]:
            column_results = get_eventspec_stats(relevant_data[[column, "event+eye_movement_type+eventspec"
                                                                  ]], target_zone_names, column)
            results.update(column_results)
        
    return results
