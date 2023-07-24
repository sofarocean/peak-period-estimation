from roguewave.wavespectra.parametric import create_parametric_frequency_spectrum
import matplotlib.pyplot as plt
import numpy as np
from roguewave import save, load
import os

frequency_step = 0.01
frequency_limits = [0.01, 0.5]
frequency_step_highres = frequency_step / 100
frequency_band = frequency_limits[1] - frequency_limits[0]
sampled_frequencies = np.linspace(frequency_limits[0], frequency_limits[1], int(frequency_band / frequency_step) + 1,
                                  endpoint=True)
interpolated_frequencies = np.linspace(frequency_limits[0], frequency_limits[1],
                                       int(frequency_band / frequency_step_highres) + 1, endpoint=True)

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
            downsampled_spectrum = true_spectrum.down_sample(sampled_frequencies)

            truth[ind_sd, ind_per] = true_spectrum.peak_period().values
            downsampled[ind_sd, ind_per] = downsampled_spectrum.peak_period().values
            interpolated[ind_sd, ind_per] = downsampled_spectrum.peak_period(use_spline=True).values
            natural[ind_sd, ind_per] = downsampled_spectrum.peak_period(use_spline=True,monotone_interpolation=False).values

    return {'target': truth, 'downsampled_error': np.abs(downsampled - truth) / truth,
            'interpolated_error': np.abs(interpolated - truth) / truth,'downsampled':downsampled,'monotone':interpolated,'natural':natural }

# Lets calculate for a wave with peakperiod between 7.5*df and 8.5*df
jj = 8
peak_frequency = np.linspace( 5 * frequency_step, 15 * frequency_step, 101)
relative_frequency = peak_frequency #(peak_frequency - jj * frequency_step) / frequency_step

# Frequency widths
frequency_width = [2*frequency_step,frequency_step,frequency_step/2,frequency_step/10]

# Running is somewhat slow - so we save locally the results after the first time.
if os.path.exists('data/data.zip'):
    data = load('data/data.zip')
else:
    # Lets calculate
    data = {}
    data['gaussian'] = get_periods(peak_frequency, frequency_width, kind='gaussian')
    data['jonswap'] = get_periods(peak_frequency, [0.0], kind='jonswap')
    data['pm'] = get_periods(peak_frequency, [0.0], kind='pm')
    save(data, 'data/data.zip')



# PLOTTING CODE
def plot( kind, _range, diff,xlabel=None,ylabel=None,plot_legend=True ):
    if diff:
        target = data[kind]['target'][0, :]
    else:
        target = 0.0

    x = relative_frequency
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


#
figure = plt.figure( figsize=[7,5],dpi=300 )
plt.subplot( 2,3,1)
plot( 'gaussian', [1], False,plot_legend=False, ylabel= '$T_{{peak}}$ [s]')

plt.ylim([5,20])

plt.subplot( 2,3,2)
plot( 'jonswap', range(0,1 ), False )
plt.ylim([5,20])

plt.subplot( 2,3,3)
plot( 'pm', range(0,1 ), False,plot_legend=False )
plt.ylim([5,20])

plt.subplot( 2,3,4)
plot( 'gaussian', [1], True,plot_legend=False,ylabel='$\Delta T$ [s]', xlabel='$f_{{peak}}$ [Hz]' )
plt.ylim([-1.5,1.5])

plt.subplot( 2,3,5)
plot( 'jonswap', range(0,1 ), True,plot_legend=False,xlabel='$f_{{peak}}$ [Hz]' )
plt.ylim([-1.5,1.5])

plt.subplot( 2,3,6)
plot( 'pm', range(0,1 ), True,plot_legend=False,xlabel='$f_{{peak}}$ [Hz]' )
plt.ylim([-1.5,1.5])

plt.tight_layout()
os.makedirs('./figures',exist_ok=True)
figure.savefig('./figures/figure03.png')

plt.show()
