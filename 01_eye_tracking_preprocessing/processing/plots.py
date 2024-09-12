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

from scipy.fftpack import fft
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def plot_fft(data: pd.DataFrame, folder: str):
    X = fft(data.index.to_series().diff().dt.total_seconds().dropna().values)
    N = len(X)
    n = np.arange(N)
    # get the sampling rate
    sr = 1 / (60 * 60)
    T = N / sr
    freq = n / T

    # Get the one-sided specturm
    n_oneside = N // 2
    # get the one side frequency
    f_oneside = freq[:n_oneside]

    plt.figure(figsize=(12, 6))
    plt.plot(f_oneside, np.abs(X[:n_oneside]), "b")
    plt.xlabel("Freq (Hz)")
    plt.ylabel("FFT Amplitude |X(freq)|")
    plt.title(folder)
    plt.show()
