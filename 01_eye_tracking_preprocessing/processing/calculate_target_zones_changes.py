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


def calculate_target_zones_changes(data: pd.DataFrame, window_size=1000):
    data_target_zone = data["target_zone"]
    number_of_changes = []
    current_changes = 0

    for i, zone in enumerate(data_target_zone):
        if i < window_size - 1:
            number_of_changes.append(0)
        if i == window_size - 1:
            for j in range(0, i):
                if data_target_zone.iloc[j] != data_target_zone.iloc[j + 1]:
                    current_changes += 1
            number_of_changes.append(current_changes)
        if i > window_size - 1:
            if data_target_zone.iloc[i] != data_target_zone.iloc[i - 1]:
                current_changes += 1
            if (
                data_target_zone.iloc[i - window_size]
                != data_target_zone.iloc[i - window_size + 1]     #### TODO: why compare the ones 1 widow size ago?
            ):
                current_changes -= 1
            number_of_changes.append(current_changes)

    data["target_zone_changes_" + str(window_size)] = number_of_changes

    return data
