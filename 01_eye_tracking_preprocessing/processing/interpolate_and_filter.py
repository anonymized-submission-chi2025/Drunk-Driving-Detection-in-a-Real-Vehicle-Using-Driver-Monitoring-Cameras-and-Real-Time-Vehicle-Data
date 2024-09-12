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
import numpy as np
from scipy import signal, interpolate

def lowpass_filter(df: pd.DataFrame, freq=50.0, cutoff=20.0, order=1):

    def _butter_lowpass(cutoff, fs, order=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = signal.butter(
            order, normal_cutoff, btype="lowpass", analog=False, output="ba"
        )
        return b, a

    def butter_lowpass_filter(data, cutoff, fs, order=1):
        b, a = _butter_lowpass(cutoff, fs=fs, order=order)
        return signal.filtfilt(b, a, data, method="gust")

    for col in df.columns:
        y = df[col].values
        # interpolate nans with nearest
        y_interp = interpolate.interp1d(
            np.arange(len(y))[~np.isnan(y)],
            y[~np.isnan(y)],
            kind="nearest",
            fill_value="extrapolate",
            bounds_error=False,
        )(np.arange(len(y)))
        y_filtered = butter_lowpass_filter(y_interp, cutoff, freq, order)
        y_filtered[np.isnan(y)] = np.nan
        df.loc[:, col] = y_filtered
    return df


def interpolate_with_limit(df, limit, method="time"):
    """
    Interpolates sequences which are shorter than limit.
    e.g. limit=2 and df=[1, np.nan, np.nan, 4, np.nan, np.nan, np.nan, 8, np.nan] ->  [1, 2, 3, 4, np.nan, np.nan, np.nan, 8, np.nan]
    :param df:
    :param limit:
    :param method:
    :return:
    """
    df_interpolated = df.interpolate(method=method, limit_direction="both")
    for col in df:
        mask = df[col].isna()
        x = (
            mask.groupby((mask != mask.shift()).cumsum()).transform(
                lambda x: len(x) > limit
            )
            & mask
        )
        df_interpolated[col] = df_interpolated.loc[~x, col]

    return df_interpolated


"""
Interpolate fills in NaN values in the data using the panda interpolate function."""


def interpolate_and_filter(
    raw_data: pd.DataFrame, cutoff=20.0, order=1
) -> pd.DataFrame:
    non_float_cols = raw_data.select_dtypes(include="int").columns

    float_cols = raw_data.select_dtypes(include="float").columns

    raw_data = raw_data[raw_data["gaze_direction_confidence"] >= 0.01]



    frequency = 50.0
    target_index = pd.date_range(
        start=raw_data.index[0].floor("s"),
        end=raw_data.index[-1].ceil("s"),
        freq="%dus" % (1000000 / frequency),
    )  # microsecs
    raw_data = raw_data.reindex(
        index=raw_data.index.union(target_index).drop_duplicates()
    )


    raw_data.loc[:, float_cols] = raw_data.loc[:, float_cols].interpolate(
        method="time", limit=5, limit_direction="both"
    )
    raw_data.loc[:, non_float_cols] = raw_data.loc[:, non_float_cols].interpolate(
        method="nearest", limit=5, limit_direction="both"
    )
    raw_data = raw_data.reindex(target_index)

    orig_data = raw_data.copy()

    # ensure we have unit vectors again (numerical inaccuracies possible after filtering)
    gaze_direction_vector = ["gaze_direction_x", "gaze_direction_y", "gaze_direction_z"]
    raw_data[gaze_direction_vector] = raw_data[gaze_direction_vector].div(
        np.linalg.norm(raw_data[gaze_direction_vector], axis=1), axis=0
    )
    quat_vector = ["face_quat_x", "face_quat_y", "face_quat_z", "face_quat_w"]
    raw_data[quat_vector] = raw_data[quat_vector].div(
        np.linalg.norm(raw_data[quat_vector], axis=1), axis=0
    )

    return raw_data
