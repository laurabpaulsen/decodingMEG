"""
Creates plots of the decoding results.

Usage: python plots.py
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import binom
from decoding import prep_data

colours = ['#0063B2FF', '#5DBB63FF']

# set font for all plots
plt.rcParams['font.family'] = 'times new roman'
plt.rcParams['image.cmap'] = 'RdBu_r'
plt.rcParams['image.interpolation'] = 'bilinear'
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['legend.title_fontsize'] = 12
plt.rcParams['figure.titlesize'] = 14
plt.rcParams['figure.dpi'] = 300


def chance_level(alpha = 0.001):
    Xbin, ybin, Xsesh, ysesh = prep_data()
    del Xbin, ybin, Xsesh
    n_trials = [len(np.concatenate(i)) for i in ysesh]
    chance_level = []
    for i in range(len(n_trials)):
        n, p = n_trials[i], 0.5
        k = binom.ppf(1-alpha, n, p)
        chance_level.append(k/n)
    return chance_level


def plot_tgm(X, vmin = 30, vmax = 70, savepath = None, chance_level = None):
    if not X.shape == (250, 250):
        raise ValueError('X must be 250, 250')

    fig, ax = plt.subplots(1, 1, figsize = (7, 7), dpi = 400)

    im = ax.imshow(X*100, vmin = vmin, vmax = vmax, origin = 'lower')
    if chance_level is not None:
        plt.contour(X*100, levels=[chance_level*100], colors='k', alpha = 0.5, linewidths=1, linestyles='--')


    ax.set_yticks(np.arange(0, 251, step=50), [0. , 0.2, 0.4, 0.6, 0.8, 1. ])
    ax.set_xticks(np.arange(0, 251, step=50), [0. , 0.2, 0.4, 0.6, 0.8, 1. ])

    cb = plt.colorbar(im, ax = ax, location = 'top', shrink = 0.5)
    cb.set_label(label = 'Accuracy (%)')
    

    fig.supxlabel('Time (s)')
    fig.supylabel('Time (s)')

    plt.tight_layout()

    if savepath is not None:
        plt.savefig(savepath)
    
    plt.close()

def tgm_cross(cross, savepath = None):

    cm = 1/2.54  # centimeters in inches
    figsize = (18*cm, 18*cm)

    vmin = 0.35
    vmax = 0.65

    fig, axs = plt.subplots(cross.shape[0], cross.shape[1], figsize = figsize, sharey=True, sharex = True)

    for i in range(cross.shape[0]):
        for j in range(cross.shape[1]):
            axs[i, j].imshow(cross[i, j], vmin = vmin, vmax = vmax, origin = 'lower')
            axs[i, j].set_xticks(np.arange(0, 251, step=50), [0. , 0.2, 0.4, 0.6, 0.8, 1. ])
            axs[i, j].set_yticks(np.arange(0, 251, step=50), [0. , 0.2, 0.4, 0.6, 0.8, 1. ])
            # rotate x ticks a bit
            for tick in axs[i, j].get_xticklabels():
                tick.set_rotation(90)

    for j in range(cross.shape[1]):
        axs[j, 0].set_ylabel(f'Session {j+1}')
        axs[0, j].set_title(f'Session {j+1}')
    fig.supylabel('Testing session')
    fig.suptitle('Training session')
    plt.tight_layout()

    if savepath is not None:
        plt.savefig(savepath)

    plt.close()

def diagonal_cross(cross, savepath = None):
    vmin = 0.40
    vmax = 0.70
    cm = 1/2.54  # centimeters in inches
    figsize = (18*cm, 7*cm)
    fig, ax = plt.subplots(2, 4, figsize = figsize)
    for i, a in enumerate(ax.flatten()):
        if i < 7:
            for j in range(cross.shape[1]):
                if j == 0 and i == 0:
                    a.axhline(y = 0.5333333333333333, color = 'k', linewidth = 0.3, linestyle = '--', alpha = 0.4, label = 'Chance')
                else:
                    a.axhline(y = 0.5333333333333333, color = 'k', linewidth = 0.3, linestyle = '--', alpha = 0.4)
                a.plot(cross[i, j].diagonal(), linewidth = 0.4, alpha = 0.7, label = f'Session {j+1}')
                a.set_title(f'Training on session {i+1}')
                a.set_xticks(np.arange(0, 251, step=50), [0. , 0.2, 0.4, 0.6, 0.8, 1. ])
                a.set_ylim(vmin, vmax)
                # change fontsize of y ticks
                a.tick_params(axis='y')

    
    # get the legend labels from the first axis and plot them on the last axis
    handles, labels = ax[0, 0].get_legend_handles_labels()
    ax[-1, -1].axis('off')
    ax[-1, -1].legend(handles, labels, loc = 'center', title = 'Testing')
    #ax[-1, -1].legend(loc = 'upper right', title = 'Testing on \n session', title_fontsize = 6, fontsize = 6)

    plt.tight_layout()

    if savepath is not None:
        plt.savefig(savepath)
    
    plt.close()

def plot_tgm_difference(a1, a2, savepath = None, cross = False):
    vmin = -0.025*100
    vmax = 0.025*100

    if a1.shape and a2.shape != (7, 7, 250, 250):
        raise ValueError('Input arrays must be of shape (7, 7, 250, 250)')
    if not cross:
        mean_a1 = np.mean(a1, axis = (0, 1))
        mean_a2 = np.mean(a2, axis = (0, 1))
    else: 
        # remove the same session training and testing
        for i in range(len(a1)):
            a1[i, i] = np.nan
            a2[i, i] = np.nan
        mean_a1 = np.nanmean(a1, axis = (0, 1))
        mean_a2 = np.nanmean(a2, axis = (0, 1))


    fig, axs = plt.subplots(1, 1, figsize = (7, 7))

    im = axs.imshow(mean_a1*100 - mean_a2*100, vmin = vmin, vmax = vmax, origin = 'lower')
    # show the colorbar on top
    cb = plt.colorbar(im, ax = axs, location = 'top', shrink = 0.5)
    cb.set_label(label = 'Accuracy difference (%)')

    # change y and x ticks
    axs.set_xticks(np.arange(0, 251, step=50), [0. , 0.2, 0.4, 0.6, 0.8, 1. ])
    axs.set_yticks(np.arange(0, 251, step=50), [0. , 0.2, 0.4, 0.6, 0.8, 1. ])

    axs.set_xlabel('Training time (s)')
    axs.set_ylabel('Testing time (s)')
    plt.tight_layout()


    if savepath is not None:
        plt.savefig(savepath)

    plt.close()

def plot_diagonal_difference(a1, a2, savepath = None, cross = False):

    if a1.shape and a2.shape != (7, 7, 250, 250):
        raise ValueError('Input arrays must be of shape (7, 7, 250, 250)')

    if not cross:
        mean_a1 = np.mean(a1, axis = (0, 1))
        mean_a2 = np.mean(a2, axis = (0, 1))
    else: 
        # remove the same session training and testing
        aa1 = np.copy(a1)
        aa2 = np.copy(a2)
        for i in range(len(a1)):
            aa1[i, i] = np.nan
            aa2[i, i] = np.nan
        mean_a1 = np.nanmean(aa1, axis = (0, 1))
        mean_a2 = np.nanmean(aa2, axis = (0, 1))
    

    fig, axs = plt.subplots(1, 1, figsize = (7, 4))

    axs.plot(np.arange(0, 250), mean_a1.diagonal()*100 - mean_a2.diagonal()*100, linewidth = 2, alpha = 0.7)
    axs.axhline(y = 0, color = 'k', linewidth = 1, linestyle = '--', alpha = 0.4)
    axs.set_xlabel('Time (s)')
    axs.set_ylabel('Accuracy difference (%)')


    # change x ticks
    axs.set_xticks(np.arange(0, 251, step=50), [0. , 0.2, 0.4, 0.6, 0.8, 1. ])
    plt.tight_layout()
    if savepath is not None:
        plt.savefig(savepath)

    plt.close()

def average_tgm(a1, chance, vmin = 35, vmax = 65, savepath = None, cross = False):
    if not cross:
        mean_a1 = np.mean(a1, axis = (0, 1))
    else:
        a = a1.copy()
        # remove the same session training and testing
        for i in range(len(a1)):
            a[i, i] = np.nan
        mean_a1 = np.nanmean(a, axis = (0, 1))

    fig, axs = plt.subplots(1, 1, figsize = (7, 7))


    im = axs.imshow(mean_a1*100, vmin = vmin, vmax = vmax, origin = 'lower')
    # show the colorbar on top
    cb = plt.colorbar(im, ax = axs, location = 'top', shrink = 0.5)
    cb.set_label(label = 'Accuracy (%)')
    plt.contour(mean_a1*100, levels=[chance*100], colors='k', alpha = 0.5, linewidths=1, linestyles='--')

    # change y and x ticks
    axs.set_xticks(np.arange(0, 251, step=50), [0. , 0.2, 0.4, 0.6, 0.8, 1. ])
    axs.set_yticks(np.arange(0, 251, step=50), [0. , 0.2, 0.4, 0.6, 0.8, 1. ])

    axs.set_xlabel('Training time (s)')
    axs.set_ylabel('Testing time (s)')
    plt.tight_layout()

    if savepath is not None:
        plt.savefig(savepath)

    plt.close()

def plot_all_diagonal(a1, savepath = None, ymin = 35, ymax = 65, cross = False):
    if not cross:
        mean_a1 = np.mean(a1, axis = 0)
    else:
        # remove the same session training and testing
        a = a1.copy()
        for i in range(len(a)):
            a[i, i] = np.nan
        mean_a1 = np.nanmean(a, axis = 0)
    
    fig, axs = plt.subplots(1, 1, figsize = (7, 4))
    for i in range(mean_a1.shape[0]):
        diag = mean_a1[i, :, :].diagonal()*100 # percentage
        if not cross:
            axs.plot(np.arange(0, 250), diag, linewidth = 1, alpha = 0.7, label = f'{i+1}')
        else:
            axs.plot(np.arange(0, 250), diag, linewidth = 1, alpha = 0.7, label = f'{i+1}')
    # plot mean
    axs.plot(np.arange(0, 250), np.mean(mean_a1, axis = 0).diagonal()*100, linewidth = 1.5, alpha = 1, color = 'k',  label = 'Mean')  

    axs.set_xticks(np.arange(0, 251, step=50), [0. , 0.2, 0.4, 0.6, 0.8, 1. ])
    axs.set_ylabel('Accuracy (%)')
    axs.set_xlabel('Time (s)')
    if not cross:
        axs.legend(loc = 'upper right', title = 'Session')
    else:
        axs.legend(loc = 'upper right', title = 'Train session')

    plt.tight_layout()
    
    if savepath is not None:
        plt.savefig(savepath)
    
    plt.close()

def within_sesh_cross_tgm(X, chance, savepath = None, vmin = 35, vmax = 65):

    mean_a1 = np.mean(X.diagonal(), axis = 2)

    fig, axs = plt.subplots(1, 1, figsize = (7, 7))
    im = axs.imshow(mean_a1*100, vmin = vmin, vmax = vmax, origin = 'lower')
    # show the colorbar on top
    cb = plt.colorbar(im, ax = axs, location = 'top', shrink = 0.5)
    cb.set_label(label = 'Accuracy (%)')
    plt.contour(mean_a1*100, levels=[chance*100], colors='k', alpha = 0.5, linewidths=1, linestyles='--')

    # change y and x ticks
    axs.set_xticks(np.arange(0, 251, step=50), [0. , 0.2, 0.4, 0.6, 0.8, 1. ])
    axs.set_yticks(np.arange(0, 251, step=50), [0. , 0.2, 0.4, 0.6, 0.8, 1. ])

    axs.set_xlabel('Training time (s)')
    axs.set_ylabel('Testing time (s)')
    plt.tight_layout()

    if savepath is not None:
        plt.savefig(savepath)
    
    plt.close()

def within_sesh_cross_tgm_diff(X1, X2, savepath = None):
    vmin = -0.035*100
    vmax = 0.035*100
    # get diagonal = same session for testing and training
    mean_a1 = np.mean(X1.diagonal(), axis = 2)
    mean_a2 = np.mean(X2.diagonal(), axis = 2)

    fig, axs = plt.subplots(1, 1, figsize = (7, 7))

    im = axs.imshow(mean_a1*100 - mean_a2*100, vmin = vmin, vmax = vmax, origin = 'lower')
    # show the colorbar on top
    cb = plt.colorbar(im, ax = axs, location = 'top', shrink = 0.5)
    cb.set_label(label = 'Accuracy difference (%)')

    # change y and x ticks
    axs.set_xticks(np.arange(0, 251, step=50), [0. , 0.2, 0.4, 0.6, 0.8, 1. ])
    axs.set_yticks(np.arange(0, 251, step=50), [0. , 0.2, 0.4, 0.6, 0.8, 1. ])

    axs.set_xlabel('Training time (s)')
    axs.set_ylabel('Testing time (s)')
    plt.tight_layout()


    if savepath is not None:
        plt.savefig(savepath)
    
    plt.close()


def within_sesh_diag_diff(X1, X2, savepath = None):
    mean_a1 = np.mean(X1.diagonal(), axis = 2)
    mean_a2 = np.mean(X2.diagonal(), axis = 2)

    fig, axs = plt.subplots(1, 1, figsize = (7, 4))

    axs.plot(np.arange(0, 250), mean_a1.diagonal()*100 - mean_a2.diagonal()*100, linewidth = 2, alpha = 0.7)
    axs.axhline(y = 0, color = 'k', linewidth = 1, linestyle = '--', alpha = 0.4)
    axs.set_xlabel('Time (s)')
    axs.set_ylabel('Accuracy difference (%)')


    # change x ticks
    axs.set_xticks(np.arange(0, 251, step=50), [0. , 0.2, 0.4, 0.6, 0.8, 1. ])

    plt.tight_layout()
    if savepath is not None:
        plt.savefig(savepath)

def compare_diagonals(dX, savepath = None):
    """
    dX: Dictionary of accuracies
    """

    fig, ax  = plt.subplots(1, 1, figsize = (7, 4))

    counter = 0
    for key, value in dX.items():
        ax.plot(np.arange(0, 250), value.diagonal()*100, label = key, linewidth = 1.5, alpha = 0.7, color = colours[counter])
        counter += 1
    
    plt.legend(loc = 'upper right')
    plt.xlabel('Time (s)')
    plt.ylabel('Accuracy (%)')

    # change x ticks
    ax.set_xticks(np.arange(0, 251, step=50), [0. , 0.2, 0.4, 0.6, 0.8, 1. ])

    plt.tight_layout()

    if savepath is not None:
        plt.savefig(savepath)
    
    plt.close()


if __name__ in '__main__':
    lbo = np.load('./accuracies/accuracies_LDA_lbo.npy', allow_pickle=True) # leave batch out
    propb = np.load('./accuracies/accuracies_LDA_prop.npy', allow_pickle=True) # balanced stratified batch
    cross = np.load('./accuracies/cross_decoding_ncv_5.npy', allow_pickle=True).squeeze() # cross session
    cross_sens = np.load('./accuracies/cross_decoding_sens_ncv_5.npy', allow_pickle=True).squeeze() # cross session

    chance_levels = chance_level(alpha = 0.05)
    avg_chance = np.mean(chance_levels)

    # within session decoding cross session
    within_sesh_cross_tgm(cross, avg_chance, savepath = f'./plots/cross_within_tgm_source.png', vmin = 35, vmax = 65)
    within_sesh_cross_tgm(cross_sens, avg_chance, savepath = f'./plots/cross_within_tgm_sens.png', vmin = 35, vmax = 65)
    within_sesh_cross_tgm_diff(cross_sens, cross, savepath = f'./plots/cross_within_tgm_diff.png')
    within_sesh_diag_diff(cross_sens, cross, savepath = f'./plots/cross_within_diag_diff.png')

    # plot session 5 (session with highest variance in sensor space)
    chance_levels = chance_level()
    plot_tgm(cross_sens[4, 4, :, :], savepath = f'./plots/cross_sesh5_sens.png', vmin = 35, vmax = 65, chance_level = chance_levels[4])
    plot_tgm(cross[4, 4, :, :], savepath = f'./plots/cross_sesh5_source.png', vmin = 35, vmax = 65, chance_level = chance_levels[4])
    compare_diagonals({'Source space': cross[4, 4, :, :], 'Sensor space': cross_sens[4, 4, :, :]}, savepath = f'./plots/cross_sesh5_diagonals.png')
    
    # plot session 6 (session with lowest variance in sensor space)
    plot_tgm(cross_sens[5, 5, :, :], savepath = f'./plots/cross_sesh6_sens.png', vmin = 35, vmax = 65, chance_level = chance_levels[5])
    plot_tgm(cross[5, 5, :, :], savepath = f'./plots/cross_sesh6_source.png', vmin = 35, vmax = 65, chance_level = chance_levels[5])
    compare_diagonals({'Source space': cross[5, 5, :, :], 'Sensor space': cross_sens[5, 5, :, :]}, savepath = f'./plots/cross_sesh6_diagonals.png')


    tgm_cross(cross, savepath = f'./plots/cross_session_tgm.png')
    tgm_cross(cross_sens, savepath = f'./plots/cross_session_tgm_sens.png')
    
    diagonal_cross(cross, savepath = f'./plots/cross_session_diagonal.png')
    diagonal_cross(cross_sens, savepath = f'./plots/cross_session_diagonal_sens.png')


    # accuracy difference plots
    plot_tgm_difference(lbo, propb, savepath = f'./plots/within_tgm_difference.png')
    plot_diagonal_difference(lbo, propb, savepath = f'./plots/within_diagonal_difference.png')

    plot_tgm_difference(cross_sens, cross, savepath = f'./plots/cross_tgm_difference.png', cross = True)
    plot_diagonal_difference(cross_sens, cross, savepath = f'./plots/cross_diagonal_difference.png', cross = True)

    # all tgms averaged
    average_tgm(lbo, avg_chance, savepath = f'./plots/average_tgm_lbo.png', vmin = 35, vmax = 65)
    average_tgm(propb, avg_chance, savepath = f'./plots/average_tgm_prop.png',  vmin = 35, vmax = 65)

    average_tgm(cross, avg_chance, savepath = f'./plots/average_tgm_cross.png', vmin = 40, vmax = 60, cross=True)
    average_tgm(cross_sens, avg_chance, savepath = f'./plots/average_tgm_cross_sens.png', vmin = 40, vmax = 60, cross=True)

    # all diagonals
    plot_all_diagonal(lbo, savepath = f'./plots/diagonal_lbo.png', ymin = 35, ymax = 65)
    plot_all_diagonal(propb, savepath = f'./plots/diagonal_prop.png', ymin = 35, ymax = 65)

    plot_all_diagonal(cross, savepath = f'./plots/diagonal_cross.png', ymin = 40, ymax = 60, cross=True)
    plot_all_diagonal(cross_sens, savepath = f'./plots/diagonal_cross_sens.png', ymin = 40, ymax = 60, cross=True)


