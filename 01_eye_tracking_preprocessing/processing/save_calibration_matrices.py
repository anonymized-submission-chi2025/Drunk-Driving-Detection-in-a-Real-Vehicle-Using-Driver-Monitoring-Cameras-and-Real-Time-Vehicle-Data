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

import os
from read_in_cam2world import read_in_cam2world

base_directory = '../../Data/field_study'
file = open('../../Data/calibration_matrices.txt', 'w')

for folder in os.listdir(base_directory):
    if not folder.startswith('.'):
        directory_folder = base_directory + '/' + folder
        cam2world = read_in_cam2world(directory_folder)
        file.write('Proband ' + folder + '\n' + str(cam2world) + '\n')

file.close()
