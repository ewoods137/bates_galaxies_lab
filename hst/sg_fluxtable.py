# Sophia C W Gottlieb I
# 20170612 produce table of flux values in a txt file
# This code was originally the sg_compoverlay_loop.py, but I am going to take all of that code out right about now.
#
# import relevant Python modules
import os
import numpy as np
from astropy.io import fits
from photutils import CircularAperture
from photutils import aperture_photometry
import glob
import math
from scipy import integrate
from astropy.cosmology import WMAP9 as cosmo
from astropy import units as u
from astropy import constants as const

# define the directory that contains the images
dir = os.environ['HSTDIR']

#setting up arrays with three elements, all zeros - placeholders
wavelengths = [4,8,1]
data = [0 for x in range(len(wavelengths))]
header = [0 for x in range(len(wavelengths))]
fnu = [0 for x in range(len(wavelengths))]
exp = [0 for x in range(len(wavelengths))]

# specify the position of the science target and the size of the region around the science target to consider
filters = np.array([475, 814, 1600]) #*u.nm
galaxies = ['J0826', 'J0901', 'J0905', 'J0944', 'J1107', 'J1219', 'J1341', 'J1506', 'J1558', 'J1613', 'J2116', 'J2140']
xcen = [3628, 3933, 3386.5, 3477.5, 3573, 3802, 3886, 4149, 3787, 4174, 3565, 4067]
ycen = [4153, 4136, 3503.2, 3404.3, 3339, 4169, 4164, 3921, 4187, 3826, 3434, 4054]

fluxvalues = [[0 for x in range(len(wavelengths))] for y in range(len(galaxies))]

#xcen = [3628.7, 3934, 3386.5, 3477.539, 3572.9, 3801.2, 3885.6, 4149.15, 3787, 3825.89, 3566.9, 4067]
#ycen = [4153.8, 4137, 3503.2, 3404.342, 3339.1, 4171.6, 4164.336, 3921.748, 4187, 4451.805, 3435.9, 4054.4]

zs = [0.603, 0.459, 0.712, 0.514, 0.467, 0.451, 0.658, 0.608, 0.402, 0.449, 0.728, 0.752]
#Ldcm is the luminosity distance in cm, even though astropy thinks it is in Mpc. 
Ldcm = cosmo.luminosity_distance(zs)*u.Mpc.to(u.cm) / u.Mpc

# define the radii to be used for aperture photometry
radii = np.arange(40)+1
aMLR_BV_Vk_ab = [[0 for x in range(40)] for y in range(7)]
aLnuNu = [0 for x in range(len(wavelengths))]
#make an array for the calculation of the area of each bagel (annulus)
area = [0 for x in range(len(radii))]

# res specifies the percent of variation we expect from systematic error... 
# For now, we have chosen 0.05, or 5%.
res = 0.05

#calculate area of each bagel
for i in range(0, len(area)):
    if i == 0:
        area[i] = math.pi*math.pow(radii[0],2)
    else:
        area[i] = math.pi*(math.pow(radii[i],2)-math.pow(radii[i-1],2))
# Now, we loop through all galaxies

for w in range (0, len(galaxies)):
    # Mostly just for our own benefit, we print the galaxy's name so we know what 
    # works and what doesn't when the code breaks.
    print(galaxies[w])
    
    collection = ['F475W','F814W','F160W']
    
    flux = np.zeros([len(collection),len(radii)]) #*u.Jy
    subflux = np.zeros([len(collection),len(radii)])
    
    for i in range (0, len(collection)):
            
        # read in the images
        file = glob.glob(dir+galaxies[w]+'_final_'+collection[i]+'*sci.fits')
        hdu = fits.open(file[0])
        data[i], header[i] = hdu[0].data, hdu[0].header
        fnu[i] = header[i]['PHOTFNU']
        exp[i] = header[i]['EXPTIME']
    
        #define positions for photometry
        positions = [(xcen[w], ycen[w])]
    
        #do photometry on images
        #convert to proper units
        for j in range(0,len(radii)):
            aperture = CircularAperture(positions, radii[j])
            phot_table = aperture_photometry(data[i], aperture)
            flux[i,j] = phot_table['aperture_sum'][0]*(fnu[i]/exp[i])
            if j == 0:
                subflux[i,j] = flux[i,j]
            else:
                subflux[i,j] = flux[i,j]-flux[i,j-1]

        fluxvalues[w]=subflux
        
# Now that fluxvalues is full, we have to start making a new table.....
# the table has 8 columns: ID, f475, iv475, f814, iv814, f1600, iv1600, and z
# ID is GalaxyName_Aperature.

# we create or open our txt file
f = open("sg_fluxvalues.txt","w+")

# we write our column titles - unsure if these need to stay, just thought it would be nice.
f.write('ID\t\tf_475\t\t\tivar_475\t\tf_814\t\t\tivar_814\t\tf_1600\t\t\tivar_1600\t\tz\n')

# we shift through the data by galaxy and then by aperture.
for w in range(0,len(galaxies)):
    for i in range(0,len(radii)):
        # Building the ID name using if/else for those with single digits.
        ID = galaxies[w]+'_'
        if i < 10:
            ID = ID + '0' + str(i)
        else:
            ID = ID + str(i)
        # writing data divided by tabs (\t character)
        f.write(ID+'\t')
        # we loop through the filters because i am lazy and it is technically good form.
        # at the same time, we grab the inverse variance (squared) which is 1/(flux*res)^2.
        for j in range(0,len(collection)):
            f.write(str(fluxvalues[w][j][i])+'\t')
            ivar = (fluxvalues[w][j][i]*res)**(-2)
            f.write(str(ivar)+'\t')
        # to conclude the line, we include the z value for the galaxy before calling for a new line (\n).
        f.write(str(zs[w])+'\n')

f.close()