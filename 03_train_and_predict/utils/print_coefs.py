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

def print_coefs(results):

    ## Check out features

    first_key, _ = next(iter(results['Early Warning']['coefs'].items()))
    coef_list = results['Early Warning']['coefs'][first_key]['Feature'].to_list()

    ## Early Warning
    coef_EW_df = []
    model = 'Early Warning'
    subjects = results[model]["subjects"]
    for t_id in np.unique(subjects):
        coef_EW_df.append(([t_id] + results[model]['coefs'][t_id]['Coefficients'].values.tolist()))
    df_coef_EW = pd.DataFrame(coef_EW_df, columns=(['id'] + coef_list))
    df_coef_EW.set_index('id', inplace=True)

    mean_row = df_coef_EW.mean().to_frame().T
    std_row = df_coef_EW.std().to_frame().T
    min_row = df_coef_EW.min().to_frame().T
    max_row = df_coef_EW.max().to_frame().T

    mean_row.index = ['mean']
    std_row.index = ['std']
    min_row.index = ['min']
    max_row.index = ['max']

    df_coef_EW = pd.concat([df_coef_EW, mean_row, std_row, min_row, max_row])

    ## Above Limit
    coef_AL_df = []
    model = 'Above Limit'
    subjects = results[model]["subjects"]
    for t_id in np.unique(subjects):
        coef_AL_df.append(([t_id] + results[model]['coefs'][t_id]['Coefficients'].values.tolist()))

    coef_AL_df = pd.DataFrame(coef_AL_df, columns=(['id'] + coef_list))
    coef_AL_df.set_index('id', inplace=True)

    mean_row = coef_AL_df.mean().to_frame().T
    std_row = coef_AL_df.std().to_frame().T
    min_row = coef_AL_df.min().to_frame().T
    max_row = coef_AL_df.max().to_frame().T

    mean_row.index = ['mean']
    std_row.index = ['std']
    min_row.index = ['min']
    max_row.index = ['max']

    coef_AL_df = pd.concat([coef_AL_df, mean_row, std_row, min_row, max_row])

    print("Early Warning")

    df_coef_EW = df_coef_EW[df_coef_EW.loc['mean'].sort_values(key=abs).index.tolist()]
    print("Top 10 Features: mean +/- std")
    print("===========")
    for feature in df_coef_EW.columns[-10:].tolist():
        print(str(feature) + ":  " + str(df_coef_EW[feature]['mean']) + " +/- " + str(df_coef_EW[feature]['std']))

    print("Above Limit")

    coef_AL_df = coef_AL_df[coef_AL_df.loc['mean'].sort_values(key=abs).index.tolist()]
    print("Top 10 Features: mean +/- std")
    print("===========")
    for feature in coef_AL_df.columns[-10:].tolist():
        print(str(feature) + ":  " + str(coef_AL_df[feature]['mean']) + " +/- " + str(coef_AL_df[feature]['std']))



    ## Early Warning - keep only the ones related to saccades

    print("Early Warning")

    df_coef_EW = df_coef_EW[df_coef_EW.loc['mean'].sort_values(key=abs).index.tolist()]
    print("Top 10 Sacc / Fixa Features: mean +/- std")
    print("===========")
    for feature in df_coef_EW.columns[-100:].tolist():
        if "SACC" in feature or "FIXA" in feature:
            print(str(feature) + ":  " + str(df_coef_EW[feature]['mean']) + " +/- " + str(df_coef_EW[feature]['std']))



    ## Above Limit - keep only the ones related to saccades

    print("Above Limit")

    coef_AL_df = coef_AL_df[coef_AL_df.loc['mean'].sort_values(key=abs).index.tolist()]
    print("Top 10 Sacc / Fixa Features: mean +/- std")
    print("===========")
    for feature in coef_AL_df.columns[-100:].tolist():
        if "SACC" in feature or "FIXA" in feature:
            print(str(feature) + ":  " + str(coef_AL_df[feature]['mean']) + " +/- " + str(coef_AL_df[feature]['std']))