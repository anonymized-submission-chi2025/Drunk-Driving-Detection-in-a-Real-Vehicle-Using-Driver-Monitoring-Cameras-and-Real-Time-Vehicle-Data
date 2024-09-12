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

""" canlogger_reader.py
Get raw data from each subject /study_day/canlogger/*_can.parquet
Raw data may have time jump at front, fix by helper.fix_the_timestamp()
Interpolate the data to 50 Hz, use the previous value to fill the missing data
Then save to /output/canlogger/can-all.parquet
can-all data is merged with scenario data, this is when make all ref data phase to 1 (is_ref=True)
Then save to /output/canlogger/can-scenario.parquet
"""

import glob
import os

import pandas as pd
from joblib import Parallel, delayed

from .helper import merge_with_scenario, fix_the_timestamp

from .can_fill_limits import FILL_LIMITS

def __fillna_with_limits(df, freq, method='ffill', bool_only=False):
    for col_name, col in df.items():
        if not bool_only or pd.api.types.is_bool_dtype(col):
            limit = FILL_LIMITS[col_name]
            if limit is not None:
                limit = int(limit / (1000 / freq))
            col.fillna(method=method, limit=limit, inplace=True)
            if pd.api.types.is_bool_dtype(col):
                col.fillna(value=False, inplace=True)
            elif pd.api.types.is_numeric_dtype(col):
                # print("fill column %s with 0" % col_name)
                col.fillna(value=0, inplace=True)

def resolve_duplicated_index(group):
    first = group.iloc[0]
    for idx in range(1, len(group)):
        row = group.iloc[idx]
        for col in group.columns:
            if pd.isnull(first[col]):
                first[col] = row[col]
    return first

def merge_duplicated_NaN(df):
    duplicates = df[df.index.duplicated(keep=False)]
    resolved = duplicates.groupby(duplicates.index).apply(resolve_duplicated_index)
    df = df.drop(duplicates.index)
    df = pd.concat([df, resolved])
    df.sort_index(inplace=True)
    return df

def process_canlogger_files(subject:int, data_folder: str, freq: int):
    data_path = os.path.join(data_folder, 'study_day/canlogger/*_can.parquet')
    print("data path", data_path)
    files = sorted(glob.glob(os.path.join(data_folder, 'study_day/canlogger/*_can.parquet')))
    files = list(filter(lambda f: os.path.getsize(f) > 0, files))

    print(f"Subject {subject}, {len(files)} files")

    print(f"{subject} read...", end='')

    def read_parquet(f):
        if os.path.getsize(f) == 0:
            print(f"Empty file {f}")
            return None
        df = pd.read_parquet(f)
        if len(df) <= 0:
            return None
        df['timestampMs'] = pd.to_datetime(df['timestampMs'], unit='ms', utc=True)
        # fix the time jump
        fix_the_timestamp(df, 'timestampMs')
        df.set_index('timestampMs', inplace=True)
        df.sort_index(inplace=True)
        df.index = df.index.tz_convert('Europe/Zurich')
        df.index.name = 'timestamp'
        df['url-name'] = df['url'] + '-' + df['name']
        df.set_index([df.index, 'url-name'], inplace=True)
        df = merge_duplicated_NaN(df)
        df = df[['valueDouble', 'valueString']].unstack()
        df.dropna(axis='columns', how='all', inplace=True)
        df.columns = df.columns.get_level_values(1)
        df.dropna(how='all', inplace=True)

        df = df.resample(f'{1000.0 / freq}ms').first()
        return df

    # concat all files
    df = pd.concat([read_parquet(f) for f in files if read_parquet(f) is not None])

    df.sort_index(inplace=True)
    df = merge_duplicated_NaN(df)

    # try to simplify column names where possible
    column_renames = {}
    for column in df.columns:
        if column.split('-')[0] == column.split('-')[1]:
            column_renames[column] = column.split('-')[0]
    df.rename(columns=column_renames, inplace=True)

    print(f"{subject} fillna...", end='')
    # ffill is the way to go since we only have data on change (this means once we have data for a channel, its value stays the same until we get it the next time)
    __fillna_with_limits(df, freq, method='ffill')

    # nans can now only be in the start of the df
    # Only use the important columns
    important_columns = ['VehicleSpeed', 'SteeringWheelAngle', 'SteeringWheelAngularVelocity', 'BrakingPressure', 'PedalForce', 'LongitudinalAcceleration', 'LateralAcceleration']
    nan_counts = df[important_columns].isna().sum()
    # delete rows with nans in the beginning
    rows_to_delete = nan_counts.max()
    df = df[rows_to_delete:]

    # now it's safe to backfill in the beginning
    # __fillna_with_limits(df, freq, method='bfill')

    df.dropna(how='all', inplace=True)

    print(f"{subject} convert...", end='')
    df = df.convert_dtypes()

    print(f"{subject} bool...", end='')
    # make datatype boolean whenever possible
    # add true/false to unique -> in case there is only one of T/F then we still can make a bool
    for column in df.columns:
        unique_vals = set(list(df[column].dropna().unique()))
        if unique_vals.issubset({'true', 'false'}):
            df[column] = df[column] == 'true'
        elif unique_vals.issubset({'True', 'False'}):
            df[column] = df[column] == 'True'
        # elif unique_vals.issubset({0, 1}):
        #    df[column] = df[column] == 1

    # fillna again now -> bools
    __fillna_with_limits(df, freq, method='ffill', bool_only=True)

    df['subject'] = subject
    print(f"Finished subject {subject}, shape {df.shape}")

    return df


def run_failsafe(fun, *args):
    try:
        return fun(*args)
    except Exception as e:
        print("Unexpected error:", e)
        import traceback
        print(traceback.format_exc())


def process_subject(subject, data_folder, data_output_directory, freq, is_ref=False, reusing=False, ref_phase_to=1):

    print("Processing subject", subject, data_output_directory)

    try:
        if reusing and os.path.exists(
                os.path.join(data_output_directory + f"/canlogger/can-all_freq-{freq:03d}.parquet")):
            print(f'Reusinging CAN data for subject {subject}')
            df = pd.read_parquet(data_output_directory + f"/canlogger/can-all_freq-{freq:03d}.parquet")
            reused = True
        else:
            df = run_failsafe(process_canlogger_files, subject, data_folder, freq)
            reused = False
        if df is not None:
 
            try:
                print("making dirs " + os.path.join(data_output_directory, "canlogger"))
                os.makedirs(os.path.join(data_output_directory, "canlogger"), exist_ok=True)
            except:
                pass

            if not reused:
                df.to_parquet(os.path.join(data_output_directory, f"canlogger/can-all_freq-{freq:03d}.parquet"))

            df = run_failsafe(merge_with_scenario, df, data_folder, is_ref, ref_phase_to)
            if df is not None:
                df.to_parquet(os.path.join(data_output_directory, f"canlogger/can-scenario_freq-{freq:03d}.parquet"))

            else:
                print("Empty scenario merged data for subject %s" % subject)

        else:
            print("Empty CAN data for subject %s" % subject)

    except Exception as e:
        print("Unexpected error:", e)
        import traceback
        print(traceback.format_exc())