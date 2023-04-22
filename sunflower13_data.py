from roguewave.spotter import (
    displacement_from_gps_doppler_velocities,
    displacement_from_gps_positions,
    spectra_from_raw_gps,
)
from roguewave import FrequencySpectrum
from roguewave import load,save
from scipy.signal.windows import get_window
import xarray
import os
import numpy
from xarray import DataArray


def get_displacements(path=None ):
    if path is None:
        path = "/Users/pietersmit/Downloads/Sunflower13/log"

    z_stages = [
        ("spike", None),
        ("integrate", None),
        ("cumulative", None),
        ("sos", None),
    ]

    name = './data/displacement_doppler.nc'
    if os.path.exists(name):
        dataset = xarray.open_dataset(name)
        displacement_doppler = dataset.to_dataframe()
    else:
        displacement_doppler = displacement_from_gps_doppler_velocities(path, pipeline_stages=z_stages, )
        dataset = xarray.Dataset.from_dataframe(displacement_doppler)
        dataset.to_netcdf(name)

    name = './data/displacement_location.nc'
    if os.path.exists(name):
        dataset = xarray.open_dataset(name)
        displacement_location = dataset.to_dataframe()
    else:
        displacement_location = displacement_from_gps_positions(path)
        dataset = xarray.Dataset.from_dataframe(displacement_location)
        dataset.to_netcdf(name)

    return displacement_doppler, displacement_location

def get_spectrum(kind) -> FrequencySpectrum:



    if kind == 'native':
        kwargs = {}
        name = f'./data/spectrum_native.nc'
    elif kind == 'zp':
        kwargs = {'fft_length':2048*8}
        name = f'./data/spectrum_zeropadded.nc'
    elif kind == 'smoothed':
        kwargs = {'window':get_window('hann', 2048),'spectral_window':numpy.ones(11)}
        name = f'./data/spectrum_smoothed.nc'
    else:
        raise Exception(f'unknown kind {kind}')


    if os.path.exists(name):
        return load(name) # type: FrequencySpectrum
    else:
        displacement_doppler, displacement_location = get_displacements()
        spectrum = \
            spectra_from_raw_gps(
                None,
                displacement_doppler=displacement_doppler,
                displacement_location=displacement_location,
                **kwargs,
            )
        save(spectrum,name)
        return spectrum

def get_interpolated_spectrum() -> FrequencySpectrum:

    name = './data/interpolated.nc'

    if os.path.exists(name):
        return load(name) # type: FrequencySpectrum

    else:
        native = get_spectrum('native')
        zp = get_spectrum('zp')
        spec = native.interpolate_frequency(zp.frequency,method='spline')
        save(spec,name)
        return spec

def get_natural_interpolated_spectrum() -> FrequencySpectrum:

    name = './data/naturalinterpolated.nc'

    if os.path.exists(name):
        return load(name) # type: FrequencySpectrum

    else:
        native = get_spectrum('native')
        zp = get_spectrum('zp')
        spec = native.interpolate_frequency(zp.frequency,method='spline',monotone_interpolation=False)
        save(spec,name)
        return spec

def peak_period_natural() -> DataArray:
    name = './data/tp_naturalinterpolated.nc'

    if os.path.exists(name):
        return load(name) # type: DataArray
    else:
        spec = get_spectrum('native')
        tp = spec.peak_period(use_spline=True,monotone_interpolation=False)
        save(tp,name)
        return tp

def peak_period_monotone() -> DataArray:
    name = './data/tp_monotoneinterpolated.nc'

    if os.path.exists(name):
        return load(name) # type: DataArray
    else:
        spec = get_spectrum('native')
        tp = spec.peak_period(use_spline=True)
        save(tp,name)
        return tp

if __name__ == '__main__':
    displacement_doppler, displacement_location = get_displacements()
    spectrum = get_spectrum('smoothed')
