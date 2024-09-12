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

"""
Generate aggregated window data from canlogger data
from (3000, 13) to (1, 13*14)
Save the aggregated data to `data_folder/canlogger/freq-{freq:03d}/aggregated_{window_size_sec:03d}.parquet`
"""

import os
import warnings

import pandas as pd
import numpy as np
import glob

from joblib import Parallel, delayed
from datetime import timedelta

from .aggregation_function import NUMERICAL_FUNCTIONS, BINARY_FUNCTIONS
from .aggregation_config import AggregationConfig

import warnings

warnings.filterwarnings("error", category=RuntimeWarning)

COLUMN_RENAMES = {
    'VehicleSpeed': 'vehicle+velocity+',
    'SteeringWheelAngle': 'driver+steer+angle',
    'SteeringWheelAngularVelocity': 'driver+steer+velocity',
    'BrakingPressure': 'driver+brake+pressure',
    'PedalForce': 'driver+gas+position',
    'LongitudinalAcceleration': 'vehicle+long+acceleration',
    'LateralAcceleration': 'vehicle+lat+acceleration',
    'BrakeActuation': 'driver+brake+active',
    'EngineSpeed': 'engine+velocity+',
    'EngineTorque': 'engine+torque+',
    'YawVelocity': 'vehicle+velocity+yaw',
    'RoadGradient': 'environment+road+gradient',
}


def get_stats_one_feature(data, key_prefix: str = None):
    """
    get statistics from data using aggregation functions
    """
    boolean = (data.dtypes == "boolean")
    data_nans = data.isna().sum()
    if data_nans > 0:
        warnings.warn(f'input data contains {data_nans} NaNs which will be removed')
    data = data.dropna()
    data = np.asanyarray(data)

    results = {}
    if not boolean:
        #
        if len(data) > 0:
            for key, value in NUMERICAL_FUNCTIONS.items():
                if key in ["power", "rms"]:
                    if np.count_nonzero(data) == 0:
                        results[key] = 0
                        continue

                if key in ["kurtosis", "skewness"]:
                    try:
                        if results["std"] < 1e-5:
                            results[key] = 0.0
                        else:
                            results[key] = value(data)
                    except Exception as e:
                        print(f"Warning caught: {e}" + " - Caused by: "
                              + key + " of "+ key_prefix + " with mean: "
                              + str(results["mean"]) + "and STD:"
                              + str(results["std"]))
                        results[key] = 0.0
                    continue
                results[key] = value(data)
        else:
            for key in NUMERICAL_FUNCTIONS.keys():
                results[key] = np.nan
        #except Exception as e:
        #    print(f"Exception caught: {e}" + "caused by: " + key_prefix)
    else:
        try:
            if len(data) > 0:
                for key, value in BINARY_FUNCTIONS.items():
                    results[key] = value(data)
            else:
                for key in BINARY_FUNCTIONS.keys():
                    results[key] = np.nan
        except Exception as e:
            print(e)

    if key_prefix is not None:
        results = {key_prefix + '+' + k: v for k, v in results.items()}
    return results


def __get_stats_window(data: pd.DataFrame, features, epoch_width, start, window_size_sec: int, freq: int):
    end = start + epoch_width
    window = data.loc[start:end]
    window = window[:-1]
    results = {
        'datetime': start,
        'agg+proportion_num_samples+CAN+': len(window) / (window_size_sec * freq)
    }
    '''
    if len(window) < window_size_sec * freq:
        return None
    else:
    '''
    # only use window with enough data
    for column in features:
        column_agg = get_stats_one_feature(window[column], key_prefix=f'{column}')
        results.update(column_agg)
    return results


def generate_canlogger_window(subject: int, data: pd.DataFrame, window_size_sec: int, freq: int, shift: int, features):
    """
    generate windowed data from canlogger data, using aggregation functions
    :param subject:
    :param data:
    :param window_size_sec:
    :param shift: second
    """
    input_data = data.copy()
    epoch_width = timedelta(seconds=window_size_sec)
    #date_range = pd.date_range(start=data.index[0].ceil('s'), end=data.index[-1].floor('s') - epoch_width,
    #                           freq=f'{shift}s')
    date_range = pd.date_range(start=data.index[0].ceil('s'), end=data.index[-1].floor('s'),
                               freq=f'{shift}s')
    results = Parallel(n_jobs=1)(
        delayed(__get_stats_window)(input_data, features, epoch_width, start, window_size_sec, freq) for start in
        date_range)
    results = pd.DataFrame(list(filter(None, results)))
    if len(results) == 0:
        return None
    results.set_index('datetime', inplace=True)
    results.sort_index(inplace=True)
    feature_cols = [col for col in results.columns if col != 'agg+proportion_num_samples+CAN+']
    results = results.dropna(subset=feature_cols, how='all')
    return results

def calculate_differential(series):
    """
    Calculate the differential of a pandas Series as the difference divided by the time delta.

    Parameters:
    series (pd.Series): A pandas Series with a datetime index.

    Returns:
    pd.Series: A pandas Series containing the differentials.
    """
    if series.dtype == 'boolean':
        # Convert boolean series to integers (True -> 1, False -> 0)
        value_diff = series.astype(int).diff().fillna(0)
    else:
        # Calculate the differences between consecutive values
        value_diff = series.diff().fillna(0)

    # Calculate the time deltas in seconds
    time_diff = series.index.to_series().diff().dt.total_seconds()

    # Calculate the differential as difference divided by timedelta
    differential = (value_diff / time_diff).fillna(0)

    return differential


def generate_canlogger_subject(subject:int, config: AggregationConfig, window_size_sec: int):
    """
    Generate canlogger data from folder and only use selected features to generate aggregated window
    :param data_folder:
    :param subject:
    :param window_size_sec:
    :return:
    """
    

    data_folder = config.data_directory
    freq = config.freq
    relative_subject_output_directory = config.relative_subject_output_directory

    folder = glob.glob(f'{data_folder}/drive_{subject}/')[0]
    print(f'Generating dataset for subject {subject}')
    data = pd.read_parquet(folder + f'{relative_subject_output_directory}/can-scenario_freq-{freq:03d}.parquet')

    if data is None:
        print(f'No can-scenario data for subject {subject}, please check!')
        return None

    # filter out data with validity != 1
    data = data[data['validity'] == 1]
    data = data.loc[:, ['scenario', 'scenario_number', 'phase'] + list(COLUMN_RENAMES.keys())]

    # make all value float rename columns
    data[list(COLUMN_RENAMES.keys())] = data[list(COLUMN_RENAMES.keys())].apply(
        lambda x: pd.to_numeric(x, errors='raise', downcast='float'))
    data.rename(columns=COLUMN_RENAMES, inplace=True)

    data['vehicle+acceleration+'] = calculate_differential(data['vehicle+velocity+'])
    data['vehicle+jerk+'] = calculate_differential(data['vehicle+acceleration+'])
    data['vehicle+snap+'] = calculate_differential(data['vehicle+jerk+'])

    data['driver+steer+acceleration'] = calculate_differential(data['driver+steer+velocity'])
    data['driver+steer+jerk'] = calculate_differential(data['driver+steer+acceleration'])
    data['driver+steer+snap'] = calculate_differential(data['driver+steer+jerk'])

    data['driver+brake+velocity'] = calculate_differential(data['driver+brake+pressure'])
    data['driver+brake+acceleration'] = calculate_differential(data['driver+brake+velocity'])
    data['driver+brake+jerk'] = calculate_differential(data['driver+brake+acceleration'])
    data['driver+brake+snap'] = calculate_differential(data['driver+brake+jerk'])

    data['driver+gas+velocity'] = calculate_differential(data['driver+gas+position'])
    data['driver+gas+acceleration'] = calculate_differential(data['driver+gas+velocity'])
    data['driver+gas+jerk'] = calculate_differential(data['driver+gas+acceleration'])
    data['driver+gas+snap'] = calculate_differential(data['driver+brake+jerk'])

    data['vehicle+lat+jerk'] = calculate_differential(data['vehicle+lat+acceleration'])
    data['vehicle+lat+snap'] = calculate_differential(data['vehicle+lat+jerk'])

    data['vehicle+long+jerk'] = calculate_differential(data['vehicle+long+acceleration'])
    data['vehicle+long+snap'] = calculate_differential(data['vehicle+long+jerk'])

    data['driver+brake+activation'] = calculate_differential(data['driver+brake+active'])

    data['engine+acceleration+'] = calculate_differential(data['engine+velocity+'])
    data['engine+jerk+'] = calculate_differential(data['engine+acceleration+'])
    data['engine+snap+'] = calculate_differential(data['vehicle+jerk+'])

    data['engine+power+'] = calculate_differential(data['engine+torque+'])

    data['vehicle+acceleration+yaw'] = calculate_differential(data['vehicle+velocity+yaw'])
    data['vehicle+jerk+yaw'] = calculate_differential(data['vehicle+acceleration+yaw'])
    data['vehicle+snap+yaw'] = calculate_differential(data['vehicle+jerk+yaw'])

    data = data.convert_dtypes()
    for column in data.columns:
        if column in ['scenario', 'scenario_number', 'phase']:
            continue
        new_column = pd.DataFrame({column + "_abs": data[column].abs()})
        data = pd.concat([data, new_column], axis=1)

    dataset = []
    for phase in [1, 2, 3]:
        data_phase = data[data['phase'] == phase]
        for scenario in data_phase['scenario'].unique():
            for scenario_num in data_phase['scenario_number'].unique():
                data_scenario = data_phase[(data_phase['scenario'] == scenario) & (
                        data_phase['scenario_number'] == scenario_num)]
                if len(data_scenario) > 0:
                    df = generate_canlogger_window(subject, data_scenario, window_size_sec, freq, shift=1,
                                                   features=data.columns.difference(
                                                       ['phase', 'scenario', 'scenario_number'])
                                                   )
                    if df is None:
                        continue

                    new_columns = {
                        'groundtruth+phase+CAN+': [phase] * len(df),
                        'groundtruth+scenario+CAN+': [scenario] * len(df),
                        'groundtruth+variant+CAN+': [scenario_num] * len(df),
                        'groundtruth+id+CAN+': [subject] * len(df)
                    }
                    new_df = pd.DataFrame(new_columns, index=df.index)
                    df = pd.concat([df, new_df], axis=1)

                    dataset.append(df)

    dataset = pd.concat(dataset)
    dataset = dataset.sort_index()
    dataset.index = dataset.index.floor(freq='s')

    # Move groundtruth columns to the front.
    cols_to_move = ['groundtruth+phase+CAN+', 'groundtruth+scenario+CAN+',
                    'groundtruth+variant+CAN+', 'groundtruth+id+CAN+']
    remaining_cols = [col for col in dataset.columns if col not in cols_to_move]
    new_col_order = cols_to_move + remaining_cols
    dataset = dataset[new_col_order]

    return dataset


def load_canlogger_subject(subject:int, config: AggregationConfig, window_size_sec: int):
    """
    Load aggregated window data of canlogger for one subject
    If not there, generate
    called by generate_canlogger
    """
    data_folder = config.data_directory
    freq = config.freq
    reusing = config.reusing_old_df
    relative_subject_output_directory = config.relative_subject_output_directory

    data_filename = f'{data_folder}/drive_{subject}/{relative_subject_output_directory}/aggregated_{window_size_sec:03d}_freq-{freq:03d}.parquet'
    if reusing and os.path.exists(data_filename):
        print("Reusing data for subject", subject)
        data = pd.read_parquet(data_filename)
        return data
    else:
        data = generate_canlogger_subject(subject, config, window_size_sec)
        if data is None:
            print(f"No canlogger feature windows generated for subject {subject}")
            return None
        data.to_parquet(data_filename, allow_truncated_timestamps=True, coerce_timestamps='ms')
    return data


def generate_canlogger(config: AggregationConfig, window_size_sec: int):
    """
    Generate data from can logger data for all selected subjects
    """
    subjects = config.subjects
    data_folder = config.data_directory
    n_jobs = config.n_jobs

    if subjects is None:
        subjects = [int(x.split('/')[-2].split('_')[-1]) for x in glob.glob(f'{data_folder}/drive_2*/')]

    print(f'Generating dataset for {len(subjects)} subjects: {sorted(subjects)}')
    with Parallel(n_jobs=min(n_jobs, len(subjects)), verbose=1) as parallel:
        df = parallel(
            delayed(load_canlogger_subject)(subject, config, window_size_sec) for subject in
            subjects)
    '''
    df = []
    for subject in subjects:
        df.append(load_canlogger_subject(subject, config, window_size_sec))
    '''
    df = pd.concat(df)
    return df
    


def load_agg_canlogger(config: AggregationConfig, window_size_sec: int):
    """
    Load aggregated window data for all selected subjects.
    If not there, generate
    """

    data_folder = config.data_directory
    freq = config.freq
    reusing = config.reusing_old_df
    output_folder = config.data_output_directory

    data_filename = output_folder + f'aggregated_{window_size_sec:03d}_freq-{freq:03d}.parquet'
    canlogger_data = generate_canlogger(config, window_size_sec)
    if canlogger_data is None:
        print(f"No canlogger feature windows generated")
    canlogger_data.sort_index(inplace=True)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    canlogger_data.to_parquet(data_filename, allow_truncated_timestamps=True, coerce_timestamps='ms')
    print(f"Saved aggregated data to {data_filename}")
    return canlogger_data
