"""
Contents: Script that reproduces figures 1 and  from the manuscript and saves it to the figures folder.

These files serve as the companion to the manuscript:

    "Continuous peak-period estimates from discrete surface-wave spectra", Smit et al., 2023

For details we on methods and results, please refer to the manuscript.

Copyright (C) 2023
Sofar Ocean Technologies

Authors: Pieter Bart Smit
"""

from roguewavespectrum import FrequencySpectrum
from roguewavespectrum.parametric import create_parametric_frequency_spectrum
#from roguewave.wavespectra.parametric import create_parametric_frequency_spectrum
import matplotlib.pyplot as plt
import numpy as np
import os


def get_spectra(peak_frequency, standard_deviation, kind='gaussian'):
    """
    Helper function to calculate peak periods for the different methods based on width/type of spectrun
    :param peak_frequencys: peak periods of the true distribution
    :param standard_deviations: standard deviation of gaussia distribution (N/A for jonswap)
    :param kind: jonswap or gaussian
    :return:
    """
    true_spectrum = create_parametric_frequency_spectrum(interpolated_frequencies, peak_frequency, 1, kind,
                                                         standard_deviation_hertz=standard_deviation)
    downsampled_spectrum = true_spectrum.downsample(sampled_frequencies)
    interpolated_spectrum = downsampled_spectrum.interpolate_frequency(interpolated_frequencies, method='spline')
    non_monotone = downsampled_spectrum.interpolate_frequency(interpolated_frequencies, method='spline',
                                                              monotone_interpolation=False)

    return {'target': true_spectrum, 'downsampled': downsampled_spectrum, 'interpolated': interpolated_spectrum,
            'non_monotone': non_monotone}


# PLOTTING CODE
def plot(spectrum: FrequencySpectrum, block=False, freq_scale=1, scale=1, **kwargs):
    x = spectrum.frequency.values / freq_scale
    y = spectrum.variance_density.values / scale

    if block:
        dx = x[2] - x[1]

        xx = []
        yy = []
        for ii in range(len(x)):
            xx += [x[ii] - 0.5 * dx, x[ii] + 0.5 * dx]
            yy += [y[ii], y[ii]]

        x, y = xx, yy # blockify(x, y)

    plt.plot(x, y, **kwargs)


def plot_example(kind, peak_frequency, step, xlab=True, ylab=True, text=None, log=False):
    gaussian = get_spectra(peak_frequency, step, kind=kind)
    scale = np.max(gaussian['target'].variance_density.values)
    plot(gaussian['downsampled'], block=True, label='piecewise', freq_scale=peak_frequency, scale=scale, color='grey')
    plot(gaussian['downsampled'], block=False, label='linear', freq_scale=peak_frequency, scale=scale, color='grey',
         linestyle='--')
    plot(gaussian['target'], scale=scale, freq_scale=peak_frequency, color='k', label='target')
    plot(gaussian['non_monotone'], freq_scale=peak_frequency, scale=scale, label='natural', color='blue')
    plot(gaussian['interpolated'], freq_scale=peak_frequency, scale=scale, label='monotone', color='orange')

    if xlab:
        plt.xlabel(r'$f/f_{peak}$ [-]')
    else:
        plt.gca().axes.xaxis.set_ticklabels([])

    if ylab:
        plt.ylabel('$E/E_{peak}$ [-]')
    else:
        plt.gca().axes.yaxis.set_ticklabels([])

    if text:
        plt.text(0.1, 0.85, text, fontsize=8)

    if not log:
        plt.xlim([0.0, 2])
    else:
        plt.yscale('log')
        plt.xscale('log')
        plt.xlim([0.0, 4])
    plt.grid('on')


if __name__ == '__main__':
    # the coarse frequency step
    frequency_step = 0.01

    # frequency limits
    frequency_limits = [0.0, 0.5]

    # the high resolution frequency step used for integration
    frequency_step_highres = frequency_step / 100

    # frequency band
    frequency_band = frequency_limits[1] - frequency_limits[0]

    # Frequencies we sample the distribution at.
    sampled_frequencies = np.linspace(frequency_limits[0], frequency_limits[1],
                                      int(frequency_band / frequency_step) + 1,
                                      endpoint=True)

    # frequencies we interpolate at
    interpolated_frequencies = np.linspace(frequency_limits[0], frequency_limits[1],
                                           int(frequency_band / frequency_step_highres) + 1, endpoint=True)

    # Figure 1
    # ---------------

    figure = plt.figure(figsize=[7, 6], dpi=300)
    plt.subplot(2, 2, 1)
    plot_example('gaussian', 0.0525, 1 * frequency_step, xlab=False, text=r'(a) $1.00 \Delta f$')
    plt.legend(fontsize=8)

    plt.subplot(2, 2, 2)
    plot_example('gaussian', 0.0525, 0.5 * frequency_step, xlab=False, ylab=False, text=r'(b) $0.50 \Delta f$')

    plt.subplot(2, 2, 3)
    plot_example('gaussian', 0.0525, 0.25 * frequency_step, text=r'(c) $0.25 \Delta f$')

    plt.subplot(2, 2, 4)
    plot_example('gaussian', 0.0525, 0.1 * frequency_step, ylab=False, text=r'(d) $0.10 \Delta f$')

    plt.tight_layout()
    os.makedirs('./figures', exist_ok=True)
    figure.savefig('./figures/figure01.png')

    # Figure 2
    # ---------------

    log = False
    figure = plt.figure(figsize=[7, 6], dpi=300)
    plt.subplot(2, 2, 1)
    plot_example('jonswap', 0.0525, 1 * frequency_step, xlab=False, text=r'(a) JONSWAP' + '\n' + r'$f_{peak}=0.055$ Hz',
                 log=log)
    plt.legend(fontsize=8)

    plt.subplot(2, 2, 2)
    plot_example('jonswap', 0.1025, 0.5 * frequency_step, xlab=False, ylab=False,
                 text=r'(b) JONSWAP' + '\n' + r'$f_{peak}=0.105$ Hz', log=log)

    plt.subplot(2, 2, 3)
    plot_example('pm', 0.0525, 0.25 * frequency_step, text=r'(c) PM' + '\n' + r'$f_{peak}=0.055$ Hz', log=log)

    plt.subplot(2, 2, 4)
    plot_example('pm', 0.1025, 0.1 * frequency_step, ylab=False, text=r'(d) PM' + '\n' + r'$f_{peak}=0.105$ Hz',
                 log=log)

    plt.tight_layout()

    os.makedirs('./figures', exist_ok=True)
    figure.savefig('./figures/figure02.png')

    plt.show()
