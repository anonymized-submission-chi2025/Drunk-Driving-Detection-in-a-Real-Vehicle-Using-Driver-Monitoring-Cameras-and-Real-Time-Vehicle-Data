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

#!/usr/bin/env python

# use this script local in environment created with Pipfile
# Matplotlib should there be 2.2.3

import pickle
import matplotlib
import matplotlib.pyplot as plt
print('matplotlib: {}'.format(matplotlib.__version__))

# # read figure path and name
# path = '/media/andreas/8GB_ANMA/test'
# fig_name = 'test'
# appendix = '.fig.pickle'
#
#
# if(".fig.pickle" in fig_name):
#     appendix = ""
# elif(".fig" in fig_name):
#     appendix = ".pickle"
#
# # read in figure
# fig_name = fig_name + appendix
# whole_path = path + '/' + fig_name
# print("Trying to plot following figure:\n{}".format(whole_path))
# fig_handle = pickle.load(open(whole_path, 'rb'))
#
# # show plot:
# plt.show()


# Load figure from disk and display
fig_handle = pickle.load(open('sinus.pickle', 'rb'))

print('axes: ', plt.gcf().get_axes())

plt.show()

print('Finished')
