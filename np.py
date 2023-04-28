from roguewave import TimeSliceAnalysis, save, load, colocate_model_spotter_spectra, FrequencyDirectionSpectrum, \
    get_spectrum, FrequencySpectrum
import matplotlib.pyplot as plt
from typing import MutableMapping, List
import numpy as np
import matplotlib.dates as mdates
from datetime import datetime, timezone
import os


def get_model_spectra():
    start = datetime(2023, 1, 11, 0, tzinfo=timezone.utc)
    stop = datetime(2023, 1, 15, tzinfo=timezone.utc)
    time_slice = TimeSliceAnalysis(start, stop)

    # location of a valid model definition
    s3_uri_mod_def = 's3://sofar-ww3-model/CONSTANTS/grid/0p25/global/mod_def.ww3'
    # A valid sofar analysis model (needs to be in model_definition_
    model_name = "SofarECMWFHResOperationalWaveModelAnalysis025"

    # Get the colocated spectra for the background and analysis files. Spectra
    spotter_ids = get_spotter_names()
    analysis, spotter = colocate_model_spotter_spectra(
        'analysis_spectra', spotter_ids,
        time_slice,
        model_name=model_name,
        model_definition=s3_uri_mod_def,
        timebase='model',
        spectral_domain='native'
    )
    analysis: FrequencyDirectionSpectrum

    background, spotter = colocate_model_spotter_spectra(
        'background_spectra', spotter_ids,
        time_slice,
        model_name=model_name,
        model_definition=s3_uri_mod_def,
        timebase='model',
        spectral_domain='native'
    )
    analysis: FrequencyDirectionSpectrum

    return analysis, background, spotter


def get_spotter_names() -> List[str]:
    return ['SPOT-010009']  # , 'SPOT-010335', 'SPOT-010349', 'SPOT-010354', 'SPOT-010375', 'SPOT-010392',
    # 'SPOT-010408', 'SPOT-010425', 'SPOT-0870', 'SPOT-1035', 'SPOT-1100', 'SPOT-1118', 'SPOT-1188',
    # 'SPOT-1198', 'SPOT-1239', 'SPOT-1251', 'SPOT-1255', 'SPOT-1264']


def get_spectra(spotter_ids=None, start_date=datetime(2023, 1, 11, tzinfo=timezone.utc),
                end_date=datetime(2023, 1, 15, tzinfo=timezone.utc)) -> MutableMapping[str, FrequencySpectrum]:
    spotter_ids = get_spotter_names() if spotter_ids is None else spotter_ids
    spotters = get_spectrum(spotter_ids, start_date=start_date, end_date=end_date, cache=True)

    return spotters


file_an = './data/fig5_analysis.nc'
file_bck = './data/fig5_background.nc'
file_obs = './data/fig5_obs.nc'
if os.path.exists('./data/fig5_analysis.nc'):
    analysis = load(file_an)
    background = load(file_bck)
    spectra = load(file_obs)
else:
    analysis, background, spectra = get_model_spectra()
    save(analysis, file_an)
    save(background, file_bck)
    save(spectra, file_obs)
# analysis = analysis.as_frequency_spectrum().sel(spotter_id='SPOT-010009')
# spectra = spectra.as_frequency_spectrum().sel(spotter_id='SPOT-010009')
# spot = spectra
# # analysis = analysis[0,:,:]
# # spot = spectra[0,:,:]
#
# plt.figure(figsize=[7,6])
# plt.subplot(3,1,1)
# imax = spot.hm0().argmax().values + 10
#
# spec = spot[imax,:] # type: FrequencySpectrum
# freq = numpy.linspace(0.03,1,1001)
# spec_interp = spec.interpolate_frequency(freq,method='spline')
# an = analysis[imax,:]
# plt.plot( spec.frequency,spec.values,'k' )
# plt.plot(spec_interp.frequency, spec_interp.values, 'r')
# plt.plot(an.frequency, an.values, 'b-x')
# plt.xlim([0,0.2])
#
# plt.subplot(3, 1, 2)
# plt.plot(spot.time, spot.peak_period(), 'k')
# plt.plot(spot.time, spot.peak_period(use_spline=True), 'r')
# plt.plot(analysis.time, analysis.peak_period(), 'b')
# print(an.peak_period())
# plt.xticks(rotation=45)
# plt.subplot(3, 1, 3)
# plt.plot(spot.time, spot.hm0(), 'k')
# plt.xticks(rotation=45)
#
# plt.show()

freq = np.linspace(0.03, 1, 10001)
spec_reference = spectra.as_frequency_spectrum().sel(spotter_id='SPOT-010009')  # type: FrequencySpectrum
spec_monotone = spec_reference.interpolate_frequency(freq, method='spline')
spec_background = background.as_frequency_spectrum().sel(spotter_id='SPOT-010009')
spec_analysis = analysis.as_frequency_spectrum().sel(spotter_id='SPOT-010009')

tp_reference = spec_reference.peak_period(use_spline=True)
tp_analysis = spec_analysis.peak_period()
tp_monotone = spec_monotone.peak_period()
tp_background = spec_background.peak_period()


def plot(start, end, ylim, month, dates, to_plot='tp', **kwargs):
    time = tp_reference.time
    for date in dates:
        plt.plot([date, date], ylim, color='r', linestyle='--')

    if to_plot == 'tp':
        plt.plot(time, tp_reference, 'grey', label='piecewise/linear', **kwargs)
        #plt.plot(time, tp_background, 'b', label='background', **kwargs)
        plt.plot(time, tp_monotone, 'orange', label='monotone', **kwargs)
        plt.plot(time, tp_analysis, 'k', label='analysis', **kwargs)
    elif to_plot == 'dir':
        plt.plot(time, spec_reference.peak_direction(), 'grey', label='piecewise', **kwargs)
        #plt.plot(time, spec_background.peak_direction(), 'b', label='background', **kwargs)
        plt.plot(time, spec_monotone.peak_direction(), 'orange', label='monotone', **kwargs)
        plt.plot(time, spec_analysis.peak_direction(), 'k', label='analysis', **kwargs)
    elif to_plot == 'hm0':
        plt.plot(time, spec_reference.hm0(), 'grey', label='piecewise', **kwargs)
        plt.plot(time, spec_background.hm0(), 'b', label='background', **kwargs)
        plt.plot(time, spec_monotone.hm0(), 'orange', label='monotone', **kwargs)
        plt.plot(time, spec_analysis.hm0(), 'k', label='analysis', **kwargs)
    # plt.plot(time, tp_analysis_zp, 'r', label='target-zp', **kwargs)

    plt.xlim((start, end))
    # plt.xticks(rotation=45)
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
    plt.xlabel(month)
    plt.ylim(ylim)
    plt.grid('on')


def blockify(x, y):
    dx = x[2] - x[1]

    xx = []
    yy = []
    for ii in range(len(x)):
        xx += [x[ii] - 0.5 * dx, x[ii] + 0.5 * dx]
        yy += [y[ii], y[ii]]
    return np.array(xx), np.array(yy)


def plot_spec(time: datetime, lim=(0.025, 0.1)):
    spec_tar = spec_analysis.sel(time=time)
    spec_nat = spec_background.sel(time=time)
    spec_mon = spec_monotone.sel(time=time)
    spec_ref = spec_reference.sel(time=time)
    spec_ref2 = spec_reference.interpolate_frequency(spec_tar.frequency).sel(time=time)

    x, y = blockify(spec_ref.frequency.values, spec_ref.values[:])
    plt.plot(x,y, 'grey', linestyle='-', label='reference')
    x, y = blockify(spec_ref2.frequency.values, spec_ref2.values[:])
    plt.plot(x, y, 'b', label='piecewise')

    #plt.plot(spec_nat.frequency, spec_nat.values[:], 'b', label='background')

    x, y = blockify(spec_tar.frequency.values, spec_tar.values[:])
    plt.plot(x, y, 'k', label='analysis')
    #plt.plot(spec_mon.frequency, spec_mon.values[:], 'orange', label='monotone')

    downsampled = spec_monotone.down_sample( spec_tar.frequency.values )
    downsampled = downsampled.sel(time=time)
    x, y = blockify(downsampled.frequency.values, downsampled.values[:])
    plt.plot(x, y, 'orange', label='monotone')
    # plt.plot(spec_tar_zp.frequency, spec_tar_zp.values[:], 'r', label='target-zp')

    time_string = time.strftime('%b-%d, %HH')
    plt.title(time_string, fontsize='10')
    lim = [0, 0.15]
    plt.xlim(lim)
    plt.grid('on')


figure = plt.figure(figsize=[7, 10], dpi=300)

start = datetime(2023, 1, 11)
end = datetime(2023, 1, 15)

dates = [datetime(2023, 1, 12), datetime(2023, 1, 12,3), datetime(2023, 1, 12,6), datetime(2023, 1, 12,9)]

plt.subplot(4, 1, 1)
plot(start, end, (4, 21), 'January, 2023', dates)
plt.ylabel('Peak Period (s)')

plt.subplot(4, 1, 2)
plot(start, end, (0, 10), 'January, 2023', dates, to_plot='hm0')
plt.ylabel('Sign. Wave Height (m)')
# plt.legend(fontsize=8)


plt.subplot(4, 2, 5)
plot_spec(dates[0], lim=(0.025, 0.5))
plt.ylabel('$E(f)$ [m$^2$/Hz]')
plt.xlabel('$f$ [Hz]')

plt.subplot(4, 2, 6)
plot_spec(dates[1])
plt.xlabel('$f$ [Hz]')

plt.subplot(4, 2, 7)
plot_spec(dates[2])
plt.ylabel('$E(f)$ [m$^2$/Hz]')
plt.xlabel('$f$ [Hz]')

plt.subplot(4, 2, 8)
plot_spec(dates[3])
plt.xlabel('$f$ [Hz]')
plt.legend(fontsize=8)
plt.tight_layout()

figure.savefig('./figures/figure05.png')
plt.show()
