import sys
import numpy as np
import pandas as pd
import scipy.stats as stats
import sklearn.metrics
import seaborn as sns
import matplotlib.pyplot as plt
sys.path.append('..')
from histogram import *
import math

sys.path.append('../..')
import utils
################# Compare patient dists and create heatmap of distribution similarity #############

###### helpers ###############
def parse_patient_code(goodHistogramC, badHistogramC, pcode):
    if pcode[0]=='g':
        histogramC = goodHistogramC
    elif pcode[0]=='b':
        histogramC = badHistogramC
    p_idx = int(pcode[1:])
    return histogramC, p_idx

def patient_code_to_df_index(pcode, ngood):
    p_idx = int(pcode[1:])
    if pcode[0]=='g':
        return p_idx
    elif pcode[0]=='b':
        return p_idx + ngood

###### mains ###############
def compare_patient_dists(goodHistogramC, badHistogramC, p1, p2, plot=False):
    # plots the distributions for two patients
    histogramC1, i1 = parse_patient_code(goodHistogramC, badHistogramC, p1)
    histogramC2, i2 = parse_patient_code(goodHistogramC, badHistogramC, p2)
    hist_1 = histogramC1.normalize()[i1]
    hist_2 = histogramC2.normalize()[i2]
    bin_values_1 = histogramC1.bins[:-1] + histogramC1.bin_size
    bin_values_2 = histogramC2.bins[:-1] + histogramC2.bin_size
    emd_distance = stats.wasserstein_distance(bin_values_1, bin_values_2, hist_1, hist_2)
    if plot:
        precounted_histograms([hist_1, hist_2], [histogramC1.bins, histogramC2.bins], 
                         'Similarity/Distance Distribution of {} and {}'.format(p1, p2), 
                              'Similarity/Dist', 'Density', [p1, p2], print_stats=False)
    return emd_distance

def heatmap_distribution_similarity(goodHistogramC, badHistogramC, figsize):
    good_histogram_matrix, bad_histogram_matrix = goodHistogramC.normalize(), badHistogramC.normalize()
    good_bin_values = goodHistogramC.bins[:-1] + goodHistogramC.bin_size
    bad_bin_values = badHistogramC.bins[:-1] + badHistogramC.bin_size
    ngood, nbad = good_histogram_matrix.shape[0], bad_histogram_matrix.shape[0]
    df_index = []
    for i in range(ngood):
        df_index.append('g{}'.format(i))
    for i in range(nbad):
        df_index.append('b{}'.format(i))
    heatmap_df = pd.DataFrame(np.zeros((ngood+nbad, ngood+nbad)), index=df_index, columns=df_index)

    for p1 in df_index:
        for p2 in df_index:
            emd_distance = compare_patient_dists(goodHistogramC, badHistogramC, p1, p2)
            p1_idx = patient_code_to_df_index(p1, ngood)
            p2_idx = patient_code_to_df_index(p2, ngood)
            heatmap_df.iloc[p1_idx, p2_idx] = emd_distance
    fig, ax = plt.subplots(figsize=figsize)         # Sample figsize in inches
    a = sns.heatmap(heatmap_df, ax=ax)
    plt.show()
    return a
    
########################### one x vs outcome #########################

###### helpers ###############
def filter_out_nans(x, outcomes):
    x_filtered = []
    outcomes_filtered = []
    for val, outcome in zip(x, outcomes):
        if np.isnan(val):
            continue
        if outcome == -1:
            continue
        x_filtered.append(val)
        outcomes_filtered.append(outcome)
    return x_filtered, outcomes_filtered

def binarize_outcomes(outcomes, good_binary=1):
    outcome_binary = [] # 1 for good, 0 for bad
    bad_binary = 1 - good_binary
    for outcome in outcomes:
        if utils.is_good_outcome(outcome):
            outcome_binary.append(good_binary)
        else:
            outcome_binary.append(bad_binary)
    return outcome_binary

def roundup(x, bin_size):
    return x+bin_size-x%bin_size

def rounddown(x, bin_size):
    if x%bin_size==0:
        return x - bin_size
    else:
        return x-x%bin_size        

###### mains ###############
def plot_xbins_vs_percent_outcomes(x, outcomes, nbins, normalize=False, binarize=False, transpose=False, scale_xaxis=True, bin_by_percentile=False, similarity_fn=None):
    # make df with outcomes on column, x-bin-ranges on index, and the value inside
    # = # people with in that bin-range with that outcome.
    # then can normalize so that row sums to 1. 
    x_filtered, outcomes_filtered = filter_out_nans(x, outcomes)
    min_x, max_x = math.floor(min(x_filtered)), math.ceil(max(x_filtered))
    if min_x==0 and max_x==1 and scale_xaxis:
        # scaled, so all between 0 and 1
        min_x = roundup(min(x_filtered), 0.002)
        max_x = rounddown(max(x_filtered), 0.002)
    bin_size = (max_x - min_x) / (nbins+0.0)
    if min_x==0 and max_x==1:
        # scaled, so nothing above 1:
        bin_starts = np.arange(min_x, max_x, bin_size)
        bin_ends = np.arange(min_x+bin_size, max_x+bin_size, bin_size)
    else:
        bin_starts = np.arange(min_x, max_x+bin_size, bin_size)
        bin_ends = np.arange(min_x+bin_size, max_x+2*bin_size, bin_size)

    if bin_by_percentile:
        percentiles = np.percentile(x_filtered, np.arange(0, 101, 100.0/nbins))
        bin_starts = percentiles[:nbins]
        bin_ends = percentiles[(-1*nbins):]
    
    df_index = []
    for bin_start, bin_end in zip(bin_starts, bin_ends):
        df_index.append('{:0.3f}-{:0.3f}'.format(bin_start, bin_end))
    if binarize:
        columns = ["good", "bad"]
    else:
        columns = [1,2,3,4,5]
    bin_vs_outcome_df = pd.DataFrame(index=df_index, columns=columns)

    for bin_start, bin_end, df_row_name in zip(bin_starts, bin_ends, bin_vs_outcome_df.index):
        outcome_counts = {}
        for column in columns:
            outcome_counts[column] = 0
        for val, outcome in zip(x_filtered, outcomes_filtered):
            if outcome == -1:
                continue
            if val >= bin_start and val < bin_end:
                if binarize:
                    outcome = "good" if utils.is_good_outcome(outcome) else "bad"
                outcome_counts[outcome] += 1
        bin_vs_outcome_df.loc[df_row_name] = outcome_counts
    bin_vs_outcome_df = bin_vs_outcome_df.fillna(0)
    if transpose:
        bin_vs_outcome_df = bin_vs_outcome_df.transpose()
    ns = bin_vs_outcome_df.sum(axis=1)
    if normalize:
        bin_vs_outcome_df = bin_vs_outcome_df.div(bin_vs_outcome_df.sum(axis=1), axis=0)
    if not transpose:
        if binarize:
            colors = [(0, 185/255., 0), (1, 0, 0)]
        if not binarize:
            colors = [(0, 185/255., 0), (90/255., 1, 90/255.), (1, 90/255., 90/255.), (210/255., 40/255., 40/255.), 
                      (185/255., 0, 0)]
    else:
        colors = None
    ax = bin_vs_outcome_df.plot.bar(stacked=True, color=colors)
    plt.legend(loc=2, bbox_to_anchor=(1.1, 1.05))
    if similarity_fn is not None:
        plt.title('% Outcomes for bins of similarity ({})'.format(similarity_fn))
    else:
        plt.title('% Outcomes for bins of similarity')
    if normalize:
        for i in range(len(ns)):
            ax.text(i, 1.03,'n={}'.format(ns[i]), horizontalalignment ='center', size=10)
        ax.set_ylim(0, 1.1)
    plt.show()
    return ax

def plot_x_vs_outcome(x, outcomes, filter=True):
    if filter:
        x, outcomes = filter_out_nans(x, outcomes)
    x_filled = np.copy(x)
    for ind in np.where(np.isnan(x_filled))[0]:
        x_filled[ind] = -200 + np.random.randint(-20,20)
    #x_filled[np.where(np.isnan(x_filled))] = -70000 + np.random.randint(-100,100)
    xy = np.vstack([x_filled,outcomes])
    z = stats.gaussian_kde(xy)(xy)
    fig, ax = plt.subplots()
    plt.scatter(x_filled, outcomes, c=z, s=10)
    plt.show()
    
def statistical_correlation(x, outcomes):
    x_filtered, outcomes_filtered = filter_out_nans(x, outcomes)
    print 'spearman', stats.spearmanr(x_filtered, outcomes_filtered)
    #print 'pearson', stats.pearsonr(x_filtered, outcomes_filtered)
    
def roc(x, outcomes, similarity_fn, similarity_type='similarity'):
    x_filtered, outcomes_filtered = filter_out_nans(x, outcomes)
    outcome_binary = binarize_outcomes(outcomes_filtered, good_binary=0 if similarity_type=='similarity' else 1)
    fpr, tpr, _ = sklearn.metrics.roc_curve(outcome_binary, x_filtered)
    roc_auc = sklearn.metrics.auc(fpr, tpr)
    f = plt.figure()
    roc = plt.plot(fpr, tpr, color='darkorange', label='ROC curve (area = %0.2f)' % roc_auc)
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic ({})'.format(similarity_fn))
    plt.legend(loc="lower right")
    plt.show()
    return f
    
def threshold(x, outcomes, similarity_type='similarity'):
    x_filtered, outcomes_filtered = filter_out_nans(x, outcomes)
    x_filtered = np.array(x_filtered)
    outcomes_filtered = np.array(outcomes_filtered)
    outcomes_bin = np.array(binarize_outcomes(outcomes_filtered))
    good_x = x_filtered[np.where((outcomes_bin))]
    bad_x = x_filtered[np.where((1-outcomes_bin))]
    if similarity_type == 'distance':
        good_cutoff = min(good_x)
        num_bad_cutoff = len(bad_x[bad_x < good_cutoff])        
    elif similarity_type =='similarity':
        good_cutoff = max(good_x)
        num_bad_cutoff = len(bad_x[bad_x > good_cutoff])
    else:
        print('similarity_type must be either "distance" or "similarity"')
    return good_cutoff, num_bad_cutoff

    
    
