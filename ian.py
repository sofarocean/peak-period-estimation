from roguewave import TimeSliceAnalysis, colocate_model_spotter, get_satellite_data, get_spotter_data, concatenate_spectra, load
from roguewave.colocate import colocate_points
from datetime import datetime, timezone, timedelta
from roguewave.spotterapi import get_spectrum
import numpy
from xarray import DataArray
import matplotlib.pyplot as plt
from typing import MutableMapping, List
from roguewave import FrequencySpectrum
from roguewave.tools.time import to_datetime64
import pandas
from roguewave.wavephysics.windestimate import estimate_u10_from_spectrum, estimate_u10_from_source_terms
from roguewave.wavephysics.balance import create_balance

def get_spotter_names() -> List[str]:
    return ['SPOT-30068D', 'SPOT-30097D', 'SPOT-30096D', 'SPOT-30104D', 'SPOT-30024D', 'SPOT-30065D']


def get_spectra(spotter_ids=None, start_date=datetime(2022, 9, 25, tzinfo=timezone.utc),
                end_date=datetime(2022, 10, 5, tzinfo=timezone.utc)) -> MutableMapping[str, FrequencySpectrum]:

    spotter_ids = get_spotter_names()  if spotter_ids is None else spotter_ids
    spotters = get_spectrum(spotter_ids, start_date=start_date, end_date=end_date, cache=True)

    return spotters


spectra = get_spectra()

for key,spot in spectra.items():
    plt.figure()
    imax = spot.hm0().argmax().values

    spec = spot[imax,:] # type: FrequencySpectrum
    freq = numpy.linspace(0.03,1,1001)
    spec_interp = spec.interpolate_frequency(freq,method='spline')

    plt.plot( spec.frequency,spec.values,'k' )
    plt.plot(spec_interp.frequency, spec_interp.values, 'r')
    plt.xlim([0,0.2])
    #plt.plot(spot.time, spot.peak_period(use_spline=True), 'r')
    #plt.xticks(rotation=45)
plt.show()
