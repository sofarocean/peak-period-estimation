from roguewave import (
    FrequencySpectrum,
    load,
    save,
)


spec = load('spectrum_target.nc')

spec.save_as_netcdf('spectrum_target.nc')

