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

import warnings

import numpy as np


# src="https://gist.github.com/TimSC/8c25ca941d614bf48ebba6b473747d72.js"
def line_plane_collision(plane_normal, plane_point, ray_direction, ray_point, epsilon=1e-6):
    ndotu = plane_normal.dot(ray_direction)
    if abs(ndotu) < epsilon:
        warnings.warn(f"no intersection or line is within plane for {plane_normal} and {ray_direction}")
        return (np.nan, np.nan)
        #raise RuntimeError("no intersection or line is within plane")

    w = ray_point - plane_point
    si = -plane_normal.dot(w) / ndotu
    psi = w + si * ray_direction + plane_point
    return psi


# src="https://gist.github.com/TimSC/8c25ca941d614bf48ebba6b473747d72.js"
def intersection_plane(data, z_planes):
    for z_plane in z_planes:
        plane_normal = np.array([0, 0, 1])
        plane_point = np.array([0, 0, z_plane])

        intersections_x = []
        intersections_y = []

        for i in range(len(data)):
            ray_direction = np.array([data['gaze_direction_x'].iloc[i], data['gaze_direction_y'].iloc[i],
                                      data['gaze_direction_z'].iloc[i]])
            ray_point = np.array([data['mideye_origin_x'].iloc[i], data['mideye_origin_y'].iloc[i],
                                  data['mideye_origin_z'].iloc[i]])
            psi = line_plane_collision(plane_normal, plane_point, ray_direction, ray_point)
            intersections_x.append(psi[0])
            intersections_y.append(psi[1])

        data['intersections_x_' + str(z_plane)] = intersections_x
        data['intersections_y_' + str(z_plane)] = intersections_y

    return data

