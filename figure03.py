"""
Contents: Script that reproduces figure 3 from the manuscript and saves it to the figures folder.

These files serve as the companion to the manuscript:

    "Continuous peak-period estimates from discrete surface-wave spectra", Smit et al., 2023

For details we on methods and results, please refer to the manuscript.

Copyright (C) 2023
Sofar Ocean Technologies

Authors: Pieter Bart Smit
"""

from roguewavespectrum.parametric import create_parametric_frequency_spectrum
import matplotlib.pyplot as plt
import numpy as np
import os
import pickle

# --- Plotting functions ---
def get_periods(peak_periods, standard_deviations, kind='gaussian'):
    """
    Helper function to calculate peak periods for the different methods based on width/type of spectrun
    :param peak_periods: peak periods of the true distribution
    :param standard_deviations: standard deviation of gaussia distribution (N/A for jonswap)
    :param kind: jonswap or gaussian
    :return:
    """
    truth = np.zeros((len(standard_deviations), len(peak_periods)))
    downsampled = np.zeros((len(standard_deviations), len(peak_periods)))
    interpolated = np.zeros((len(standard_deviations), len(peak_periods)))
    natural = np.zeros((len(standard_deviations), len(peak_periods)))

    for ind_sd, standard_deviation in enumerate(standard_deviations):
        for ind_per, period in enumerate(peak_periods):
            true_spectrum = create_parametric_frequency_spectrum(interpolated_frequencies, period, 1, kind,
                                                                 standard_deviation_hertz=standard_deviation)
            downsampled_spectrum = true_spectrum.downsample(sampled_frequencies)

            truth[ind_sd, ind_per] = true_spectrum.peak_period().values
            downsampled[ind_sd, ind_per] = downsampled_spectrum.peak_period().values
            interpolated[ind_sd, ind_per] = downsampled_spectrum.peak_period(use_spline=True).values
            natural[ind_sd, ind_per] = downsampled_spectrum.peak_period(use_spline=True,monotone_interpolation=False).values

    return {'target': truth, 'downsampled_error': np.abs(downsampled - truth) / truth,
            'interpolated_error': np.abs(interpolated - truth) / truth,'downsampled':downsampled,'monotone':interpolated,'natural':natural }





# PLOTTING CODE
def plot( periods, data, kind, _range, diff,xlabel=None,ylabel=None,plot_legend=True ):
    if diff:
        target = data[kind]['target'][0, :]
    else:
        target = 0.0

    x = periods
    y = data[kind]['downsampled'][0, :]
    plt.plot(x, y-target, color=[0.6,0.6,0.6],label='linear/piecewise')

    y = data[kind]['target'][0, :]
    plt.plot(x, y-target, color='k',label='target')
    for jj in _range:
        for spline_kind in ['natural','monotone']:
            y = data[kind][spline_kind][jj,:]
            if not kind =='gaussian':
                string = f"{spline_kind}"
            else:
                string = f"{spline_kind} {frequency_width[jj]/frequency_step:2.1f} $\Delta f$"
            plt.plot(x, y-target,label=string)
    plt.grid('on')
    if plot_legend:
        plt.legend(fontsize=8)
    plt.xlim( (0.05,0.15))

    if xlabel:
        plt.xlabel(xlabel)
    else:
        plt.gca().axes.xaxis.set_ticklabels([])

    if ylabel:
        plt.ylabel(ylabel)
    else:
        plt.gca().axes.yaxis.set_ticklabels([])

def get_data(peak_frequency, frequency_width):
    # Running is somewhat slow - so we save locally the results after the first time.
    if os.path.exists('data/data.zip'):
        with open("data/data.pkl", "rb") as file_handle:
            data = pickle.loads(file_handle)
    else:
        # Lets calculate
        data = {}
        data['gaussian'] = get_periods(peak_frequency, frequency_width, kind='gaussian')
        data['jonswap'] = get_periods(peak_frequency, [0.0], kind='jonswap')
        data['pm'] = get_periods(peak_frequency, [0.0], kind='pm')

        with open("data/data.pkl", "wb") as file_handle:
            pickle.dump(data, file_handle)


    return data

# --- Main script ---
if __name__ == '__main__':

    # --- Setup ---

    # the coarse frequency step
    frequency_step = 0.01

    # frequency limits
    frequency_limits = [0.01, 0.5]

    # the high resolution frequency step used for integration
    frequency_step_highres = frequency_step / 100

    # frequency band
    frequency_band = frequency_limits[1] - frequency_limits[0]

    # Frequencies we sample the distribution at.
    sampled_frequencies = np.linspace(frequency_limits[0], frequency_limits[1], int(frequency_band / frequency_step) + 1,
                                      endpoint=True)

    # frequencies we interpolate at
    interpolated_frequencies = np.linspace(frequency_limits[0], frequency_limits[1],
                                           int(frequency_band / frequency_step_highres) + 1, endpoint=True)

    # Peak frequencies we consider
    peak_frequency = np.linspace( 5 * frequency_step, 15 * frequency_step, 101)

    # Frequency widths
    frequency_width = [2*frequency_step,frequency_step,frequency_step/2,frequency_step/10]

    # Get data to plot
    data = get_data(peak_frequency, frequency_width)

    # -- Plotting --
    figure = plt.figure( figsize=[7,5],dpi=300 )
    plt.subplot( 2,3,1)
    plot( peak_frequency,data,'gaussian', [1], False,plot_legend=False, ylabel= '$T_{{peak}}$ [s]')

    plt.ylim([5,20])

    plt.subplot( 2,3,2)
    plot( peak_frequency,data,'jonswap', range(0,1 ), False )
    plt.ylim([5,20])

    plt.subplot( 2,3,3)
    plot( peak_frequency,data,'pm', range(0,1 ), False,plot_legend=False )
    plt.ylim([5,20])

    plt.subplot( 2,3,4)
    plot( peak_frequency,data,'gaussian', [1], True,plot_legend=False,ylabel='$\Delta T$ [s]', xlabel='$f_{{peak}}$ [Hz]' )
    plt.ylim([-1.5,1.5])

    plt.subplot( 2,3,5)
    plot( peak_frequency,data,'jonswap', range(0,1 ), True,plot_legend=False,xlabel='$f_{{peak}}$ [Hz]' )
    plt.ylim([-1.5,1.5])

    plt.subplot( 2,3,6)
    plot( peak_frequency,data,'pm', range(0,1 ), True,plot_legend=False,xlabel='$f_{{peak}}$ [Hz]' )
    plt.ylim([-1.5,1.5])

    plt.tight_layout()
    os.makedirs('./figures',exist_ok=True)
    figure.savefig('./figures/figure03.png')

    plt.show()
