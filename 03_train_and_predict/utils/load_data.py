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

import pandas as pd
import os


def load_data(config: dict[str, any]) -> tuple[pd.DataFrame, list[str]]:
    core_features = []

    if config["use_dmc"]:
        core_features = core_features + config["dmc_features"]

        if config["only_load_core_features"]:
            columns_to_load = (['groundtruth+id++', 'groundtruth+variant++',
                              'groundtruth+scenario++', 'groundtruth+phase++',
                              'groundtruth+BAC++' ] + config["dmc_features"])
            if 'agg+proportion_num_samples++' not in columns_to_load:
                columns_to_load.append('agg+proportion_num_samples++')
        else:
            columns_to_load = None

        data_path = os.path.join(
            config["data_directory"], 'ircam/all_probands_'
                                      + str(config["window_length"]) + '.parquet')
        data_et = pd.read_parquet(data_path,
            columns=columns_to_load)

        if not config["use_reference"]:
            reference_index = data_et["groundtruth+id++"].isin(
                config["selected_participants"]["reference"])
            data_et = data_et[~reference_index]
        if not config["use_placebo"]:
            placebo_index = data_et["groundtruth+id++"].isin(
                config["selected_participants"]["placebo"])
            data_et = data_et[~placebo_index]
        
        # TODO: The following columns contain NaNs. Find the reason.
        cols_to_delete = ['misc+drowsinessTime_ms++skewness',
                          'misc+drowsinessTime_ms++kurtosis',
                          'misc+drowsinessTime_ms+_abs+kurtosis',
                          'misc+drowsinessTime_ms+_abs+skewness',
                          'misc+inattentionTime_ms++kurtosis',
                          'misc+inattentionTime_ms++skewness',
                          'misc+inattentionTime_ms+_abs+kurtosis']

        data_et = data_et.drop(columns=[col for col in cols_to_delete if col in data_et.columns])
        data_et = data_et.dropna()

        num_samples_ET_threshold = 0.75
        data_et = data_et[data_et['agg+proportion_num_samples++'] >= num_samples_ET_threshold]

        if config["verbose"]:
            print("Shape ET data", str(data_et.shape))

    if config["use_can"]:
        core_features = core_features + config["can_features"]

        if config["only_load_core_features"]:
            columns_to_load = (['groundtruth+id+CAN+', 'groundtruth+variant+CAN+',
                              'groundtruth+scenario+CAN+', 'groundtruth+phase+CAN+']
                               + config["can_features"])
            if 'agg+proportion_num_samples+CAN+' not in columns_to_load:
                columns_to_load.append('agg+proportion_num_samples+CAN+')
        else:
            columns_to_load = None

        can_data = pd.read_parquet(os.path.join(
            config["data_directory"], 'canlogger/aggregated_'
                                      + str(config["window_length"]).zfill(3) + '_freq-050.parquet'),
            columns=columns_to_load)

        can_data["groundtruth+id+CAN+"] = can_data["groundtruth+id+CAN+"].astype(str)

        if not config["use_reference"]:
            reference_index = can_data["groundtruth+id+CAN+"].isin(
                [s[6:] for s in config["selected_participants"]["reference"]])
            can_data = can_data[~reference_index]
        if not config["use_placebo"]:
            placebo_index = can_data["groundtruth+id+CAN+"].isin(
                [s[6:] for s in config["selected_participants"]["placebo"]])
            can_data = can_data[~placebo_index]

        num_samples_CAN_threshold = 0.75
        can_data = can_data[can_data['agg+proportion_num_samples+CAN+'] >= num_samples_CAN_threshold]

        if config["verbose"]:
            print("Shape CAN data", str(can_data.shape))

    # BAC only exists in CAN data.
    core_features = [value for value in core_features if value not in [
        'groundtruth+variant++', 'groundtruth+id++', 'groundtruth+phase++',
        'groundtruth+scenario++', 'groundtruth+BAC++', 'groundtruth+phase+CAN+',
        'groundtruth+scenario+CAN+', 'groundtruth+variant+CAN+', 'groundtruth+id+CAN+']]

    if config["use_can"] and config["use_dmc"]:
        merged_df = pd.merge(
            data_et, can_data, left_index=True, right_index=True, how='inner')

        if config["verbose"]:
            print(merged_df.shape)
        '''
        print((merged_df['phase'] == merged_df['groundtruth+phase++']).all())
        print((merged_df['scenario'] == merged_df['groundtruth+scenario++']).all()) #ok
        print((merged_df['scenario_number'] == merged_df['groundtruth+variant++']).all()) #ok
        print((("drive_" + merged_df['subject_id']) == merged_df['groundtruth+id++']).all())
        '''

        merged_df.drop('groundtruth+phase+CAN+', inplace=True, axis=1)
        merged_df.drop('groundtruth+scenario+CAN+', inplace=True, axis=1)
        merged_df.drop('groundtruth+variant+CAN+', inplace=True, axis=1)
        merged_df.drop('groundtruth+id+CAN+', inplace=True, axis=1)

        data = merged_df

    if (not config["use_can"]) and config["use_dmc"]:
        data = data_et

    if (not config["use_dmc"]) and config["use_can"]:
        can_data["groundtruth+variant++"] = can_data["groundtruth+variant+CAN+"]
        can_data["groundtruth+id++"] = can_data["groundtruth+id+CAN+"]
        can_data["groundtruth+phase++"] = can_data["groundtruth+phase+CAN+"]
        can_data["groundtruth+scenario++"] = can_data["groundtruth+scenario+CAN+"]
        can_data.drop('groundtruth+variant+CAN+', inplace=True, axis=1)
        can_data.drop('groundtruth+id+CAN+', inplace=True, axis=1)
        can_data.drop('groundtruth+phase+CAN+', inplace=True, axis=1)
        can_data.drop('groundtruth+scenario+CAN+', inplace=True, axis=1)
        data = can_data

        data["groundtruth+id++"] = "drive_" + data["groundtruth+id++"]

    # Delete participants that were not selected:
    participants_to_keep = (config["selected_participants"]["treatment"] +
                            config["selected_participants"]["reference"] +
                            config["selected_participants"]["placebo"])
    data = data.loc[data["groundtruth+id++"].isin(participants_to_keep)].copy()

    if config["verbose"]:
        print("Shape (combined) data", str(data.shape))

    match_state_phase = {1: 0, 2: 2, 3: 1}
    data['groundtruth+state++'] = data['groundtruth+phase++'].replace(match_state_phase)

    if config["verbose"]:
        print("Number of drivers:", len(data["groundtruth+id++"].unique()))
        print("Names of drivers:", data["groundtruth+id++"].unique())
        print("Number of scenarios:", len(data["groundtruth+scenario++"].unique()))
        print("Names of scenarios:", data["groundtruth+scenario++"].unique())
        # originally called scenario
        print("Number of phases:", len(data["groundtruth+phase++"].unique()))
        # originally called scenario
        print("Names of phases:", data["groundtruth+phase++"].unique())
        # originally called scenario # NEW
        print("Number of states:", len(data["groundtruth+state++"].unique()))
        # originally called scenario # NEW
        print("Names of states:", data["groundtruth+state++"].unique())

        print("Number of features: ", data.shape[1])

    data["y_EW"] = 0.0
    data["y_AL"] = 0.0
    index_pos_EW = ((data["groundtruth+id++"].isin(config["selected_participants"]["treatment"])) &
                    (data["groundtruth+state++"] > 0))
    index_pos_AL = ((data["groundtruth+id++"].isin(config["selected_participants"]["treatment"])) &
                    (data["groundtruth+state++"] == 2))
    data.loc[index_pos_EW, 'y_EW'] = 1.0
    data.loc[index_pos_AL, 'y_AL'] = 1.0

    return data, core_features
