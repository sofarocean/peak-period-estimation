import sunflower13_data
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timezone

spec_reference = sunflower13_data.get_spectrum('native')
spec_target = sunflower13_data.get_spectrum('zp')
spec_monotone = sunflower13_data.get_interpolated_spectrum()
spec_natural = sunflower13_data.get_natural_interpolated_spectrum()

tp_reference = spec_reference.peak_period()
tp_target = spec_target.peak_period()
tp_monotone  = sunflower13_data.peak_period_monotone()
tp_natural = sunflower13_data.peak_period_natural()


xstart = datetime(2022,9,24)
xend = datetime(2022,9,29)

def plot( start, end, ylim, month,dates, **kwargs ):
    time = tp_reference.time
    for date in dates:
        plt.plot(  [date,date],ylim,color='r',linestyle='--')

    plt.plot(time, tp_reference, 'grey', label='piecewise', **kwargs)
    plt.plot(time, tp_reference, 'grey', label='linear',linestyle='--', **kwargs)
    plt.plot(time, tp_natural, 'b', label='natural', **kwargs)
    plt.plot(time, tp_monotone, 'orange', label='monotone', **kwargs)
    plt.plot(time, tp_target, 'k', label='target', **kwargs)


    plt.xlim((start, end))
    #plt.xticks(rotation=45)
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
    plt.xlabel(month)
    plt.ylim(ylim)
    plt.grid('on')

def blockify(x,y):
    dx = x[2] - x[1]

    xx = []
    yy = []
    for ii in range( len(x) ):
        xx += [x[ii]-0.5*dx,x[ii]+0.5*dx]
        yy += [y[ii],y[ii]]
    return np.array(xx),np.array(yy)

def plot_spec(time, lim=(0.025,0.1)):
    spec_tar = spec_target.sel(time=time)
    spec_nat = spec_natural.sel(time=time)
    spec_mon = spec_monotone.sel(time=time)
    spec_ref = spec_reference.sel(time=time)


    x,y = blockify( spec_ref.frequency.values,spec_ref.values[:] )
    plt.plot( x,y,'grey',label='piecewise' )
    plt.plot(spec_ref.frequency, spec_ref.values[:], 'grey', linestyle='--')
    plt.plot(spec_nat.frequency, spec_nat.values[:], 'b', label='natural')
    plt.plot(spec_mon.frequency, spec_mon.values[:], 'orange', label='monotone')
    plt.plot(spec_tar.frequency, spec_tar.values[:], 'k', label='target')


    plt.xlim( lim)
    plt.grid('on')


figure = plt.figure(figsize=[7,10],dpi=300)

dates = [datetime(2022,9,24,7),datetime(2022,9,25,5),datetime(2022,9,26,5),datetime(2022,10,11,22)]

plt.subplot( 3,2,1)
plot(datetime(2022,9,24),datetime(2022,9,29),(12,21),'September, 2022',dates )
plt.ylabel('Peak Period (s)')
plt.legend(fontsize=8)

plt.subplot( 3,2,2)
plot(datetime(2022,10,10),datetime(2022,10,15),(14,18),'October, 2022',dates )

plt.subplot( 3,2,3)
plot_spec( dates[0], lim=(0.025,0.5))
plt.ylabel('$E(f)$ [m$^2$/Hz]')

plt.subplot( 3,2,4)
plot_spec( dates[1])

plt.subplot( 3,2,5)
plot_spec( dates[2])
plt.ylabel('$E(f)$ [m$^2$/Hz]')
plt.xlabel( '$f$ [Hz]')

plt.subplot( 3,2,6)
plot_spec( dates[3])
plt.xlabel( '$f$ [Hz]')
plt.tight_layout()

figure.savefig('./figures/figure04.png')
plt.show()