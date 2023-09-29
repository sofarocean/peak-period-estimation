"""
Contents: Routines to load data from observed data files. Also so convinience routines that save intermediate results
to disk so that plotting can be done faster once results are calculated.

These files serve as the companion to the manuscript:

    "Continuous peak-period estimates from discrete surface-wave spectra", Smit et al., 2023

For details we on methods and results, please refer to the manuscript.

Copyright (C) 2023
Sofar Ocean Technologies

Authors: Pieter Bart Smit
"""
from roguewavespectrum import FrequencySpectrum
from scipy.signal.windows import get_window
import xarray
import os
import numpy
from xarray import DataArray
import pickle

def get_data():
    kinds = ['reference','target','monotone','natural']
    spectra = {}
    tp = {}
    hm0 = {}
    for kind in kinds:
        spectra[kind] = get_spectrum(kind)
        tp[kind] = get_peak_period(kind)
        hm0[kind] = spectra[kind].significant_waveheight

    return spectra, tp, hm0

def get_spectrum(kind) -> FrequencySpectrum:
    """
    Get spectra from disk or calculate it if it does not exist yet. The returned spectrum takes the form
    of a roguewave.FrequencySpectrum object.

    :param kind: one of 'reference', 'target', 'monotone', 'natural'
    :return: spectrum
    """


    if kind == 'reference':
        kwargs = {'segment_length_seconds': 3600, 'use_u':True,'use_v':True}
        name = f'./data/spectrum_reference.nc'


        return FrequencySpectrum.from_netcdf(name) # type: FrequencySpectrum


    elif kind == 'target':
        kwargs = {'window':get_window('hann', 2048),'spectral_window':numpy.ones(9),
                  'segment_length_seconds':3600, 'use_u':True,'use_v':True}
        name = f'./data/spectrum_target.nc'

        return FrequencySpectrum.from_netcdf(name)
    elif kind == 'monotone':
        name = './data/spectrum_monotone.nc'

        if os.path.exists(name):
            with open(name, "rb") as file_handle:
                spec = pickle.load(file_handle)
            return spec

        else:
            native = get_spectrum('reference')
            hr = get_spectrum('target')
            spec = native.interpolate_frequency(hr.frequency, method='spline')
            with open(name, "wb") as file_handle:
                pickle.dump(spec, file_handle)
            return spec

    elif kind == 'natural':
        name = './data/spectrum_natural.nc'

        if os.path.exists(name):
            if os.path.exists(name):
                with open(name, "rb") as file_handle:
                    spec = pickle.load(file_handle)
                return spec

        else:
            native = get_spectrum('reference')
            hr = get_spectrum('target')
            spec = native.interpolate_frequency(hr.frequency, method='spline', monotone_interpolation=False)
            with open(name, "wb") as file_handle:
                pickle.dump(spec, file_handle)
            return spec

    else:
        raise Exception(f'unknown kind {kind}')

def get_peak_period(kind) -> DataArray:
    """
    Get peak period from disk or calculate it if it does not exist yet. The returned peak period takes the form
    of a xarray.DataArray object.

    :param kind: one of 'reference', 'target', 'monotone', 'natural'
    :return: peak periods
    """

    if kind == 'reference':
        return get_spectrum(kind).peak_period()

    elif kind == 'target':
        return get_spectrum(kind).peak_period()

    elif kind == 'monotone':
        name = './data/tp_monotone.nc'

        if os.path.exists(name):
            with open(name, "rb") as file_handle:
                tp = pickle.load(file_handle)
            return tp(name)  # type: DataArray
        else:
            spec = get_spectrum('reference')
            tp = spec.peak_period(use_spline=True)
            with open(name, "wb") as file_handle:
                pickle.dump(tp, file_handle)
            return tp

    elif kind == 'natural':
        name = './data/tp_natural.nc'

        if os.path.exists(name):
            with open(name, "rb") as file_handle:
                tp = pickle.load(file_handle)
            return tp(name)  # type: DataArray
        else:
            spec = get_spectrum('reference')
            tp = spec.peak_period(use_spline=True, monotone_interpolation=False)
            with open(name, "wb") as file_handle:
                pickle.dump(tp, file_handle)
            return tp
    else:
        raise Exception(f'unknown kind {kind}')


def get_displacements():
    """
    Get raw displacement data from netcdf file. Note that the displacement data is not include as part of the repository
    due to its size. Instead, derived spectra are included.

    :return: Pandas dataframe with displacement data.
    """
    dataset = xarray.open_dataset('./data/displacement.nc')
    return dataset.to_dataframe()