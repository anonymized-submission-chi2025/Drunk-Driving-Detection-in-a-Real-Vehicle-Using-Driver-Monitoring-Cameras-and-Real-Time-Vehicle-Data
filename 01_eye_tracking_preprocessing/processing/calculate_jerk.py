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
def calculate_jerk(data):
    window_width = 1
    step = int(np.ceil(float(window_width) / 2))

    jerk_list = []
    jerk_r_list = []
    jerk_azimuth_list = []
    jerk_elevation_list = []
    jerk_azimuth_elevation_list = []

    jerk_roll_list = []
    jerk_pitch_list = []
    jerk_yaw_list = []
    jerk_head_list = []

    jerk_mideye_origin = []
    jerk_mideye_origin_x = []
    jerk_mideye_origin_y = []
    jerk_mideye_origin_z = []

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

        # Invalid intervals; first jerk of each sequence is set to 0
        if start_pos == end_pos:
            jerk_list.append(0)
            jerk_r_list.append(0)
            jerk_azimuth_list.append(0)
            jerk_elevation_list.append(0)
            jerk_azimuth_elevation_list.append(0)
            jerk_roll_list.append(0)
            jerk_pitch_list.append(0)
            jerk_yaw_list.append(0)
            jerk_head_list.append(0)
            jerk_mideye_origin.append(0)
            jerk_mideye_origin_x.append(0)
            jerk_mideye_origin_y.append(0)
            jerk_mideye_origin_z.append(0)

            continue

        # Calculate derivatives
        time = (data.index[end_pos] - data.index[start_pos]).total_seconds()
        jerk_azimuth = (data['acceleration_azimuth'].iloc[end_pos] - data['acceleration_azimuth'].iloc[start_pos]) / time
        jerk_elevation = (data['acceleration_elevation'].iloc[end_pos] - data['acceleration_elevation'].iloc[start_pos]) / time

        # Jerk of head rotation
        jerk_roll_list.append((data['acceleration_roll'].iloc[end_pos] - data['acceleration_roll'].iloc[start_pos]) / time)
        jerk_pitch_list.append((data['acceleration_pitch'].iloc[end_pos] - data['acceleration_pitch'].iloc[start_pos]) / time)
        jerk_yaw_list.append((data['acceleration_yaw'].iloc[end_pos] - data['acceleration_yaw'].iloc[start_pos]) / time)
        jerk_head_list.append((data['acceleration_head'].iloc[end_pos] - data['acceleration_head'].iloc[start_pos]) / time)

        # Jerk of mid eye origin
        jerk_mideye_origin.append(
            (data['acceleration_mideye_origin'].iloc[end_pos] - data['acceleration_mideye_origin'].iloc[start_pos]) / time)
        jerk_mideye_origin_x.append(
            (data['acceleration_mideye_origin_x'].iloc[end_pos] - data['acceleration_mideye_origin_x'].iloc[start_pos]) / time)
        jerk_mideye_origin_y.append(
            (data['acceleration_mideye_origin_y'].iloc[end_pos] - data['acceleration_mideye_origin_y'].iloc[start_pos]) / time)
        jerk_mideye_origin_z.append(
            (data['acceleration_mideye_origin_z'].iloc[end_pos] - data['acceleration_mideye_origin_z'].iloc[start_pos]) / time)

        # Calculate jerks in different directions
        jerk_r_direction = -(data['acceleration_elevation'].iloc[i] ** 2) - (data['acceleration_azimuth'].iloc[i] ** 2) * (
                np.cos(data['elevation'].iloc[i]) ** 2)
        jerk_azimuth_direction = jerk_azimuth * np.cos(data['elevation'].iloc[i]) - 2 * data[
            'acceleration_elevation'].iloc[i] * data['acceleration_azimuth'].iloc[i] * np.sin(data['elevation'].iloc[i])
        jerk_elevation_direction = jerk_elevation + (data['acceleration_azimuth'].iloc[i] ** 2) * np.sin(
            data['elevation'].iloc[i]) * np.cos(data['elevation'].iloc[i])

        # Append jerks to lists
        jerk_list.append(np.linalg.norm(
            np.array([jerk_r_direction, jerk_azimuth_direction, jerk_elevation_direction])))
        #jerk_r_list.append(np.linalg.norm(jerk_r_direction))
        jerk_r_list.append(jerk_r_direction)
        jerk_azimuth_list.append(jerk_azimuth_direction)
        jerk_elevation_list.append(jerk_elevation_direction)
        jerk_azimuth_elevation_list.append(np.linalg.norm(
            np.array([0, jerk_azimuth_direction, jerk_elevation_direction])))

    data['jerk'] = np.array(jerk_list)
    data['jerk_r'] = np.array(jerk_r_list)
    data['jerk_azimuth'] = np.array(jerk_azimuth_list)
    data['jerk_elevation'] = np.array(jerk_elevation_list)
    data['jerk_azimuth_elevation'] = np.array(jerk_azimuth_elevation_list)

    data['jerk_roll'] = np.array(jerk_roll_list)
    data['jerk_pitch'] = np.array(jerk_pitch_list)
    data['jerk_yaw'] = np.array(jerk_yaw_list)
    data['jerk_head'] = np.array(jerk_head_list)

    data['jerk_mideye_origin'] = np.array(jerk_mideye_origin)
    data['jerk_mideye_origin_x'] = np.array(jerk_mideye_origin_x)
    data['jerk_mideye_origin_y'] = np.array(jerk_mideye_origin_y)
    data['jerk_mideye_origin_z'] = np.array(jerk_mideye_origin_z)



    return data
