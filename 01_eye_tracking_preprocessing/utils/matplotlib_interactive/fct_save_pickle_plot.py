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
import matplotlib.pyplot as plt
import pickle

presentation_and_report_plot_setup = True # if True, larger title and font

if presentation_and_report_plot_setup == True:
    matplotlib.rcParams['axes.titlesize'] = 20
    matplotlib.rcParams['axes.labelsize'] = 18
    matplotlib.rcParams['legend.fontsize'] = 16
    matplotlib.rcParams['lines.linewidth'] = 3
    matplotlib.rcParams['xtick.labelsize'] = 18
    matplotlib.rcParams['ytick.labelsize'] = 18
    matplotlib.rcParams['font.size'] = 14 #labelLines Text
else:
    matplotlib.rcParams['axes.titlesize'] = 19
    matplotlib.rcParams['axes.labelsize'] = 15
    matplotlib.rcParams['legend.fontsize'] = 12
    matplotlib.rcParams['lines.linewidth'] = 2
    matplotlib.rcParams['xtick.labelsize'] = 12
    matplotlib.rcParams['ytick.labelsize'] = 12

def save_pickle_plot(plt, name, SAVE_PATH, use_fixed_size=True, fig_size_inches =(10,10), save_pickle=True, save_png=True, save_pdf=True):
    """
    Save figure as pickle, png and pdf file.
    The name of the figure is specified with name
    """
    fig_handle = plt.gcf()

    # Resize figure
    if use_fixed_size == True:
        fig_handle.set_size_inches(fig_size_inches, forward=False)

    # Save pickle
    if save_pickle == True:
        picklename = SAVE_PATH + name + '.pickle'
        with open(picklename, 'wb') as f:
            pickle.dump(fig_handle, f)

    # Save Figure
    if save_pdf == True:
        figname = SAVE_PATH + name + '.pdf'
        plt.savefig(figname, dpi=150)

    if save_png == True:
        figname = SAVE_PATH + name + '.png'
        plt.savefig(figname, dpi=150)

    # close figure
    plt.close(fig_handle)
    return
