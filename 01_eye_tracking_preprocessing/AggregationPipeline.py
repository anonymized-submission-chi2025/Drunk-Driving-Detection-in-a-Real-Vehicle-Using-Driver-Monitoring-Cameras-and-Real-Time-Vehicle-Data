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
import os
import pandas as pd
import copy
import pyarrow
import datetime
from functools import partial
from timeit import default_timer as timer
import matplotlib.pyplot as plt
import numpy as np

from joblib import Parallel, delayed

from aggregation.aggregation_helper import interpolate_data, scale_data
from aggregation.crop_data_aggregation import crop_data_aggregation
from aggregation.add_phase_scenario_columns import add_phase_scenario_columns
from processing.target_zones import get_target_zone_names
from aggregation.fct_eye_utils import get_features
from utils.load_data import load_data
from aggregation.load_config import load_config, AggregationConfig

from aggregation.load_config import load_config


frequencies = pd.DataFrame(columns=[0.05, 0.25, 0.5, 0.75, 0.95])

class AggregationPipeline:
    def __init__(self, config_file: str) -> None:
        # Load basic configs from .yaml file
        self.config = load_config(config_file)

    def save_one_participant_csv_safely(self, aggregation_size: int, proband_id: str):
        try:
            data_agg = self.save_one_participant_csv(
                aggregation_size, proband_id)
            return data_agg
        except Exception as e:
            print(proband_id)
            print(f"Exception occurred: {e}")

    def save_one_participant_csv(self, aggregation_size: int, proband_id: str):

        config = copy.deepcopy(self.config)
        print('----------------------------------------')
        print('Proband: ', proband_id)

        directory_save = os.path.join(config.data_directory_processed, proband_id, 'ircam/')

        filename = os.path.join(
            directory_save, f"{proband_id}_{str(aggregation_size)}.pkl")
        file_exists_already = os.path.exists(filename)

        if (not config.enforce_recalculation) and file_exists_already:
            print(f"The files for participant {proband_id} will be reloaded.")
            data_agg = pd.read_pickle(filename)
            return data_agg

        # Load data from processed files
        directory_processed = config.data_directory_processed

        data, data_phases, data_phases_pkl = load_data(
            directory_processed, proband_id, 'aggregation', config)

        # Interpolate data to constant frequency
        # ensure all eye movement are present in the data (might not always be the case if, e.g., a IHPS was never detected
        eye_movement_binary = ['event+FIXA+onehot', 'event+HPSO+onehot',
                               'event+IHPS+onehot', 'event+ILPS+onehot',
                               'event+ISAC+onehot', 'event+LPSO+onehot',
                               'event+MISSING+onehot', 'event+PURS+onehot',
                               'event+SACC+onehot']
        for x in eye_movement_binary:
            if x not in data.columns:
                data[x] = 0

        data = interpolate_data(data, config.binary_features)

        # Crop data for faster aggregation
        data = crop_data_aggregation(
            data, data_phases, data_phases_pkl, config.selected_phases, config.selected_scenarios, 0)
        
        # Scale features with standard scaler for relevant columns
        # data = scale_data(data)

        # Get target zone names for proper naming of the columns
        target_zone_data = get_target_zone_names()
        target_zone_names = {}
        for target_zone in target_zone_data:
            target_zone_names.update(
                {target_zone: target_zone_data[target_zone]['name']})
        # print(data.isna().mean() * 100)
        # for index, value in (data.isna().mean() * 100).items():
            # print(f"Index: {index}, Value: {value}")
        # print(data)
        # Calculate statistical aggregation features

        # For faster testing only

        '''
        numerical_features = ['mideye_origin_x']
        binary_features = []
        single_eye_movement_features = []
        data = data[5000:20000]
        '''

        data_agg = get_features(data, epoch_width=aggregation_size, step_size=config.step_size,
                                numerical_features=config.numerical_features, binary_features=config.binary_features,
                                single_eye_movement_features=config.single_eye_movement_features,
                                all_eye_movement_features='event+eye_movement_type+eventspec',
                                target_zone_names=target_zone_names)

        # Crop data such that only valid sliding windows remain by taking into account the epoch width
        data_agg = crop_data_aggregation(data_agg, data_phases, data_phases_pkl,
                                         config.selected_phases, config.selected_scenarios, 0)

        # Reorder columns that num_samples is at first position
        data_agg = data_agg[['agg+num_samples+not_nan+'] +
                            [c for c in data_agg.columns if c != 'agg+num_samples+not_nan+']]
        data_agg = data_agg[['agg+num_samples++'] +
                            [c for c in data_agg.columns if c != 'agg+num_samples++']]

        # Add phase, scenario and variant columns
        data_agg = add_phase_scenario_columns(
            data_agg, data_phases, config.selected_phases)

        # Defragment the data frame
        data_agg = data_agg.copy()

        # Sets the target blood alocohl concentration.
        blood_biometrics = ['groundtruth+BAC+']

        # need to take the BG value at the end of each timeframe --> add timedelta
        # TODO: this shifts the data_agg index, why?
        target_index = data_agg.index + \
            datetime.timedelta(seconds=aggregation_size)
        data_agg[blood_biometrics] = data[blood_biometrics].reindex(data.index.union(
            target_index)).interpolate(method='time').loc[target_index].values

        # Move bg levels, phase, scenario, variant and id to the first columns

        columns_to_move = ['groundtruth+id++', 'groundtruth+variant++', 'groundtruth+scenario++', 'groundtruth+phase++'] + blood_biometrics
        data_agg['groundtruth+id++'] = proband_id
        data_agg = data_agg[columns_to_move +
                            [c for c in data_agg.columns if c not in columns_to_move]]
        data_agg.rename(columns={'groundtruth+BAC+': 'groundtruth+BAC++'}, inplace=True)

        # Neglect samples where less than 1/3 of frames were present
        data_considered = data_agg['agg+num_samples++'] > aggregation_size * \
            1 / 3 * config.framerate
        data_agg['agg+proportion_num_samples++'] = data_agg['agg+num_samples++'] / \
            (aggregation_size * config.framerate)
        # print('Considered ', data_considered.sum(), 'out of ', len(data_considered))
        # data_agg = data_agg[data_considered]

        # TODO: Some values are in float64 instead of Float64. Find the reason why the following is needed.
        def standardize_to_pandas_float(df):
            for column in df.columns:
                if pd.api.types.is_float_dtype(df[column]):
                    df[column] = df[column].astype('Float64')
            return df

        data_agg = standardize_to_pandas_float(data_agg)

        # Save data to parquet file
        data_agg.convert_dtypes().to_parquet(directory_save + proband_id +
                                             '_' + str(aggregation_size) + '.parquet')
        data_agg.to_pickle(directory_save + proband_id +
                           '_' + str(aggregation_size) + '.pkl')

        return data_agg

    def save_all_participants_csv(self, data_agg_all, directory_data, epoch_width, selected_phases):
        print('----------------------------------------')
        print('----------------------------------------')
        print('Summarizing all probands')
        print('Number of probands: ' + str(len(data_agg_all)))

        # Concat list of all probands to one dataframe.
        data_agg_all = pd.concat(data_agg_all)
        data_agg_all.sort_index(inplace=True)

        # Create the destination directory if it does not exist.
        directory_path = os.path.join(directory_data, 'ircam')
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        # Save as csv for all participants.
        directory_save = os.path.join(directory_path, f"all_probands_{str(epoch_width)}.parquet")
        data_agg_all.to_parquet(directory_save)
        print('Saved in: ', directory_save)

        return

    def run(self) -> pd.DataFrame:
        # Main function

        # Define directories
        directory_processed = self.config.data_directory_processed

        proband_ids = [proband_id for proband_id in os.listdir(
            directory_processed) if not proband_id.startswith('.') and proband_id[-3:] in self.config.probands_selected]

        for aggregation_size in self.config.aggregation_sizes:
            start_time = timer()

            if self.config.multi_cores is False or len(proband_ids) == 1:
                print("Not using multiple cores")
                data_agg_all = []
                for proband_id in proband_ids:
                    data_agg_all.append(self.save_one_participant_csv(
                        aggregation_size, str(proband_id)))
                self.save_all_participants_csv(
                    data_agg_all, self.config.data_directory_processed, aggregation_size, self.config.selected_phases)
            elif self.config.multi_cores is True:
                print("Using multiple cores")
                with Parallel(n_jobs=min(19, len(proband_ids)), verbose=101, backend='multiprocessing') as parallel:
                    data_agg_all = parallel(delayed(self.save_one_participant_csv_safely)(
                        aggregation_size, str(proband_id)) for proband_id in proband_ids)

                self.save_all_participants_csv(
                    data_agg_all, self.config.data_directory_processed, aggregation_size, self.config.selected_phases)
            else:
                print('Error with multi_cores setting in script!')
                exit()

            end_time = timer()
            process_time = end_time - start_time
            print(
                f'Finished with epoch width {aggregation_size}s in {process_time} seconds.')

        return data_agg_all
