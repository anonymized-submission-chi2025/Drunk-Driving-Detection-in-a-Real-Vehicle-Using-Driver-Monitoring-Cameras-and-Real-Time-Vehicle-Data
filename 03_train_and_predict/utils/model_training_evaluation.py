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

from sklearn.metrics import make_scorer, accuracy_score, balanced_accuracy_score, average_precision_score, f1_score, \
    recall_score, precision_score, matthews_corrcoef, roc_curve, roc_auc_score
from joblib import Parallel, delayed
import numpy as np
from sklearn.base import clone
import pandas as pd
import pickle
from sklearn.pipeline import Pipeline
from utils.scale_train_one_model import train_sklearn_LR_lasso, train_sklearn_general


from utils.train_on_top_model import train_on_top_model

SCORING = {'ROC AUC': 'roc_auc', 'Accuracy': make_scorer(accuracy_score),
           "Balanced Accuracy": make_scorer(balanced_accuracy_score), "F1": make_scorer(f1_score),
           "PRC AUC": make_scorer(average_precision_score, response_method="predict_proba"),
           "Recall": make_scorer(recall_score), "Precision": make_scorer(precision_score),
           "MCC": make_scorer(matthews_corrcoef)}


def train_one_participant(clf: Pipeline, X: pd.DataFrame, y: pd.Series, y_orig: pd.Series, groups: pd.Series, scenarios: pd.Series, group: str, config: dict[str, any]) -> dict[str, any]:
    X_train = X[groups != group]
    y_train = y[groups != group]
    X_test = X[groups == group]

    #y_pred_proba_train, y_pred_proba_test, coef = train_sklearn_general(X_train, y_train, X_test)
    y_pred_proba_train, y_pred_proba_test, coef = train_sklearn_LR_lasso(X_train, y_train, X_test)
    #y_pred_proba_train, y_pred_proba_test, coef = train_IGANN(X_train, y_train, X_test)

    if config["use_on_top_model"]:
        y_pred_proba_test = train_on_top_model(y_pred_proba_train,
                                               y_pred_proba_test, y_train,
                                               y[groups == group],
                                               groups[groups != group],
                                               groups[groups == group], 
                                               scenarios[groups != group],
                                               scenarios[groups == group], 
                                               y_orig[groups != group],
                                               y_orig[groups == group])

    AUCROC_train_score = roc_auc_score(y_train, y_pred_proba_train)

    return {group: {"y_pred_proba_test": y_pred_proba_test, "AUCROC_train_score": AUCROC_train_score, "coef": coef, "X_test": X_test,
                    "y_true_test": y[groups == group], "user_ids": groups[groups == group], "scenarios": scenarios[groups == group],
                    "y_orig_test": y_orig[groups == group]}}


def train_LOSO(data: pd.DataFrame, clf: Pipeline, y_column: str, core_features: list[str], model: str, config: dict[str, any]) -> dict[str, any]:
    '''
    not_to_use_cols = [
        'groundtruth+variant++', 'groundtruth+id++', 'groundtruth+phase++',
        'groundtruth+scenario++', 'groundtruth+BAC++', 'groundtruth+phase+CAN+',
        'groundtruth+state++', 'y_EW', 'y_AL', 'groundtruth+state+CAN+',
        'groundtruth+scenario+CAN+', 'groundtruth+variant+CAN+', 'groundtruth+id+CAN+']

    core_features = [x for x in data.columns if x not in not_to_use_cols]
    '''
    n_jobs = config["num_cores"]

    X = data[core_features]
    y_orig = data["groundtruth+state++"]
    scenarios = data["groundtruth+scenario++"]
    groups = data["groundtruth+id++"]
    y = data[y_column]

    verbose = 0
    if config["verbose"]:
        verbose = 101

    if config["use_parallel_processing"]:
        with Parallel(n_jobs=n_jobs, verbose=verbose) as parallel:
            results = parallel(delayed(train_one_participant)(clone(
                clf), X, y, y_orig, groups, scenarios, group, config) for group in np.unique(groups))
    else:
        results = []
        for group in np.unique(groups):
            print("Processing: " + str(group))
            results.append(train_one_participant(
                clone(clf), X, y, y_orig, groups, scenarios, group, config))

    results = {k: v for d in results for k, v in d.items()}

    data_out = data.copy()
    data_out["y_test"] = -1
    data_out["y_proba_test"] = -1
    data_out["y_orig_test"] = -1
    data_out["user_ids"] = -1
    data_out["scenarios"] = -1

    model_infos = {}

    for group in sorted(results.keys()):

        participant_index = (data_out["groundtruth+id++"] == group)
        data_out.loc[participant_index,
                     'y_test'] = results[group]["y_true_test"]
        data_out.loc[participant_index,
                     'y_proba_test'] = results[group]["y_pred_proba_test"]
        data_out.loc[participant_index,
                     'y_orig_test'] = results[group]["y_orig_test"]
        data_out.loc[participant_index,
                     'user_ids'] = results[group]["user_ids"]
        data_out.loc[participant_index,
                     'scenarios'] = results[group]["scenarios"]

        results_participant = dict()
        results_participant["coefs"] = results[group]["coef"]
        results_participant["AUROC_train"] = results[group]["AUCROC_train_score"]
        model_infos[group] = results_participant

    y_min_class = 0
    y_max_class = 1
    data_out['y_pred_test'] = np.where(
        data_out['y_proba_test'] < 0.5, y_min_class, y_max_class)

    model_infos['data'] = data_out
    model_infos['features'] = core_features
    model_infos['name'] = model
    model_infos['window_size'] = config["window_length"]

    AUROC_train_score_new = []
    for key, value in model_infos.items():
        if "drive" not in key:
            continue
        AUROC_train_score_new.append(value["AUROC_train"])

    if config["verbose"]:
        print("Training scores " + model + " :")
        print(str(np.array(AUROC_train_score_new).mean()) +
              " +/- " + str(np.array(AUROC_train_score_new).std()))

    return model_infos


def train_LOSO_safely(data: pd.DataFrame, clf: Pipeline, y_column: str, core_features: list[str], model: str, config: dict[str, any]) -> dict[str, any]:
    try:
        model_infos = train_LOSO(
            data, clf, y_column, core_features, model, config)
        return model_infos
    except Exception as e:
        print(f"An exception occurred: {e}")
