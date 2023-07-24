"""
Contents: Script that reproduces figure 4 from the manuscript and saves it to the figures folder.

These files serve as the companion to the manuscript:

    "Continuous peak-period estimates from discrete surface-wave spectra", Smit et al., 2023

For details we on methods and results, please refer to the manuscript.

Copyright (C) 2023
Sofar Ocean Technologies

Authors: Pieter Bart Smit
"""

import observed_data
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os

# --- Plotting functions ---
def plot_bulk_parameter(data, start_date, end_date, ylim, xlabel, spectral_dates, **kwargs):
    """
    Plot bulk parameters waveheight or peak periods.
    :param data: data to plot
    :param start_date: start date
    :param end_date: end date
    :param ylim: y limits
    :param xlabel: x label
    :param spectral_dates: dates to plot vertical lines
    :param kwargs: kwargs for plot
    :return: None
    """
    time = data['reference'].time
    for date in spectral_dates:
        plt.plot([date, date], ylim, color='r', linestyle='--')

    plt.plot(time, data['reference'], 'grey', label='piecewise/linear', **kwargs)
    plt.plot(time, data['natural'], 'b', label='natural', **kwargs)
    plt.plot(time, data['monotone'], 'orange', label='monotone', **kwargs)
    plt.plot(time, data['target'], 'k', label='target', **kwargs)

    plt.xlim((start_date, end_date))
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
    plt.xlabel(xlabel)
    plt.ylim(ylim)
    plt.grid('on')


def plot_spec(spectral_dates: datetime, spectrum, lim=(0., 0.3)):
    """
    Plot spectra
    :param spectral_dates: date to plot spectrum for.
    :param spectrum: spectral data
    :param lim: frequency limits
    :return: None
    """
    def blockify(x, y):
        """
        Create bars to plot for discrete spectra
        :param x: time
        :param y: period
        :return: plotable bars
        """
        dx = x[2] - x[1]

        xx = []
        yy = []
        for ii in range(len(x)):
            xx += [x[ii] - 0.5 * dx, x[ii] + 0.5 * dx]
            yy += [y[ii], y[ii]]
        return np.array(xx), np.array(yy)

    spec_tar = spectrum['target'].sel(time=spectral_dates)
    spec_nat = spectrum['natural'].sel(time=spectral_dates)
    spec_mon = spectrum['monotone'].sel(time=spectral_dates)
    spec_ref = spectrum['reference'].sel(time=spectral_dates)

    x, y = blockify(spec_ref.frequency.values, spec_ref.values[:])
    plt.plot(x, y, 'grey', label='piecewise')
    plt.plot(spec_ref.frequency, spec_ref.values[:], 'grey', linestyle='--', label='linear')
    plt.plot(spec_nat.frequency, spec_nat.values[:], 'b', label='natural')
    plt.plot(spec_mon.frequency, spec_mon.values[:], 'orange', label='monotone')
    plt.plot(spec_tar.frequency, spec_tar.values[:], 'k', label='target')

    time_string = spectral_dates.strftime('%b-%d, %HH')
    plt.title(time_string, fontsize='10')
    plt.xlim(lim)
    plt.minorticks_on()
    plt.grid('on')
    plt.grid(which='major', linestyle='-', linewidth=1)
    plt.grid(which='minor', linestyle='-', linewidth=0.5)


# --- Main script ---
if __name__ == '__main__':

    # Get the data
    spectrum, peak_period, significant_wave_height = observed_data.get_data()

    # Set the time range
    start_date = datetime(2022, 9, 24)
    end_date = datetime(2022, 9, 29)

    # Set the dates to plot spectra for
    spectral_dates = [datetime(2022, 9, 17, 12), datetime(2022, 9, 23, 3), datetime(2022, 9, 24, 7),
                      datetime(2022, 9, 25, 12)]

    # Create the figure
    figure = plt.figure(figsize=[7, 10], dpi=300)

    # plot peak periods.
    plt.subplot(4, 1, 1)
    plot_bulk_parameter(peak_period,datetime(2022, 9, 13), datetime(2022, 9, 30), (4, 21), 'September, 2022', spectral_dates)
    plt.ylabel('Peak Period (s)')

    # plot significant wave heights periods.
    plt.subplot(4, 1, 2)
    plot_bulk_parameter(significant_wave_height,datetime(2022, 9, 13), datetime(2022, 9, 30), (0, 3), 'September, 2022', spectral_dates)
    plt.ylabel('Sign. Wave Height (m)')

    # Plot the different spectra
    plt.subplot(4, 2, 5)
    plot_spec(spectral_dates[0], spectrum)
    plt.ylabel('$E(f)$ [m$^2$/Hz]')
    plt.xlabel('$f$ [Hz]')

    plt.subplot(4, 2, 6)
    plot_spec(spectral_dates[1],spectrum)
    plt.xlabel('$f$ [Hz]')

    plt.subplot(4, 2, 7)
    plot_spec(spectral_dates[2],spectrum)
    plt.ylabel('$E(f)$ [m$^2$/Hz]')
    plt.xlabel('$f$ [Hz]')

    plt.subplot(4, 2, 8)
    plot_spec(spectral_dates[3],spectrum)
    plt.xlabel('$f$ [Hz]')

    # Add the legend
    plt.legend(fontsize=8)
    plt.tight_layout()

    # Save the figure, and show it.
    os.makedirs('./figures', exist_ok=True)
    figure.savefig('./figures/figure04.png')
    plt.show()
