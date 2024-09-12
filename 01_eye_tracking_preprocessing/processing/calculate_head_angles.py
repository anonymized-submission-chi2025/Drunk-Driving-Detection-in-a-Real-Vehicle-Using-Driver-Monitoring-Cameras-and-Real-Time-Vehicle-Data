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

import numpy as np
import pandas as pd
from scipy.spatial.transform import Rotation as R
from read_in_cam2world import read_in_cam2world


def get_head_rotation_matrix(data):
    qxx = data['face_quat_x'][0] * data['face_quat_x'][0]
    qyy = data['face_quat_y'][0] * data['face_quat_y'][0]
    qzz = data['face_quat_z'][0] * data['face_quat_z'][0]
    qww = data['face_quat_w'][0] * data['face_quat_w'][0]

    qxy = data['face_quat_x'][0] * data['face_quat_y'][0]
    qxz = data['face_quat_x'][0] * data['face_quat_z'][0]
    qyz = data['face_quat_y'][0] * data['face_quat_z'][0]

    qwx = data['face_quat_w'][0] * data['face_quat_x'][0]
    qwy = data['face_quat_w'][0] * data['face_quat_y'][0]
    qwz = data['face_quat_w'][0] * data['face_quat_z'][0]

    matrix = np.array([qww + qxx - qyy - qzz,
                       2 * (qxy - qwz),
                       2 * (qxz + qwy),
                       2 * (qxy + qwz),
                       qww - qxx + qyy - qzz,
                       2 * (qyz - qwx),
                       2 * (qxz - qwy),
                       2 * (qyz + qwx),
                       qww - qxx - qyy + qzz])

    return matrix


def calculate_head_angles():
    data = pd.DataFrame({'face_quat_w': [0.299454, 0.288757, 0.7660444, 0.123669, 0.309366],
                         'face_quat_x': [0.899953, 0.849437, 0, 0.904928, 0.909348],
                         'face_quat_y': [-0.019242, -0.092895, 0.6427876, 0.133506, 0.115058],
                         'face_quat_z': [-0.316293, -0.431795, 0, 0.384690, 0.253261]})

    quaternions = np.array(
        [data['face_quat_x'], data['face_quat_y'], data['face_quat_z'], data['face_quat_w']]).transpose()
    print(quaternions)
    r = R.from_quat(quaternions)
    #print(r.as_matrix())
    print(r.magnitude())
    print(r.as_euler('xyz', degrees=True))

    cam2world = read_in_cam2world('../../Data/field_study/212')
    cam2world_rot = cam2world[:3, :3]
    print(cam2world_rot)

    head_WCS_rot = cam2world_rot @ r.as_matrix()

    print('head_WCS_rot')
    print(head_WCS_rot)
    r_new = R.from_matrix(head_WCS_rot)
    print(r_new.as_euler('zxy', degrees=True))



calculate_head_angles()
