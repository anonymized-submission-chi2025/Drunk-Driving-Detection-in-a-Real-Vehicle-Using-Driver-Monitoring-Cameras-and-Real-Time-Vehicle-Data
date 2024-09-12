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

import math
import numpy as np


# Window approach reused from
# src="https://github.com/MikhailStartsev/deep_em_classifier/blob/master/feature_extraction/arff_utils/GetAcceleration.m"
def calculate_snap(data):
    window_width = 1
    step = int(np.ceil(float(window_width) / 2))

    snap_list = []
    snap_r_list = []
    snap_azimuth_list = []
    snap_elevation_list = []
    snap_azimuth_elevation_list = []

    snap_roll_list = []
    snap_pitch_list = []
    snap_yaw_list = []
    snap_head_list = []

    snap_mideye_origin = []
    snap_mideye_origin_x = []
    snap_mideye_origin_y = []
    snap_mideye_origin_z = []


    for i in range(len(data)):
        # Get initial interval
        if step == window_width:
            start_pos = i - step
            end_pos = i
        else:
            start_pos = i - step
            end_pos = i + step

        # Fine tune intervals
        if start_pos < 0:
            start_pos = i

        if end_pos > len(data) - 1:
            end_pos = i

        # Invalid intervals; first snap of each sequence is set to 0
        if start_pos == end_pos:
            snap_list.append(0)
            snap_r_list.append(0)
            snap_azimuth_list.append(0)
            snap_elevation_list.append(0)
            snap_azimuth_elevation_list.append(0)
            snap_roll_list.append(0)
            snap_pitch_list.append(0)
            snap_yaw_list.append(0)
            snap_head_list.append(0)
            snap_mideye_origin.append(0)
            snap_mideye_origin_x.append(0)
            snap_mideye_origin_y.append(0)
            snap_mideye_origin_z.append(0)
            continue

        # Calculate derivatives
        time = (data.index[end_pos] - data.index[start_pos]).total_seconds()
        snap_azimuth = (data['jerk_azimuth'].iloc[end_pos] - data['jerk_azimuth'].iloc[start_pos]) / time
        snap_elevation = (data['jerk_elevation'].iloc[end_pos] - data['jerk_elevation'].iloc[start_pos]) / time

        # Snap of head rotation
        snap_roll_list.append((data['jerk_roll'].iloc[end_pos] - data['jerk_roll'].iloc[start_pos]) / time)
        snap_pitch_list.append((data['jerk_pitch'].iloc[end_pos] - data['jerk_pitch'].iloc[start_pos]) / time)
        snap_yaw_list.append((data['jerk_yaw'].iloc[end_pos] - data['jerk_yaw'].iloc[start_pos]) / time)
        snap_head_list.append((data['jerk_head'].iloc[end_pos] - data['jerk_head'].iloc[start_pos]) / time)

        # Snap of mid eye origin
        snap_mideye_origin.append(
            (data['jerk_mideye_origin'].iloc[end_pos] - data['jerk_mideye_origin'].iloc[start_pos]) / time)
        snap_mideye_origin_x.append(
            (data['jerk_mideye_origin_x'].iloc[end_pos] - data['jerk_mideye_origin_x'].iloc[start_pos]) / time)
        snap_mideye_origin_y.append(
            (data['jerk_mideye_origin_y'].iloc[end_pos] - data['jerk_mideye_origin_y'].iloc[start_pos]) / time)
        snap_mideye_origin_z.append(
            (data['jerk_mideye_origin_z'].iloc[end_pos] - data['jerk_mideye_origin_z'].iloc[start_pos]) / time)

        # Calculate snaps in different directions
        snap_r_direction = -(data['jerk_elevation'].iloc[i] ** 2) - (data['jerk_azimuth'].iloc[i] ** 2) * (
                np.cos(data['elevation'].iloc[i]) ** 2)
        snap_azimuth_direction = snap_azimuth * np.cos(data['elevation'].iloc[i]) - 2 * data[
            'jerk_elevation'].iloc[i] * data['jerk_azimuth'].iloc[i] * np.sin(data['elevation'].iloc[i])
        snap_elevation_direction = snap_elevation + (data['jerk_azimuth'].iloc[i] ** 2) * np.sin(
            data['elevation'].iloc[i]) * np.cos(data['elevation'].iloc[i])

        # Append snaps to lists
        snap_list.append(np.linalg.norm(
            np.array([snap_r_direction, snap_azimuth_direction, snap_elevation_direction])))
        #snap_r_list.append(np.linalg.norm(snap_r_direction))
        snap_r_list.append(snap_r_direction)
        snap_azimuth_list.append(snap_azimuth_direction)
        snap_elevation_list.append(snap_elevation_direction)
        snap_azimuth_elevation_list.append(np.linalg.norm(
            np.array([0, snap_azimuth_direction, snap_elevation_direction])))

    data['snap'] = np.array(snap_list)
    data['snap_r'] = np.array(snap_r_list)
    data['snap_azimuth'] = np.array(snap_azimuth_list)
    data['snap_elevation'] = np.array(snap_elevation_list)
    data['snap_azimuth_elevation'] = np.array(snap_azimuth_elevation_list)

    data['snap_roll'] = np.array(snap_roll_list)
    data['snap_pitch'] = np.array(snap_pitch_list)
    data['snap_yaw'] = np.array(snap_yaw_list)
    data['snap_head'] = np.array(snap_head_list)

    data['snap_mideye_origin'] = np.array(snap_mideye_origin)
    data['snap_mideye_origin_x'] = np.array(snap_mideye_origin_x)
    data['snap_mideye_origin_y'] = np.array(snap_mideye_origin_y)
    data['snap_mideye_origin_z'] = np.array(snap_mideye_origin_z)

    return data
