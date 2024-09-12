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

import datetime
import numpy as np
import pandas as pd
import math

from collections import defaultdict
from itertools import groupby
from scipy.stats import skew, kurtosis, iqr, entropy
import warnings

warnings.filterwarnings("error", category=RuntimeWarning)


# from entropy import perm_entropy, spectral_entropy, svd_entropy, app_entropy, sample_entropy


# This file has been copied from the master thesis of Andreas Marxer and has been adapted afterwards


def get_stats(data: pd.DataFrame, key_suffix: str = None, epoch_width: int = 60) -> pd.DataFrame:
    """
    Function defining the statistical measures considered for aggregation
    :return: (pd.DataFrame) data of aggregated featues with column 'num_samples'
    """
    results = {
        "mean": np.nan,
        "median": np.nan,
        "std": np.nan,
        "q5": np.nan,  # 5% quantil
        "q95": np.nan,  # 95% quantil
        "iqr": np.nan,  # inter quantil range
        "power": np.nan,
        "skewness": np.nan,
        "kurtosis": np.nan,
        "n_sign_changes": np.nan,
        #'ratio': np.nan,
    }
    if (len(data) > 0) and (not data.isna().all()):
        results["mean"] = np.mean(data)
        results["median"] = np.nanmedian(data)  # RD was median
        results["std"] = np.std(data)
        results["q5"] = np.nanquantile(data, 0.05)  # RD was quantile
        results["q95"] = np.nanquantile(data, 0.95)  # RD was quantile
        results["iqr"] = iqr(
            data, nan_policy="omit"
        )  # RD nan_policy was default before
        results["energy"] = np.nansum(
            [x**2 for x in data]
        )  # * scale_factor #RD was sum before
        if np.count_nonzero(data) == 0:
            results["power"] = 0
        else:
            results["power"] = results["energy"] / np.count_nonzero(data)
        try:
            results["skewness"] = float(
                skew(data, nan_policy="omit")
            )  # RD nan_policy was default before, float conversion wasn't there but there were issues
        except RuntimeWarning as e:
            print(f"Warning caught: {e}" + " cause by: " + key_suffix)
        try:
            results["kurtosis"] = kurtosis(
                data, nan_policy="omit"
            )  # RD nan_policy was default before
        except RuntimeWarning as e:
            print(f"Warning caught: {e}" + " caused by: " + key_suffix)
        # Ensure that we do not divide by zero
        nan_mask = np.isnan(data)
        results["n_sign_changes"] = np.nansum(
            np.diff(
                np.sign(
                    data,
                )
            )
            != 0
        )
        # results['ratio'] = math.log(max(data) / statistics.median(data))
    """
    
    if len(data) > 0:
        results['mean'] = np.mean(data)
        results['median'] = np.median(data)
        results['std'] = np.std(data)
        results['q5'] = np.quantile(data, 0.05)
        results['q95'] = np.quantile(data, 0.95)
        results['range'] = results['max'] - results['min']
        results['iqr'] = iqr(data)
        results['energy'] = np.sum([x**2 for x in data]) #* scale_factor
        results['skewness'] = skew(data)
        results['kurtosis'] = kurtosis(data)
        results['rms'] = np.sqrt(results['energy'] / len(data))
        results['lineintegral'] = np.abs(np.diff(data)).sum()
        results['n_sign_changes'] = np.sum(np.diff(np.sign(data
                                                           ,)) != 0)
        #results['ratio'] = math.log(max(data) / statistics.median(data))
    """
    if key_suffix is not None:
        results = {key_suffix + "+" + k: v for k, v in results.items()}

    results["agg+num_samples++"] = len(data)  # added marxera
    results["agg+num_samples+not_nan+"] = data.count()

    return results


def get_binary_stats(data: pd.DataFrame, key_suffix: str = None, epoch_width: int = 60) -> pd.DataFrame:
    """
    Function defining the statistical measures considered for aggregation
    :return: (pd.DataFrame) data of aggregated featues with column 'num_samples'
    """
    results = {
        "sum": np.nan,
        "std": np.nan,
        "mean": np.mean,
    }

    if (len(data) > 0) and (not data.isna().all()):
        results["sum"] = np.nansum(data)
        results["std"] = np.nanstd(data)
        results["mean"] = np.mean(data)
    # Add Mean here

    if key_suffix is not None:
        results = {key_suffix + "+" + k: v for k, v in results.items()}

    return results


def get_all_eye_movement_stats(data: pd.DataFrame, key_suffix: str = None, epoch_width: int = 60) -> pd.DataFrame:
    """
    Function defining the statistical measures considered for aggregation
    :return: (pd.DataFrame) data of aggregated featues with column 'num_samples'
    """
    results = {
        "max_occurrences": np.nan,
    }

    if (len(data) > 0) and (not data.isna().all()):
        # Get the eye movement type with the maximum number of occurrences in this epoch
        d = defaultdict(int)
        for i in data:
            d[i] += 1
        result = max(d.items(), key=lambda x: x[1])
        results["max_occurrences"] = result[0]

    if key_suffix is not None:
        results = {key_suffix + "+" + k: v for k, v in results.items()}

    return results


def got_binary_event_stats(
    data: pd.DataFrame, target_zone_names: list[str], key_suffix: str = None, epoch_width: int = 60
) -> pd.DataFrame:
    """
    Function defining the statistical measures considered for aggregation
    :return: (pd.DataFrame) data of aggregated featues with column 'num_samples'
    """
    results = {
        'duration': np.nan,
        'frequency_event_time': np.nan,
        'frequency_event_samples': np.nan,
        'frequency_sample': np.nan,
        'percentage_time': np.nan,
        'percentage_events': np.nan,
        'ratio_sample_events': np.nan,
        'amplitude': np.nan,
        'event_count': np.nan,
    }

    if len(data) > 0:
        data = data.copy()

        total_length = (data.index[-1] - data.index[0]).total_seconds()
        number_window_samples = len(data)
        number_events_samples = len(data[data[key_suffix] == 1])
        number_all_type_events = (data['event+eye_movement_type+eventspec'].diff().fillna(0) != 0.0).sum()


        # Calculate durations per event and the target zone of the event
        duration_events_list = []
        target_zones_events = []
        amplitudes_event_list = []
        ix = (data[key_suffix] * 1.0).diff().fillna(0)
        if (data[key_suffix] * 1.0).iloc[0] == 1.0:
            ix.iloc[0] = 1
        if (data[key_suffix] * 1.0).iloc[-1] == 1.0:
            ix.iloc[-1] = -1
        if -1.0 in ix.unique():
            event_times = list(zip(data.index[ix == 1], data.index[ix == -1]))
            for event_time in event_times:
                duration_events_list.append(
                    (
                        event_time[1] - event_time[0] - datetime.timedelta(seconds=0.02)
                    ).total_seconds()
                )
                target_zones_events.append(data.loc[event_time[0]]["aoi+target_zone+"])
                amplitudes_event_list.append(
                    np.sum(np.abs(data.loc[event_time[0]:event_time[1]]['gaze+angle_change+velocity'].to_numpy())))


        # New array grouped to target zones
        duration_target_zone = np.column_stack(
            (duration_events_list, target_zones_events)
        )

        group = defaultdict(list)
        for name, url in duration_target_zone:
            group[url].append(name)


        # Calculate average duration, frequency and percentage of the eye movement type
        if not duration_events_list:
            duration_events_list.append(0)
        if not amplitudes_event_list:
            amplitudes_event_list.append(0)


        total_duration_events = np.sum(duration_events_list)
        total_amplitude_events = np.sum(amplitudes_event_list)
        number_key_suffix_events = len([k for k, _ in groupby((data[key_suffix] * 1.0)) if k == 1])

        results['event_count'] = number_key_suffix_events

        if number_key_suffix_events > 0:
            results["duration"] = total_duration_events / number_key_suffix_events
            results['amplitude'] = total_amplitude_events / number_key_suffix_events
        else:
            results["duration"] = 0
            results['amplitude'] = 0

        if total_length > 0:
            results['frequency_event_time'] = number_key_suffix_events / total_length
            results['percentage_time'] = total_duration_events / total_length

        else:
            results['frequency_event_time'] = 0
            results['percentage_time'] = 0
        
        if number_window_samples > 0:
            results['frequency_event_samples'] = number_key_suffix_events / number_window_samples
            results['frequency_sample'] = number_events_samples / number_window_samples
        else:
            results['frequency_event_samples'] = 0
            results['frequency_sample'] = 0

        if number_all_type_events > 0:
            results['percentage_events'] = number_key_suffix_events / number_all_type_events
            results['ratio_sample_events'] = number_events_samples / number_all_type_events
        else:
            results['percentage_events'] = 0
            results['ratio_sample_events'] = 0

    if key_suffix is not None:
            results = {key_suffix + "+" + k: v for k, v in results.items()}

    return results

def get_target_zone_stats(data, target_zone_names, key_suffix: str = None, epoch_width: int = 60):
    """
    Function defining the statistical measures considered for aggregation
    :return: (pd.DataFrame) data of aggregated featues with column 'num_samples'
    """
    results = {}

    if len(data) > 0:
        data = data.copy()

        # Calculate the statistics of the entire window
        number_all_regional_events_fixations = 0
        for region_number in target_zone_names:
            number_all_regional_events_fixations = number_all_regional_events_fixations + \
                                                   len([k for k, _ in groupby((data["aoi+target_zone+"] == region_number) &
                                                                              (data['event+FIXA+onehot'] == 1.0)) if k == 1])

        temp_helper_array = []
        for region_number in target_zone_names:

            # Calculate durations of target zone event, considering all the events (and not only the ones of fixations)
            duration_events_list_all = []
            ix_all = ((data["aoi+target_zone+"] == region_number)*1).diff().fillna(0)
            if (data["aoi+target_zone+"] == region_number).iloc[0] == 1.0:
                ix_all.iloc[0] = 1
            if (data["aoi+target_zone+"] == region_number).iloc[-1] == 1.0:
                ix_all.iloc[-1] = -1
            if -1.0 in ix_all.unique():
                event_times = list(zip(data.index[ix_all == 1], data.index[ix_all == -1]))
                for event_time in event_times:
                    duration_events_list_all.append(
                        (event_time[1] - event_time[0] - datetime.timedelta(seconds=0.02)).total_seconds())

            if not duration_events_list_all:
                duration_events_list_all.append(0)
            total_duration_events_all = np.sum(duration_events_list_all)
            number_region_events_all = len([k for k, _ in groupby(data["aoi+target_zone+"] == region_number) if k == 1])

            duration_name = 'aoi+duration_all+' + str(target_zone_names[region_number] + "+")
            if number_region_events_all > 0:
                results[duration_name] = total_duration_events_all / number_region_events_all
            else:
                results[duration_name] = 0

            # Calculate other statistics, by using all the samples (and not only the ones of fixations)
            number_region_samples_all = len(data[data["aoi+target_zone+"] == region_number])
            number_total_window_samples = len(data)

            sample_frequency_name_all = 'aoi+region_sample_frequency_all+' + str(target_zone_names[region_number] + "+")
            if number_total_window_samples > 0:
                results[sample_frequency_name_all] = number_region_samples_all / number_total_window_samples
            else:
                results[sample_frequency_name_all] = 0

            # Calculate durations of target zone event, considering only the ones belonging to fixations
            duration_events_list_fixations = []
            ix_fixations = (((data["aoi+target_zone+"] == region_number) &
                             (data['event+FIXA+onehot'] == 1.0)) * 1).diff().fillna(0)
            if ((data["aoi+target_zone+"] == region_number) & (data['event+FIXA+onehot'] == 1.0)).iloc[0] == 1.0:
                ix_fixations.iloc[0] = 1
            if ((data["aoi+target_zone+"] == region_number) & (data['event+FIXA+onehot'] == 1.0)).iloc[-1] == 1.0:
                ix_fixations.iloc[-1] = -1
            if -1.0 in ix_fixations.unique():
                event_times = list(zip(data.index[ix_fixations == 1], data.index[ix_fixations == -1]))
                for event_time in event_times:
                    duration_events_list_fixations.append(
                        (event_time[1] - event_time[0] - datetime.timedelta(seconds=0.02)).total_seconds())

            # Calculate average duration, frequency and percentage of the eye movement type
            if not duration_events_list_fixations:
                duration_events_list_fixations.append(0)
            total_duration_events_fixations = np.sum(duration_events_list_fixations)
            number_region_events_fixations = len([k for k, _ in groupby((data["aoi+target_zone+"] == region_number) &
                                                                        (data['event+FIXA+onehot'] == 1.0)) if k == 1])

            duration_name = 'aoi+duration_fixations+' + str(target_zone_names[region_number] + "+")
            if number_region_events_fixations > 0:
                results[duration_name] = total_duration_events_fixations / number_region_events_fixations
            else:
                results[duration_name] = 0

            # Calculate the region sample frequency, by using only the fixations samples
            number_region_samples_fixations = len(data[(data["aoi+target_zone+"] == region_number) &
                                                       (data['event+FIXA+onehot'] == 1)])
            sample_frequency_name_fixations = 'aoi+region_sample_frequency_fixations+' + \
                                              str(target_zone_names[region_number] + "+")
            if number_total_window_samples > 0:
                results[sample_frequency_name_fixations] = number_region_samples_fixations / number_total_window_samples
            else:
                results[sample_frequency_name_fixations] = 0

            # Calculate the regional gaze event percentage, by using only the fixations
            gaze_event_percentage = 'aoi+gaze_event_percentage+' + str(target_zone_names[region_number] + "+")
            if number_all_regional_events_fixations > 0:
                results[gaze_event_percentage] = number_region_events_fixations / number_all_regional_events_fixations
            else:
                results[gaze_event_percentage] = 0
    return results

def get_eventspec_stats(data, target_zone_names, key_suffix: str = None, epoch_width: int = 60):
    results = {}

    eye_categorization = {
        0: "FIXA",
        1: "PURS",
        2: "SACC",
        3: "ISAC",
        4: "MISSING",
        5: "HPSO",
        6: "IHPS",
        7: "ILPS",
        8: "LPSO",
    }

    eye_moment_type = data["event+eye_movement_type+eventspec"]
    eye_moment_type = eye_moment_type.replace(eye_categorization)

    metric_name = "_".join(key_suffix.split("+")[1].split("_")[-2:])

    if len(data) > 0:
        for movement_type in ["FIXA", "PURS", "SACC", "ISAC", "MISSING", "HPSO", "IHPS", "ILPS","LPSO"]:
            relevant_values = data[key_suffix][eye_moment_type == movement_type]
            # drop repeated values
            filtered_values = relevant_values[relevant_values.diff().ne(0)]
            movement_type_dict = get_stats(filtered_values,
                                           ("event+" + movement_type + "+" + metric_name))

            for key, value in movement_type_dict.items():
                if isinstance(value, float) and math.isnan(value):
                    movement_type_dict[key] = 0

            keys_to_remove = [key for key in movement_type_dict if "agg+num_samples" in key]
            for key in keys_to_remove:
                del movement_type_dict[key]
                
            results.update(movement_type_dict)

    return results


