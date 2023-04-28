import sunflower13_data
import numpy
from roguewave import get_spectrum
from roguewave.spotterapi import search_rectangle
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress
from roguewave import to_datetime64, FrequencySpectrum

spotter = ['SPOT-010460','SPOT-1000','SPOT-0807']


start = datetime(2023,4,1)
end = datetime(2023,4,23)
spotter = get_spectrum(spotter,start,end)[spotter[0]] # type: FrequencySpectrum



#tp_monotone  = sunflower13_data.peak_period_monotone()

tp_monotone = spotter.peak_period(use_spline=True,monotone_interpolation=False)
dir = (270 - spotter.mean_direction().values) %360
# plt.figure(figsize=(7,6))
# plt.plot(tp_monotone.time,tp_monotone)
#
# plt.xticks(rotation=45)
# plt.show()
# exit(-1)
time = tp_monotone.time
fp_monotone = 1/tp_monotone

def regress(x,y):
    res = linregress( x, y )
    return res.slope, res.intercept

def distance( time_second,fpeak ):
    res = linregress( time_second, fpeak )
    dfdt = res.slope
    g = 9.81
    R = g / 4 / np.pi / dfdt / 1000
    return R

start = datetime(2023,4,10).timestamp()
end = datetime(2023,4,12).timestamp()



fp = fp_monotone.values
time = time.values.astype('float64')/1e9
msk = (time > start) & (time < end)
fp = fp[ msk ]
dir = dir[msk]
time = time[msk]
t = to_datetime64(time)

a,b = regress(time,fp)
plt.subplot(2,1,1)
plt.plot(t,fp)
plt.plot(t, a*time+b,'r--')

plt.subplot(2,1,2)
plt.plot(t,dir)
print(distance(time,fp))
plt.show()
