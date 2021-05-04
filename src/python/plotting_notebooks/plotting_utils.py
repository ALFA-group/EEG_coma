import pandas as pd
import numpy as np
import seaborn
import matplotlib
import matplotlib.pyplot as plt 
import sys
sys.path.append('..')
import utils
import seaborn

# Various utilities for plotting lines in many colors

def find_contiguous_colors(colors):
    # finds the continuous segments of colors and returns those segments
    segs = []
    curr_seg = []
    prev_color = ''
    for c in colors:
        if c == prev_color or prev_color == '':
            curr_seg.append(c)
        else:
            segs.append(curr_seg)
            curr_seg = []
            curr_seg.append(c)
        prev_color = c
    segs.append(curr_seg) # the final one
    return segs
 
def plot_multicolored_lines(x, y,colors, ax):
    segments = find_contiguous_colors(colors)
    _ = plt.figure()
    start= 0
    for seg in segments:
        end = start + len(seg)
        l, = ax.plot(x[start:end+1],y[start:end+1],lw=1,c=seg[0]) 
        start = end
        
def plot_colored_line(x, y, coloring, color_list, ax):
    # coloring is array of indices into color_list
    colors = [color_list[c] for c in coloring]
    plot_multicolored_lines(x, y, colors, ax)