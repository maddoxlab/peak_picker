#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 14 15:04:01 2019

@author: mpolonenko
"""
# %%
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from expyfun.io import write_hdf5, read_hdf5
import datetime
import json
# import random

# %% user settings
opath = '/mnt/data/abr_rates_pips/peaks/'
eeg_file = 'example_data.hdf5'

experiment_str = 'pABRrates'
marker = 'mjp_'  # initials of peak picker
peak = 'V'  # TODO: update code to allow multiple peaks at a time

data = read_hdf5(opath + eeg_file)
# subjects = data['subjects']  # these were randomly chosen for 20 subjects
subjects = np.arange(len(data['subjects']))
subject_index = {si: i for i, si in enumerate(subjects)}
subjects_pick = subjects  # choose which subjects to do (ie if not all at once)
# subjects_pick = random.sample(subjects, 3)

overwrite_file = True
save_fig = True
save_hdf5 = True
save_txt = True

# %% settings
x_min = -5  # ms
x_max = 45  # ms

ear_shifts = [0, x_max - x_min]  # to shift the right ear on the figure
ear_colors = ['b', 'r']

lw = [1, 2]  # when not marked/marked (to help see which ones are not done yet)
y_display = 0.25  # how close the waveforms are plotted
picker_size = [3, 15]

# %% load data
frequencies = data['frequencies']
intensities = data['intensities']
rates = data['rates']
ears = data['ears']
t = data['t']
fs = data['fs']
t_ms = data['t_ms']
w_all = data['w']  # matrix shape: (subject, rate, level, ear, freq, time)

# %% define functions


def multipage(filename, figs=None, dpi=200):
    pp = PdfPages(filename)
    if figs is None:
        figs = [plt.figure(n) for n in plt.get_fignums()]
    for fig in figs:
        fig.savefig(pp, format='pdf')
    pp.close()


def onpick(event):
    global points_clicked
    global latency
    global amplitude
    thisline = event.artist
    label = thisline.get_label()

    xdata, ydata = thisline.get_data()
    if label[:8] != 'landmark':
        ind = event.ind
        points = np.array([xdata[ind], ydata[ind]])
        plt.plot(points[0], points[1], 'k+-', markersize=12, lw=1.5,
                 picker=True, pickradius=picker_size[1],
                 label='landmark' + label)
    else:
        thisline.remove()
        label = label[8:]

    for ch in ax.get_children():
        if len(str(ch.get_label())) >= 8 and str(
                ch.get_label())[:8] == 'landmark':
            ch.set_data((np.array([d[0]]) for d in ch.get_data()))

    points_clicked[label] = np.array([ch.get_data() for
                                      ch in ax.get_children() if
                                      ch.get_label() == 'landmark' + label])[
                                          ..., 0]

    if label[:8] == 'landmark':
        parent_label = label[8:]
    else:
        parent_label = label

    parent_line = ax.get_children()[[a.get_label() for a in
                                     ax.get_children()].index(parent_label)]

    if len(points_clicked[label]) == 2:
        if np.argmin(points_clicked[label][:, 0]) == 1:  # if in wrong order
            points_clicked[label] = points_clicked[label][::-1]  # flip it
        latency[label] = points_clicked[label][0, 0] - x_shift[label]
        amplitude[label] = points_clicked[label][0, 1] - points_clicked[
            label][1, 1]
        parent_line.set_linewidth(lw[1])
    else:
        latency[label] = np.nan
        amplitude[label] = np.nan
        parent_line.set_linewidth(lw[0])
    print(points_clicked[label])


def onclose(event):
    global time_picking
    global end_time
    end_time = datetime.datetime.now()
    time_picking = (end_time - start_time).total_seconds()
    print('Time to pick peaks:' + str(time_picking / 60) + ' min')
    print(latency)
    print(amplitude)
    if save_fig:
        plt.savefig(opath + marker + experiment_str + '_{:03}_{}.png'.format(
            subject, peak))
    if save_hdf5:
        write_hdf5(opath + marker + experiment_str + '_{:03}_{}.hdf5'.format(
            subject, peak), dict(
                # points_clicked=points_clicked,
                # x_shift=x_shift,
                # y_shift=y_shift,
                time_picking=time_picking,
                latency=latency,
                amplitude=amplitude), overwrite=overwrite_file)
    if save_txt:
        with open(opath + marker + experiment_str + '_{:03}_{}.txt'.format(
                subject, peak), 'w') as outfile:
            json.dump(dict(latency=latency, amplitude=amplitude), outfile)


# %% plot the waveforms and allow interactive peak picking

for subject in subjects_pick:
    w = w_all[subject_index[subject]]
    tmin = int((x_min / 1e3 - t[0]) * fs)
    tmax = int((x_max / 1e3 - t[0]) * fs)
    t0 = int(t[0] * fs)

    plt.ion()
    points_clicked = {}
    amplitude = {}
    latency = {}
    y_shift = {}
    x_shift = {}

    fig = plt.figure(figsize=(12, 9))
    for sh in ear_shifts:
        plt.axvline(sh + t_ms[t0], color='k', ls=':', lw=1)
        for grid in [10, 20, 30, 40]:
            plt.axvline(sh + t_ms[t0] + grid, color='k', ls=':', lw=1,
                        alpha=0.2)
    ax = fig.add_subplot(111)
    ax.set_ylabel(r'$\mu$V')
    ax.set_xlabel('Time (ms)')
    ax.set_title('subject: {:03}'.format(subject))
    counter = 0
    for r in range(len(rates)):
        for li in range(len(intensities)):
            for f in range(5):
                for e, sh, c in zip(range(2), ear_shifts, ear_colors):
                    line, = ax.plot(
                        sh + t_ms[tmin:tmax], y_display * counter +
                        w[r, li, e, f, tmin:tmax], color=c, lw=lw[0],
                        picker=True, pickradius=picker_size[0],
                        label='s{:03}_r{:03}_l{:2}_e{:1}_f{:1}_{}'.format(
                            subject, rates[r], intensities[li], e, f, peak))
                    x_shift[line.get_label()] = sh
                    y_shift[line.get_label()] = counter * y_display
                    amplitude[line.get_label()] = np.nan
                    latency[line.get_label()] = np.nan
                counter += 1
            counter += 1
    fig.canvas.mpl_connect('pick_event', onpick)
    start_time = datetime.datetime.now()
    fig.canvas.mpl_connect('close_event', onclose)
    go_to_next = input('Press enter!')
