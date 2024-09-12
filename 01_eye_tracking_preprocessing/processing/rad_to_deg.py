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

columns = [
    "azimuth",
    "elevation",
    "velocity",
    "velocity_azimuth",
    "velocity_elevation",
    "angle_change",
    "angle_change_azimuth",
    "angle_change_elevation",
    "direction",
    "acceleration",
    "acceleration_r",
    "acceleration_azimuth",
    "acceleration_elevation",
    "acceleration_azimuth_elevation",
    "jerk",
    "jerk_r",
    "jerk_azimuth",
    "jerk_elevation",
    "jerk_azimuth_elevation",
    "snap",
    "snap_r",
    "snap_azimuth",
    "snap_elevation",
    "snap_azimuth_elevation",
    "roll",
    "pitch",
    "yaw",
    "velocity_roll",
    "velocity_pitch",
    "velocity_yaw",
    "acceleration_roll",
    "acceleration_pitch",
    "acceleration_yaw",
    "jerk_roll",
    "jerk_pitch",
    "jerk_yaw",
    "snap_roll",
    "snap_pitch",
    "snap_yaw",
]


def rad_to_deg(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data[columns] = data[columns].apply(np.rad2deg)
    return data
