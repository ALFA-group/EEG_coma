import math
import numpy as np

def scale_dtw_exp(dtw_arr, param):
    exponent = dtw_arr / param
    denom = np.power(math.e * np.ones(len(dtw_arr)), exponent) 
    return 1/denom

def scale_xcorr_exp(xcorr_arr, param):
    # shift according to the minimum xcorr value, -4.0, so that it's between 0 and 1 
    exponent = (xcorr_arr + 4.0) / param
    denom = np.power(math.e * np.ones(len(xcorr_arr)), exponent)
    return 1.0-1.0/denom

def scale_dtw_sigmoid(dtw_arr):
    exponent = (dtw_arr - 500.0)/100.0
    pwr = np.power(math.e * np.ones(len(dtw_arr)), exponent)
    return 1.0 / (1.0 + pwr)

def scale_xcorr_sigmoid(xcorr_arr):
    exponent = (500.0 - xcorr_arr)/100.0
    pwr = np.power(math.e * np.ones(len(xcorr_arr)), exponent)
    return 1.0 / (1.0 + pwr)

def scale_dtw_linear(arr):
    return 1 - arr/ 1020.0

def scale_xcorr_linear(arr):
    return arr/ 945.0

def scale_arr(arr, similarity_fn, scale_fn='exp', param=None):
    if scale_fn not in ['exp', 'sigmoid', 'noscale', 'linear']:
        print('scale_fn must be one of "exp", "linear", "sigmoid", or "noscale"')
    if scale_fn=='noscale':
        return arr
    if scale_fn=='dtw' and param is None:
        param = 100.0
    if similarity_fn=='dtw':
        if scale_fn=='exp':
            return scale_dtw_exp(arr, param)
        elif scale_fn=='sigmoid':
            return scale_dtw_sigmoid(arr)
        elif scale_fn=='linear':
            return scale_dtw_linear(arr)
    elif similarity_fn=='xcorr':
        if scale_fn=='exp':
            return scale_xcorr_exp(arr, param)
        elif scale_fn=='sigmoid':
            return scale_xcorr_sigmoid(arr)
        elif scale_fn=='linear':
            return scale_xcorr_linear(arr)
    else:
        print "similarity fn must be 'dtw' or 'xcorr'"
