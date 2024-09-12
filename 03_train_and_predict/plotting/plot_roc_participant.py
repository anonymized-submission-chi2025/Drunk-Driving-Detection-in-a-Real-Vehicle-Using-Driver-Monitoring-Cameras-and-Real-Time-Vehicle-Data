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
import matplotlib.pyplot as plt
from sklearn import metrics



def labelLine(line,x,label=None,align=True,**kwargs):
    """
    Function called by labelLines and drawing text per single line
    line:  element of ax.get_lines()
    return: (None) add text to current plot
    """
    ax = line.axes
    xdata = line.get_xdata()
    ydata = line.get_ydata()

    if (x < xdata[0]) or (x > xdata[-1]):
        print('x label location is outside data range!')
        return

    #Find corresponding y coordinate and angle of the line
    ip = 1
    for i in range(len(xdata)):
        if x < xdata[i]:
            ip = i
            break

    y = ydata[ip-1] + (ydata[ip]-ydata[ip-1])*(x-xdata[ip-1])/(xdata[ip]-xdata[ip-1])

    if not label:
        label = line.get_label()

    if align:
        #Compute the slope
        dx = xdata[ip] - xdata[ip-1]
        dy = ydata[ip] - ydata[ip-1]
        ang = degrees(atan2(dy,dx))

        #Transform to screen co-ordinates
        pt = np.array([x,y]).reshape((1,2))
        trans_angle = ax.transData.transform_angles(np.array((ang,)),pt)[0]

    else:
        trans_angle = 0

    #Set a bunch of keyword arguments
    if 'color' not in kwargs:
        kwargs['color'] = line.get_color()

    if ('horizontalalignment' not in kwargs) and ('ha' not in kwargs):
        kwargs['ha'] = 'center'

    if ('verticalalignment' not in kwargs) and ('va' not in kwargs):
        kwargs['va'] = 'center'

    if 'backgroundcolor' not in kwargs:
        kwargs['backgroundcolor'] = ax.get_facecolor()

    if 'clip_on' not in kwargs:
        kwargs['clip_on'] = True

    if 'zorder' not in kwargs:
        kwargs['zorder'] = 2.5

    ax.text(x,y,label,rotation=trans_angle,**kwargs)

def labelLines(lines,align=True,xvals=None,shorten_label=False, **kwargs):
    """
    Function to draw description in ROC plot of every line
    lines:  ax.get_lines()
    return: (None) add text to current plot
    """

    ax = lines[0].axes
    labLines = []
    labels = []

    #Take only the lines which have labels other than the default ones
    for line in lines:
        label = line.get_label()
        # added marxera --------------------------------------------------------
        #print('original label: ', label)

        if shorten_label:
            # neglect (AUC ...) ending
            split = label.split("(")
            short_label = split[0]
            # within plot
            split = short_label.split("old")
            short_label = split[-1]
            # overview within plot
            split = short_label.split("within")
            short_label = split[-1]
            # only category within plot
            split = short_label.split(":")
            short_label = split[0]

            if short_label.find("Mean ROC") == 0:
                short_label = short_label[0:8]

            # loso
            split = short_label.split("out")
            short_label = split[-1]
            # overwrite
            label = short_label

        #print('adjusted label: ', label)
        # end of added marxera -------------------------------------------------

        if "_line" not in label:
            labLines.append(line)
            labels.append(label)

    if xvals is None:
        xmin,xmax = ax.get_xlim()
        xvals = np.linspace(xmin,xmax,len(labLines)+2)[1:-1]

    for line,x,label in zip(labLines,xvals,labels):
        labelLine(line,x,label,align,**kwargs)

def plot_roc_participant(y_true, p_pred, groups, envs, setup_name, save_folder, print_details=True):
    # Initialize variables
    tprs = []
    aurocs = []
    precs = []
    auprcs = []
    mean_fpr = np.linspace(0, 1, 100)
    mean_recall = np.linspace(1, 0, 100)

    env_aurocs = {'highway': [], 'rural': [], 'city': []}
    env_aurocs_comp = {'highway': [], 'rural': [], 'city': []}
    env_tprs = {'highway': [], 'rural': [], 'city': []}
    env_tprs_comp = {'highway': [], 'rural': [], 'city': []}

    # Define figures
    fig_roc, ax_roc = plt.subplots(figsize=(16, 10), tight_layout=True)
    fig_roc_highway, ax_roc_highway = plt.subplots(figsize=(16, 10), tight_layout=True)
    fig_roc_town, ax_roc_town = plt.subplots(figsize=(16, 10), tight_layout=True)
    fig_roc_rural, ax_roc_rural = plt.subplots(figsize=(16, 10), tight_layout=True)
    fig_roc_comp, ax_roc_comp = plt.subplots(1, 3, figsize=(16, 8), tight_layout=True)
    fig_roc_prc, ax_roc_prc = plt.subplots(1, 2, figsize=(16, 10), tight_layout=True)
    ax_ROC_prc = ax_roc_prc[0]
    ax_roc_PRC = ax_roc_prc[1]

    # ------------------------------------------------------------------------------
    # Plot curves for single cv splits
    for group in sorted(np.unique(groups)):
        fpr, tpr, _ = metrics.roc_curve(y_true[groups == group], p_pred[groups == group])
        interp_tpr = np.interp(mean_fpr, fpr, tpr)
        interp_tpr[0] = 0.0
        tprs.append(interp_tpr)
        roc_auc = metrics.roc_auc_score(y_true[groups == group], p_pred[groups == group])
        aurocs.append(roc_auc)
        if print_details:
            ax_roc.plot(mean_fpr, interp_tpr, alpha=0.3, lw=1,
                        label='ROC CV leaving out P' + str(group) + fr' (AUC = {roc_auc:0.2f})')
            ax_ROC_prc.plot(mean_fpr, interp_tpr, alpha=0.3, color='black', lw=1)

        # Plot each scenario
        for i, (env, env_ax) in enumerate(zip(['highway', 'rural', 'city', 'highway', 'rural', 'city'],
                                              [ax_roc_highway, ax_roc_rural, ax_roc_town, *ax_roc_comp.flat])):

            y_trues, y_preds = y_true[(groups == group) & (envs == env)], p_pred[(groups == group) & (envs == env)]
            fpr, tpr, _ = metrics.roc_curve(y_trues, y_preds)
            interp_tpr = np.interp(mean_fpr, fpr, tpr)
            interp_tpr[0] = 0.0

            if i < 3:
                try:   
                    roc_auc_env = metrics.roc_auc_score(y_trues, y_preds)
                    env_aurocs[env].append(roc_auc_env)
                    env_tprs[env].append(interp_tpr)
                    if print_details:
                        env_ax.plot(mean_fpr, interp_tpr, alpha=0.3, lw=1,
                                    label='ROC CV leaving out P' + str(group) + fr' (AUC = {roc_auc_env:0.2f})')
                except ValueError as e:
                    print(group, "exception was thrown: ", e)       
            else:
                try:
                    env_aurocs_comp[env].append(metrics.roc_auc_score(y_trues, y_preds))
                    env_tprs_comp[env].append(interp_tpr)
                    if print_details:
                        env_ax.plot(mean_fpr, interp_tpr, alpha=0.1, color='black', lw=1)
                except ValueError as e:
                    print(group, "exception was thrown: ", e)   

        # Precision-recall plot
        prec, recall, _ = metrics.precision_recall_curve(y_true[groups == group], p_pred[groups == group])
        interp_prec = np.flip(np.interp(np.flip(mean_recall), np.flip(recall), np.flip(prec)))
        interp_prec[-1] = 1.0
        precs.append(interp_prec)
        auprc = metrics.auc(recall, prec)
        auprcs.append(auprc)
        if print_details:
            ax_roc_PRC.plot(mean_recall, interp_prec, alpha=0.1, color='black', lw=1)
    # ------------------------------------------------------------------------------
    def roc_plot(ax, ax_aurocs, ax_tprs, title, color_fill):
        ax.plot([0, 1], [0, 1], linestyle='--', lw=2, color='r', label='Chance', alpha=.8)
        mean_tpr = np.mean(ax_tprs, axis=0)
        mean_tpr[-1] = 1.0
        ax.plot(mean_fpr, mean_tpr, color='b', lw=2, alpha=.8,
                label=fr'Mean ROC (AUC = {np.mean(ax_aurocs):0.2f} $\pm$ {np.std(ax_aurocs):0.2f})')

        std_tpr = np.std(ax_tprs, axis=0)
        tprs_upper, tprs_lower = np.minimum(mean_tpr + std_tpr, 1), np.maximum(mean_tpr - std_tpr, 0)
        ax.fill_between(mean_fpr, tprs_lower, tprs_upper, color=color_fill, alpha=.2, label=r'$\pm$ 1 SD')
        ax.set_aspect('equal', 'box')
        ax.set(xlabel='1 - Specificity', ylabel='Sensitivity')
        ax.legend(loc="lower right")
        ax.set(xlim=[-0.02, 1.02], ylim=[-0.02, 1.02], title=title)

    # ------------------------------------------------------------------------------
    # Plot mean curves and set design settings

    # Overall ROC plot
    roc_plot(ax_roc, aurocs, tprs, '', 'grey')
    labelLines(ax_roc.get_lines(), align=False, xvals=None, shorten_label=True)
    ax_roc.set(xlim=[-0.05, 1.05], ylim=[-0.05, 1.05], xlabel='False Positive Rate', ylabel='True Positive Rate')
    ax_roc.legend(bbox_to_anchor=(1.04, 0.5), loc="center left", fontsize='large')
    #fig_roc.suptitle('ROC AUC Overview LOSO', fontsize=20)

    # Scenario plots
    for i, (env, env_ax) in enumerate(zip(['highway', 'rural', 'city', 'highway', 'rural', 'city'],
                                          [ax_roc_highway, ax_roc_rural, ax_roc_town, *ax_roc_comp.flat])):
        if i < 3:
            roc_plot(env_ax, env_aurocs[env], env_tprs[env], '', 'grey')
            labelLines(env_ax.get_lines(), align=False, xvals=None, shorten_label=True)
            env_ax.set(xlim=[-0.05, 1.05], ylim=[-0.05, 1.05], xlabel='False Positive Rate',
                       ylabel='True Positive Rate')
            #env_ax.set_title('ROC AUC Overview LOSO - Scenario ' + env.capitalize(), fontsize=20)
            env_ax.legend(bbox_to_anchor=(1.04, 0.5), loc="center left", fontsize='large')
        else:
            roc_plot(env_ax, env_aurocs_comp[env], env_tprs_comp[env], f'ROC Curve - {env.capitalize()}', 'b')
            env_ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12))

    fig_roc_comp.suptitle('Comparison of the ROC plots for the different scenarios LOSO', y=0.85, fontsize=20)

    # ROC vs. Precision-Recall plot
    # ROC plot
    roc_plot(ax_ROC_prc, aurocs, tprs, 'ROC Curve', 'b')
    fig_roc_prc.suptitle('ROC vs. Precision-Recall LOSO', y=0.90, fontsize=20)

    # Precision-Recall plot
    ratio_positive_examples = y_true.sum() / len(y_true)
    ax_roc_PRC.plot([0, 1], [ratio_positive_examples, ratio_positive_examples],
                    linestyle='--', lw=2, color='r', label='Ratio positive examples', alpha=.8)
    mean_prec = np.mean(precs, axis=0)
    ax_roc_PRC.plot(mean_recall, mean_prec, color='b', lw=2, alpha=.8,
                    label=fr'Mean PR (AUC = {metrics.auc(mean_recall, mean_prec):0.2f} $\pm$ {np.std(auprcs):0.2f})')

    std_prec = np.std(precs, axis=0)
    precs_upper, precs_lower = np.minimum(mean_prec + std_prec, 1), np.maximum(mean_prec - std_prec, 0)
    ax_roc_PRC.fill_between(mean_recall, precs_upper, precs_lower, color='b', alpha=.2, label=r'$\pm$ 1 SD')
    ax_roc_PRC.set_aspect('equal', 'box')
    ax_roc_PRC.set(xlabel='Recall', ylabel='Precision')
    ax_roc_PRC.legend(loc="lower right")
    ax_roc_PRC.set(xlim=[-0.02, 1.02], ylim=[-0.02, 1.02], title=f"PR Curve")

    # ------------------------------------------------------------------------------
    # Save figures
    '''
    fig_roc.savefig(save_folder + setup_name + '_ROC.pdf', bbox_inches='tight', dpi=150)
    fig_roc_highway.savefig(save_folder + setup_name + '_ROC_highway.pdf', bbox_inches='tight', dpi=150)
    fig_roc_town.savefig(save_folder + setup_name + '_ROC_town.pdf', bbox_inches='tight', dpi=150)
    fig_roc_rural.savefig(save_folder + setup_name + '_ROC_rural.pdf', bbox_inches='tight', dpi=150)
    fig_roc_comp.savefig(save_folder + setup_name + '_ROC_comp.pdf', bbox_inches='tight', dpi=150)
    fig_roc_prc.savefig(save_folder + setup_name + '_ROC_PRC.pdf', bbox_inches='tight', dpi=150)
    '''
    plt.show(fig_roc)
    print("highway:")
    plt.show(fig_roc_highway)
    print("town:")
    plt.show(fig_roc_town)
    print("rural:")
    plt.show(fig_roc_rural)
    plt.show(fig_roc_comp)
    plt.show(fig_roc_prc)
    plt.close(fig_roc)
    plt.close(fig_roc_highway)
    plt.close(fig_roc_town)
    plt.close(fig_roc_rural)
    plt.close(fig_roc_comp)
    plt.close(fig_roc_prc)