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
from scipy.stats import skew, kurtosis, iqr, entropy

NUMERICAL_FUNCTIONS = {
    'mean': np.mean,
    'median': np.nanmedian,
    'std': np.std,
    'min': np.min,
    'q5': lambda x: np.nanquantile(x, 0.05),
    'max': np.max,
    'q95': lambda x: np.nanquantile(x, 0.95),
    'range': lambda x: (np.max(x) - np.min(x)),
    'iqr': lambda x: iqr(x, nan_policy="omit"),
    'iqr5_95': lambda x: iqr(x, rng=(5, 95), nan_policy="omit"),
    'sum':np.nansum,
    'energy': lambda x: np.nansum(x ** 2),
    'power': lambda x: np.nansum(x ** 2) / np.count_nonzero(x),
    'skewness': lambda x: skew(x, nan_policy="omit"),
    'kurtosis': lambda x: kurtosis(x, nan_policy="omit"),
    'rms': lambda x: np.sqrt(np.nansum(x ** 2) / np.count_nonzero(x)),
    'sum_abs_changes': lambda x: np.nansum(np.abs(np.diff(x))),
    'n_sign_changes': lambda x: np.nansum(np.diff(np.sign(x)) != 0),
}

BINARY_FUNCTIONS = {
    'sum': np.nansum,
    'mean': np.nanmean,
    'std': np.std,
}

