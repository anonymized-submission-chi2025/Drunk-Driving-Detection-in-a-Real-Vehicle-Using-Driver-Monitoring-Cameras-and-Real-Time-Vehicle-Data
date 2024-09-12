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

import tkinter as tk
import pickle
import matplotlib.pyplot as plt

def plot_pickle():
    #Read figure path and name
    path = e1.get()
    fig_name = e2.get()
    appendix = ".pickle"
    if(".pickle" in fig_name):
        appendix = ""
    fig_name = fig_name + appendix
    whole_path = path + '/' + fig_name
    print("Trying to plot following figure:\n{}".format(whole_path))
    figx = pickle.load(open(whole_path, 'rb'))

    # Read axes limits
    try:
        x_min = float(e3.get())
    except:
        x_min = None
    try:
        xmax = float(e4.get())
    except:
        x_max = None
    try:
        y_min = float(e5.get())
    except:
        y_min = None
    try:
        y_max = float(e6.get())
    except:
        y_max = None
    # Set axes limits
    axes = plt.gcf().get_axes()
    for ax in axes:
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)


    # Read axis label
    try:
        x_label = str(e7.get())
    except:
        x_label = None
    try:
        y_label = str(e8.get())
    except:
        y_label = None
    # Set axis labels
    plt.xlabel(x_label)
    plt.ylabel(y_label)


    # Read title
    try:
        title_name = str(e9.get())
    except:
        title_name = None
    # Set title
    plt.title(title_name)

    # Show plot:
    plt.show()

if __name__=='__main__':
    master = tk.Tk()
    tk.Label(master,
             text="Required fields:").grid(row=0)
    tk.Label(master,
             text="Folder").grid(row=1)
    tk.Label(master,
             text="Figure").grid(row=2)
    tk.Label(master,
             text="Optional fields:").grid(row=3)
    tk.Label(master,
             text="x_min").grid(row=4)
    tk.Label(master,
             text="x_max").grid(row=5)
    tk.Label(master,
             text="y_min").grid(row=6)
    tk.Label(master,
             text="y_max").grid(row=7)
    tk.Label(master,
            text="x_label").grid(row=8)
    tk.Label(master,
            text="y_label").grid(row=9)
    tk.Label(master,
            text="Title").grid(row=10)


    e1 = tk.Entry(master)
    e2 = tk.Entry(master)
    e3 = tk.Entry(master)
    e4 = tk.Entry(master)
    e5 = tk.Entry(master)
    e6 = tk.Entry(master)
    e7 = tk.Entry(master)
    e8 = tk.Entry(master)
    e9 = tk.Entry(master)

    e1.grid(row=1, column=1, ipadx=400)
    e2.grid(row=2, column=1, ipadx=400)
    e3.grid(row=4, column=1, ipadx=50)
    e4.grid(row=5, column=1, ipadx=50)
    e5.grid(row=6, column=1, ipadx=50)
    e6.grid(row=7, column=1, ipadx=50)
    e7.grid(row=8, column=1, ipadx=50)
    e8.grid(row=9, column=1, ipadx=50)
    e9.grid(row=10, column=1, ipadx=400)

    tk.Button(master,
              text='Quit',
              command=master.quit).grid(row=15,
                                        column=0,
                                        sticky=tk.W,
                                        pady=4)
    tk.Button(master,
              text='Show', command=plot_pickle).grid(row=15,
                                                           column=1,
                                                           sticky=tk.W,
                                                           pady=4)

    tk.mainloop()
