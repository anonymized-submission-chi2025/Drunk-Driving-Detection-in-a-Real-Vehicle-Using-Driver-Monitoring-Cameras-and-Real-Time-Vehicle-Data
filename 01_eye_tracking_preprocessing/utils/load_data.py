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

import os
from typing import Tuple
import pandas as pd
import pickle
from typing import Union
from aggregation.load_config import AggregationConfig


def process_data(data: pd.DataFrame, config: AggregationConfig) \
        -> pd.DataFrame:

    new_features = []

    for numerical_feature in config.numerical_features:
        #data[(numerical_feature + "_abs")] = data[numerical_feature].abs()
        new_features.append(numerical_feature + "_abs")
        new_column = pd.DataFrame({numerical_feature + "_abs": data[numerical_feature].abs()})
        data = pd.concat([data, new_column], axis=1)

    config.numerical_features.extend(new_features)


    return data


def add_microseconds_to_datetime(dt_str):
    """
    Adds microseconds to datetime object in string format.
    """
    if not isinstance(dt_str, str):
        return dt_str
    # If microseconds are not present in the datetime string
    if '.' not in dt_str:
        # Add '.000000' to the datetime string
        dt_str = dt_str.replace('+', '.000000+')
    return dt_str

# The return types of the load_data function
DF = pd.DataFrame
AggregationReturnType = Tuple[DF, DF, DF]
VisualizationReturnType = Tuple[DF, DF, DF, DF, DF, DF]

def load_data(
    base_directory: str, folder: str, caller, config:AggregationConfig
) -> Union[VisualizationReturnType, AggregationReturnType, None]:

    directory_saved = os.path.join(base_directory, folder, "ircam")
    
    data = pd.read_pickle(os.path.join(directory_saved, folder + ".pkl"))

    data = process_data(data, config)

    data_phases = pd.read_csv(
        os.path.join(directory_saved, f"phases_{folder}.csv"), sep=","
    )
    data_phases_pkl = pd.read_pickle(
        os.path.join(directory_saved, f"phases_{folder}.pkl")
    )

    data_phases = data_phases.loc[:, ~data_phases.columns.str.contains("^Unnamed")]

    # Some start/end times do not exactly follow the format %Y-%m-%d %H:%M:%S.%f%z, where .%f is missing.
    # Therefore, add the zeros after the comma if missing to avoid the  time format confusion when calling to_datetime.
    data_phases['start'] = data_phases['start'].apply(add_microseconds_to_datetime)
    data_phases['end'] = data_phases['end'].apply(add_microseconds_to_datetime)

    data_phases["start"] = pd.to_datetime(data_phases["start"])
    if "last_start_pass" in data_phases.columns:
        data_phases["end"] = pd.to_datetime(data_phases["last_start_pass"])
        data_phases.drop(columns=["last_start_pass"], inplace=True)
    else:
        data_phases["end"] = pd.to_datetime(data_phases["end"], format='ISO8601')

    if caller == "visualization":
        with open(os.path.join(directory_saved, "selected_phases.pckl"), "rb") as f:
            selected_phases = pickle.load(f)
        with open(os.path.join(directory_saved, "selected_scenarios.pckl"), "rb") as f:
            selected_scenarios = pickle.load(f)
        with open(
            os.path.join(directory_saved, "selected_phase_times.pckl"), "rb"
        ) as f:
            selected_phase_times = pickle.load(f)
        with open(
            os.path.join(directory_saved, "selected_scenario_times.pckl"), "rb"
        ) as f:
            selected_scenario_times = pickle.load(f)

        return (
            data,
            data_phases,
            selected_phases,
            selected_scenarios,
            selected_phase_times,
            selected_scenario_times,
        )

    elif caller == "aggregation":
        return data, data_phases, data_phases_pkl

    else:
        print(
            "Wrong caller argument to load data. Give correct caller type [visualization, aggregation]."
        )
        return
