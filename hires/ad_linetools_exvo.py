# Aleks Diamond-Stanic
# Feb 27, 2018
#
# https://github.com/linetools/linetools/blob/master/docs/examples/Voigt_examples.ipynb

#import sys
#sys.path.append('/Users/aleks/github/linetools/')

# suppress warnings for these examples
import warnings
warnings.filterwarnings('ignore')


### import
import astropy.units as u
from linetools.spectralline import AbsLine, SpectralLine
from linetools.spectra import io as lsio
from linetools.analysis import voigt as lav
from linetools import spectralline as ltsp
from linetools.spectra.xspectrum1d import XSpectrum1D
from linetools.isgm import abscomponent as lt_abscomp
from linetools.lists.linelist import LineList
import numpy as np
from pkg_resources import resource_filename
from scipy import integrate

# plots
from matplotlib import pyplot as plt
import pylab
pylab.rcParams['figure.figsize'] = (8.0, 6.0)
import matplotlib
matplotlib.rc('xtick', labelsize=20) 
matplotlib.rc('ytick', labelsize=20)

# Define a plotting function
def plt_line(spec):
    #plt.clf()
    #plt.figure(dpi=1200)
    plt.plot(spec.wavelength.value, spec.flux.value, 'k-', drawstyle='steps-mid', lw=1.5)
    plt.xlim(3644., 3650.)
    plt.ylabel('Normalized Flux', fontsize=20.)
    plt.xlabel('Wavelength', fontsize=20.)
    #ax = plt.gca()
    #ax.xaxis.set_major_locator(plt.MultipleLocator(2.))
    #ax.get_xaxis().get_major_formatter().set_useOffset(False)
    plt.ylim(0., 1.1)
    plt.show()
    plt.close()

ism = LineList('ISM')

abslin = AbsLine(1215.670*u.AA,z=2.0, linelist=ism)
#abslin = AbsLine(1215.670*u.AA, linelist=ism)

abslin.attrib['N'] = 10**14./u.cm**2  # log N
abslin.attrib['b'] = 25.*u.km/u.s
abslin.attrib['z'] = 2.0

xspec = XSpectrum1D.from_file(resource_filename('linetools','/spectra/tests/files/UM184_nF.fits'))
#xspec = lsio.readspec(resource_filename('linetools','/spectra/tests/files/UM184_nF.fits'))
#Load
abslin.analy['spec'] = xspec
#lsio.readspec(resource_filename('linetools','/spectra/tests/files/UM184_nF.fits'))#('../../linetools/spectra/tests/files/UM184_nF.fits')

#Generate
vmodel = abslin.generate_voigt()

# Plot
plt_line(vmodel)

abslin.attrib['N'] = 10**17.5/u.cm**2
abslin.attrib['b'] = 20.*u.km/u.s

wave = np.linspace(3644, 3650,100)*u.AA

vmodel2 = abslin.generate_voigt(wave=wave)

plt_line(vmodel2)

abslin2 = AbsLine('DI 1215')
abslin2.attrib['N'] = 10**13./u.cm**2  # log N
abslin2.attrib['b'] = 15.*u.km/u.s
abslin2.attrib['z'] = 2.0

vmodel3 = lav.voigt_from_abslines(wave,[abslin,abslin2])

plt_line(vmodel3)

tau = lav.voigt_from_abslines(wave,abslin,ret='tau')

plt.plot(wave,tau, 'k-', drawstyle='steps-mid', lw=1.5)
plt.xlim(3642., 3652.)
plt.ylim(0.,15000.)
plt.ylabel('Optical Depth', fontsize=20.)
plt.xlabel('Wavelength', fontsize=20.)
plt.show()
plt.close()

from astropy.modeling import fitting

fitvoigt = lav.single_voigt_model(logN=np.log10(abslin.attrib['N'].value),b=abslin.attrib['b'].value,
                                z=abslin.attrib['z'], wrest=abslin.wrest.value, 
                                gamma=abslin.data['gamma'].value, f=abslin.data['f'],
                                 fwhm=3.)

fitter = fitting.LevMarLSQFitter()

vmodel2.flux.value[0] = 1
vmodel2.flux.value[99] = 1

p = fitter(fitvoigt,wave[1:99].value,vmodel2.flux[1:99].value,weights=1./(np.ones(len(wave[1:99]))*0.1))
print(p)

plt.plot(wave, vmodel2.flux, 'k-',drawstyle='steps')
plt.plot(wave,p(wave.value), 'g-')
plt.xlim(3642., 3652.)
plt.ylim(0., 1.1)

plt.show()
plt.close()

import timeit

def voigt_slow(a, u):
    """ Calculate the voigt function to very high accuracy.
    Uses numerical integration, so is slow.  Answer is correct to 20
    significant figures.
    Note this needs `mpmath` or `sympy` to be installed.
    """
    try:
        import mpmath as mp
    except ImportError:
        from sympy import mpmath as mp
    with mp.workdps(20):
        z = mp.mpc(u, a)
        result = mp.exp(-z*z) * mp.erfc(-1j*z)

    return result.real


# This cell takes a few minutes to run.

a = 0.05
alluvoigt = np.linspace(0.,5.,1000)
true_voigt05 = []
for uvoigt in alluvoigt:
    true_voigt05.append(voigt_slow(a,uvoigt))
#%timeit -r 10 for uvoigt in alluvoigt: true_voigt05.append(voigt_slow(a,uvoigt))
## Just take first 1000
true_voigt05 = np.array(true_voigt05[0:1000])

plt.plot(alluvoigt, true_voigt05, '-')
plt.show()
plt.close()

# VoigtKing
# Speed
#%timeit -r 10 king_voigt05 = lav.voigtking(alluvoigt,a)

# Accuracy
king_voigt05 = lav.voigtking(alluvoigt,a)
plt.plot(alluvoigt, king_voigt05-true_voigt05, 'k-')
plt.show()
plt.close()


#SciPy
from scipy.special import wofz
def voigt_wofz(u,a):
    return wofz(u + 1j * a).real

# %timeit -r 10 wofz_voigt05 = voigt_wofz(alluvoigt,a)


wofz_voigt05 = voigt_wofz(alluvoigt,a)
#
plt.plot(alluvoigt, wofz_voigt05-true_voigt05, 'g-')
plt.show()
plt.close()

