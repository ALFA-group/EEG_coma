import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import scipy
import IPython
import string
import os
import plotly
import plotly.figure_factory
sns.set(color_codes=True)
plotly.offline.init_notebook_mode(connected=True)

# Various utilities for plotting histograms

def describe_array(arr, title, xlabel, ylabel, bins=None, zoom=None, rug=True, kde=False, save=False, ylim=None, xlim=None, norm_hist=False):
    # Simple histogram using matplotlib 
    if zoom is not None:
        #arr = [x for x in arr if x>=zoom[0] and x<=zoom[1]]
        arr = arr[np.where(arr >=zoom[0])]
        arr = arr[np.where(arr<=zoom[1])]
    if len(arr)==0:
        print('Title: {} - Empty arr'.format(title))
        return
    print('mean: {}, median: {}, range: ({}, {}), num elts: {}'.format(np.average(arr), 
                                                              np.median(arr), 
                                                              np.min(arr), np.max(arr), 
                                                              len(arr)))
    p = sns.distplot(arr, kde=kde, rug=rug, bins=bins, norm_hist=norm_hist)
    ax = plt.gca()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    if ylim is not None:
        ax.set_ylim(ylim[0], ylim[1])
    if xlim is not None:
        ax.set_xlim(xlim[0], xlim[1])
    plt.show()
    if save:
        image_name = string.replace(string.replace(title, ' ', '_'), '-', '') + '.png'
        p.figure.savefig(os.path.join(title), bbox_inches='tight')
    return ax

def describe_array_plotly(arr, title, xlabel, ylabel, rug_labels=None, bin_size=None, zoom=None, rug=True, kde=False):
    # simple histogram, using plotly instead of matplotlib
    if zoom is not None:
        if rug_labels is not None:
            zoomed_arr = []
            zoomed_labels = []
            for i, x in enumerate(arr):
                if x>=zoom[0] and x<=zoom[1]:
                    zoomed_arr.append(x)
                    zoomed_labels.append(rug_labels[i])
            arr = zoomed_arr
            rug_labels = zoomed_labels
        else:
            arr = [x for x in arr if x>=zoom[0] and x<=zoom[1]]
    if len(arr)==0:
        print('Title: {} - Empty arr'.format(title))
        return
    print('mean: {}, median: {}, range: ({}, {}), num elts: {}'.format(np.average(arr), 
                                                              np.median(arr), 
                                                              np.min(arr), np.max(arr), 
                                                              len(arr)))
    if len(arr)==1:
        print('N=1, no histogram')
        return
    hist_data = [arr]
    fig = plotly.figure_factory.create_distplot(
        hist_data, group_labels = ['data'], rug_text=[rug_labels], show_curve=kde, show_rug=rug, bin_size=[bin_size])
    fig['layout'].update(title=title)
    fig['layout']['xaxis1'].update(title=xlabel) # Plot!
    fig['layout']['yaxis1'].update(title=ylabel) # Plot!
    fig['layout'].update(height=400, width=500)
    return plotly.offline.iplot(fig)

def describe_arrays(arrs, titles, xlabel, ylabel, zoom=None, rug=True, kde=False, rug_labels=None, bin_size=None, bins=None, save=False, use_plotly=False):
    # Creates historams of many arrays
    #
    # Note: arrs, titles, xlabel, ylabel, zoom, rug, kde are for both plotly=True and plotly=False
    # rug_labels and bin_size can only be used with plotly=True
    # bins and save can only be used with plotly=False
    if use_plotly:
        if bins is not None:
            print('bins will be ignored since use_plotly=True; to change binning use "bin_size" parameter')
        if save is not None:
            print('save will be ignored since use_plotly=True')
    else:
        if rug_labels is not None:
            print('rug labels will be ignored since use_plotly=False')
        if bin_size is not None:
            print('bin_size will be ignored since use_plotly=False; to change binning with plotly use "bins" parameter')
    i = 0
    while i>=0 and i<len(arrs):
        IPython.display.clear_output()
        arr = arrs[i]
        title = titles[i]
        if use_plotly:
            if rug_labels is not None:
                plot_rug_labels = rug_labels[i]
            else:
                plot_rug_labels = None
            describe_array_plotly(arr, title, xlabel, ylabel, rug_labels=plot_rug_labels, bin_size=bin_size, zoom=zoom, rug=rug, kde=kde)
        else:
            describe_array(np.array(arr), title, xlabel, ylabel, bins=bins, zoom=zoom, rug=rug, kde=kde, save=save)

        inp = raw_input('Prev plot-"b", Exit-"e", Next plot-Any other key')
        if inp=='e':
            break
        elif inp=='b':
            i-=1
        else:
            i+=1
    IPython.display.clear_output()
    
def precounted_histogram(counts, bins, title, xlabel, ylabel, zoom=None, ylim=None, xlim=None):
    # Create a histogram, given a list of bins and counts
    # counts should be an array of length n 
    # bins should be an array of length n+1 representing the bin edges
    sum_nums = 0
    N = sum(counts)  # total number of numbers
    n = 0            # number of numbers seen so far
    for i in range(len(counts)):
        count = counts[i]
        bin_range = bins[i], bins[i+1]
        bin_middle = (bins[i] + bins[i+1])/2.0
        sum_nums += bin_middle * count
        if n < N/2 and n+count >=N/2:
            median = bin_middle
        n += count
    mean = sum_nums / N
            
    print('estimate of mean: {}, estimate of median: {}, range: ({}, {}), num elts: {}'.format(mean, 
                                                              median, 
                                                              bins[0], bins[-1], 
                                                              N))
    h = plt.hist(bins[:-1], bins, weights=counts)
    ax = plt.gca()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    if ylim is not None:
        ax.set_ylim(ylim[0], ylim[1])
    if xlim is not None:
        ax.set_xlim(xlim[0], xlim[1])
    plt.show()
    return h, ax
    
def precounted_histograms(counts_l, bins_l, title, xlabel, ylabel, hist_labels, zoom=None, ylim=None, xlim=None, print_stats=True):
    # plots multiple precounted histograms on the same axis for comparison
    # counts_l is a list of counts arrays
    # bins_l is a list of bins arrays
    # hist_labels is a list of labels corresponding to each histogram
    for counts, bins, hist_label in zip(counts_l, bins_l, hist_labels):
        if print_stats:
            sum_nums = 0
            N = sum(counts)  # total number of numbers
            n = 0            # number of numbers seen so far
            for i in range(len(counts)):
                count = counts[i]
                bin_range = bins[i], bins[i+1]
                bin_middle = (bins[i] + bins[i+1])/2.0
                sum_nums += bin_middle * count
                if n < N/2 and n+count >=N/2:
                    median = bin_middle
                n += count
            mean = sum_nums / N
            print('{} : ~mean: {}, ~median: {}, range: ({}, {}), num elts: {}'.format(hist_label, mean, 
                                                                      median, 
                                                                      bins[0], bins[-1], 
                                                                      N))
        plt.hist(bins[:-1], bins, weights=counts, alpha=0.5, label=hist_label)
    ax = plt.gca()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    if ylim is not None:
        ax.set_ylim(ylim[0], ylim[1])
    if xlim is not None:
        ax.set_xlim(xlim[0], xlim[1])
    plt.legend()
    plt.show()
    return ax
    
def precounted_percentile(counts, bins, percentile):
    # computes a given percentile (0-100) of an array expressed as a histogram
    sum_nums = 0
    N = sum(counts)  # total number of numbers
    n = 0            # number of numbers seen so far
    target_mass = N * percentile / 100.
    if percentile==0:
        return bins[0]
    if percentile==100:
        return bins[-1]
    for i in range(len(counts)):
        count = counts[i]
        bin_range = bins[i], bins[i+1]
        bin_middle = (bins[i] + bins[i+1])/2.0
        sum_nums += bin_middle * count
        if n < target_mass and n+count >=target_mass:
            desired_percentile = bin_middle
            return bin_middle
        n += count
    
def precounted_percentiles(counts, bins, percentiles):
    # computes a list of given percentiles (0-100) of an array expressed as a histogram
    return [precounted_percentile(counts, bins, p) for p in percentiles]
        
