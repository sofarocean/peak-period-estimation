from roguewave import (
    FrequencySpectrum,
    load,
    save
)
from roguewave.spotter import spectra_from_raw_gps
from scipy.signal.windows import get_window
import xarray
import os
import numpy
from xarray import DataArray

def get_displacements(path=None ):
    dataset = xarray.open_dataset('./data/displacement.nc')
    return dataset.to_dataframe()

def get_spectrum(kind) -> FrequencySpectrum:
    if kind == 'native':
        kwargs = {'segment_length_seconds': 3600, 'use_u':True,'use_v':True}
        name = f'./data/spectrum_native.nc'
    elif kind == 'smoothed':
        kwargs = {'window':get_window('hann', 2048),'spectral_window':numpy.ones(9),
                  'segment_length_seconds':3600, 'use_u':True,'use_v':True}
        name = f'./data/spectrum_smoothed.nc'
    else:
        raise Exception(f'unknown kind {kind}')

    if os.path.exists(name):
        return load(name) # type: FrequencySpectrum
    else:
        displacement_doppler = get_displacements()
        spectrum = \
            spectra_from_raw_gps(
                None,
                displacement_doppler=displacement_doppler,
                **kwargs,
            )
        save(spectrum,name)
        return spectrum

def get_interpolated_spectrum() -> FrequencySpectrum:

    name = './data/spectrum_monotone.nc'

    if os.path.exists(name):
        return load(name) # type: FrequencySpectrum

    else:
        native = get_spectrum('native')
        hr = get_spectrum('smoothed')
        spec = native.interpolate_frequency(hr.frequency,method='spline')
        save(spec,name)
        return spec

def get_natural_interpolated_spectrum() -> FrequencySpectrum:

    name = './data/spectrum_natural.nc'

    if os.path.exists(name):
        return load(name) # type: FrequencySpectrum

    else:
        native = get_spectrum('native')
        hr = get_spectrum('smoothed')
        spec = native.interpolate_frequency(hr.frequency,method='spline',monotone_interpolation=False)
        save(spec,name)
        return spec

def peak_period_natural() -> DataArray:
    name = './data/tp_natural.nc'

    if os.path.exists(name):
        return load(name) # type: DataArray
    else:
        spec = get_spectrum('native')
        tp = spec.peak_period(use_spline=True,monotone_interpolation=False)
        save(tp,name)
        return tp

def peak_period_monotone() -> DataArray:
    name = './data/tp_monotone.nc'

    if os.path.exists(name):
        return load(name) # type: DataArray
    else:
        spec = get_spectrum('native')
        tp = spec.peak_period(use_spline=True)
        save(tp,name)
        return tp

if __name__ == '__main__':
    displacement = get_displacements()
    spectrum = get_spectrum('smoothed')
