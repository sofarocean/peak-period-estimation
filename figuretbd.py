import sunflower13_data
import numpy
import matplotlib.pyplot as plt
from datetime import datetime, timezone
PATH = "/Users/pietersmit/Downloads/Sunflower13/log"

z_stages = [
    ("spike", None),
    ("integrate", None),
    ("cumulative", None),
    ("sos", None),
]

use_u=True

spectra = sunflower13_data.get_spectrum('native')
spectra2 = sunflower13_data.get_spectrum('smoothed')
spectra3 = sunflower13_data.get_spectrum('zp')

xstart = datetime(2022,9,24)
xend = datetime(2022,10,1)

# xstart = datetime(2022,10,10)
# xend = datetime(2022,10,15)

s = spectra3.sel(time=[xstart,xend])


intp  = sunflower13_data.get_interpolated_spectrum()
intp_spline  = sunflower13_data.get_natural_interpolated_spectrum()

plt.figure(figsize=[7,5],dpi=300)
n = 600

plt.plot( spectra3.frequency.values,spectra3.variance_density.values[n,:],'b'  )
plt.plot( spectra.frequency.values,spectra.variance_density.values[n,:],'k'  )
plt.plot( intp.frequency.values,intp.variance_density.values[n,:],'orange'  )


f = 0.035*1.1**numpy.arange(0,36)
plt.plot(f,f*0,'kx')
plt.xlim( (0.,0.2))


plt.figure(figsize=[7,6],dpi=300)
plt.plot( spectra3.time,spectra.peak_period(),'grey' )
plt.plot( spectra3.time,spectra3.peak_period(),'b' )
plt.plot( spectra3.time,intp.peak_period(),'orange' )

plt.xticks(rotation=45)

plt.xlim((xstart,xend))
plt.grid('on')

plt.figure(figsize=[7,6],dpi=300)
plt.plot( spectra3.time,spectra3.hm0(),'b' )
plt.plot( spectra3.time,intp.hm0(),'orange' )
plt.plot( spectra3.time,spectra.hm0(),'grey' )

plt.xticks(rotation=45)
plt.xlim((xstart,xend))
plt.grid('on')

plt.figure(figsize=[7,6],dpi=300)
plt.plot( [0,20],[0,20],'k--')
plt.plot( spectra3.peak_period(),spectra.peak_period(),'kx' )
plt.plot( spectra3.peak_period(),intp.peak_period(),'bx' )
plt.grid('on')

plt.figure(figsize=[7,6],dpi=300)
plt.plot( spectra3.time,spectra.peak_direction(),'grey' )
plt.plot( spectra3.time,spectra3.peak_direction(),'b' )
plt.plot( spectra3.time,intp.peak_direction(),'orange' )
plt.xticks(rotation=45)
plt.xlim((xstart,xend))
plt.grid('on')

plt.show()