import observed_data
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

spec = {}
spec['reference'] = observed_data.get_spectrum('native')
spec['target'] = observed_data.get_spectrum('smoothed')
spec['monotone'] = observed_data.get_interpolated_spectrum()
spec['natural'] = observed_data.get_natural_interpolated_spectrum()

tp = {}
tp['reference'] = spec['reference'].peak_period()
tp['target'] = spec['target'].peak_period()
tp['monotone']  = observed_data.peak_period_monotone()
tp['natural'] = observed_data.peak_period_natural()


xstart = datetime(2022,9,24)
xend = datetime(2022,9,29)

def plot( start, end, ylim, month,dates,to_plot='tp', **kwargs ):
    time = tp['reference'].time
    for date in dates:
        plt.plot(  [date,date],ylim,color='r',linestyle='--')

    if to_plot=='tp':
        plt.plot(time, tp['reference'], 'grey', label='piecewise/linear', **kwargs)
        plt.plot(time, tp['natural'], 'b', label='natural', **kwargs)
        plt.plot(time, tp['monotone'], 'orange', label='monotone', **kwargs)
        plt.plot(time, tp['target'], 'k', label='target', **kwargs)
    elif to_plot=='dir':
        plt.plot(time, spec['reference'].peak_direction(), 'grey', label='piecewise', **kwargs)
        plt.plot(time, spec['natural'].peak_direction(), 'b', label='natural', **kwargs)
        plt.plot(time, spec['monotone'].peak_direction(), 'orange', label='monotone', **kwargs)
        plt.plot(time, spec['target'].peak_direction(), 'k', label='target', **kwargs)
    elif to_plot=='hm0':
        plt.plot(time, spec['reference'].hm0(), 'grey', label='piecewise', **kwargs)
        plt.plot(time, spec['natural'].hm0(), 'b', label='natural', **kwargs)
        plt.plot(time, spec['monotone'].hm0(), 'orange', label='monotone', **kwargs)
        plt.plot(time, spec['target'].hm0(), 'k', label='target', **kwargs)


    plt.xlim((start, end))
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

def plot_spec(time:datetime, lim=(0.025,0.1)):
    spec_tar = spec['target'].sel(time=time)
    spec_nat = spec['natural'].sel(time=time)
    spec_mon = spec['monotone'].sel(time=time)
    spec_ref = spec['reference'].sel(time=time)


    x,y = blockify( spec_ref.frequency.values,spec_ref.values[:] )
    plt.plot( x,y,'grey',label='piecewise' )
    plt.plot(spec_ref.frequency, spec_ref.values[:], 'grey', linestyle='--',label='linear')
    plt.plot(spec_nat.frequency, spec_nat.values[:], 'b', label='natural')
    plt.plot(spec_mon.frequency, spec_mon.values[:], 'orange', label='monotone')
    plt.plot(spec_tar.frequency, spec_tar.values[:], 'k', label='target')

    time_string = time.strftime('%b-%d, %HH')
    plt.title( time_string,fontsize='10' )
    lim = [0,0.3]
    plt.xlim( lim)
    plt.minorticks_on()
    plt.grid('on')
    plt.grid(which='major', linestyle='-',linewidth=1)
    plt.grid(which='minor', linestyle='-',linewidth=0.5)

figure = plt.figure(figsize=[7,10],dpi=300)

dates = [datetime(2022,9,17,12),datetime(2022,9,23,3), datetime(2022,9,24,7),datetime(2022,9,25,12)]

plt.subplot( 4,1,1)
plot(datetime(2022,9,13),datetime(2022,9,30),(4,21),'September, 2022',dates )
plt.ylabel('Peak Period (s)')


plt.subplot( 4,1,2)
plot(datetime(2022,9,13),datetime(2022,9,30),(0,3),'September, 2022',dates,to_plot='hm0' )
plt.ylabel('Sign. Wave Height (m)')



plt.subplot( 4,2,5)
plot_spec( dates[0], lim=(0.025,0.5))
plt.ylabel('$E(f)$ [m$^2$/Hz]')
plt.xlabel( '$f$ [Hz]')

plt.subplot( 4,2,6)
plot_spec( dates[1])
plt.xlabel( '$f$ [Hz]')

plt.subplot( 4,2,7)
plot_spec( dates[2])
plt.ylabel('$E(f)$ [m$^2$/Hz]')
plt.xlabel( '$f$ [Hz]')

plt.subplot( 4,2,8)
plot_spec( dates[3])
plt.xlabel( '$f$ [Hz]')
plt.legend(fontsize=8)
plt.tight_layout()

figure.savefig('./figures/figure04.png')
plt.show()