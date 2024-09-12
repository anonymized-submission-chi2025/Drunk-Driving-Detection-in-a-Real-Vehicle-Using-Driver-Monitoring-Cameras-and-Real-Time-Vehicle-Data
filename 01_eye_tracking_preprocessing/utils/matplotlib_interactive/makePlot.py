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

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
import pickle
# OWN FUNCTIONS
from fct_save_pickle_plot import save_pickle_plot

# Plot simple sinus function
x = np.linspace(0, 2*np.pi)
y = np.sin(x)
plt.plot(x, y)
plt.title('Test')

# save
##########################

# fig_handle = plt.gcf()
# print('fig_handle axes: ', fig_handle.get_axes())
# # Save pickle
# with open('sinus.pickle', 'wb') as f:
#     pickle.dump(fig_handle, f)
#
# # Save Figure
# plt.savefig('sinus.pdf', dpi=400)
#
# # close figure
# plt.close(fig_handle)


# save with function defined
###########################
name = 'test_new'
SAVE_FIG_PATH = '/headwind/analysis/notes/'
save_pickle_plot(plt, name, SAVE_FIG_PATH)
