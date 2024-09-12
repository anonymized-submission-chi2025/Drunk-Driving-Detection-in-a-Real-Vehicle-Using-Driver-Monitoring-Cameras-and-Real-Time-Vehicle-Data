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

def main_plotting(result_dfs, config):
    import seaborn as sns

    from sklearn import metrics
    import scipy.stats as st
    from matplotlib import rcParams
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.offsetbox import AnchoredText

    # The following still affects all plots, even if they are in generated in subfunctions

    matplotlib.rcParams['axes.titlesize'] = 18
    matplotlib.rcParams['axes.labelsize'] = 12
    matplotlib.rcParams['legend.fontsize'] = 12
    matplotlib.rcParams['font.size'] = 14
    matplotlib.rcParams['lines.linewidth'] = 2
    matplotlib.rcParams['xtick.labelsize'] = 10
    matplotlib.rcParams['ytick.labelsize'] = 10
    matplotlib.rcParams['pdf.fonttype'] = 42
    matplotlib.rcParams['ps.fonttype'] = 42

    rcParams.update({
        'font.family':'sans-serif',
        'font.sans-serif':['Liberation Sans'],
        })

    class LegendHandler(matplotlib.legend_handler.HandlerBase):
        def create_artists(self, legend, orig_handle,
                           x0, y0, width, height, fontsize, trans):
            l1 = plt.Line2D([x0,y0+width], [1*height,1*height], color='C0')
            return [l1]

    LABEL = 30

    model_colors = {
        'Margin': 'C1',
        'Early Warning': 'C0',
        'Above Limit': 'C4'
    }

    scenario_colors = { 'Margin': {'highway': (253/255, 187/255, 128/255), 'rural': (242/255, 109/255, 24/255), 'city': (146/255, 46/255, 3/255)},
                       'Early Warning': { 'highway': (162/255, 203/255, 226/255), 'rural': (48/255, 128/255, 189/255), 'city': (8/255, 78/255, 151/255)},
                       'Above Limit': {'highway': (185/255, 186/255, 218/255), 'rural': (128/255, 125/255, 186/255), 'city': (68/255, 9/255, 129/255)},
    }

    def transform_data(all_results):
        y_true = []
        y_pred = []
        y_pred_proba = []
        y_orig = []
        scenarios = []
        subjects = []
        coefs = {}

        for key in all_results.keys():
            if "2" in key:
                y_true.extend(all_results[key]["y_true"])
                y_pred.extend(all_results[key]["y_pred"])
                y_pred_proba.extend(all_results[key]["y_pred_proba"])
                scenarios.extend(all_results[key]["scenario"])
                subjects.extend([key] * len(all_results[key]["y_true"]))
                y_orig.extend(all_results[key]["y_orig"])
                coefs[key] = all_results[key]["coefs"]

        
        y_true = np.array(y_true)  
        y_pred = np.array(y_pred)
        y_pred_proba = np.array(y_pred_proba)
        scenarios = np.array(scenarios)
        subjects = np.array(subjects)
        y_orig = np.array(y_orig)
        return {"y_true": y_true,"y_orig": y_orig, "y_pred": y_pred, "y_pred_proba": y_pred_proba, "scenarios": scenarios, "subjects": subjects, "coefs": coefs}

    results = {}
    models = config["models"]
    for model in models:
        print(model)
        results[model] = transform_data(result_dfs[model])
    print([k for k in results.keys()])

    from plotting.plot_roc import plot_roc

    plot_roc(results, model_colors, scenario_colors)

    from plotting.plot_roc_participant import plot_roc_participant
    for model in results.keys():
        print("*****************************************************")
        print(model)
        result = results[model]

        plot_roc_participant(result['y_true'], result['y_pred_proba'], result['subjects'], result['scenarios'], " ", "", print_details=True)

    from utils.print_coefs import print_coefs

    print_coefs(results)