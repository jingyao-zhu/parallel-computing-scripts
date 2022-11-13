#!/usr/conda/python3
# created 08/24/2022 Jingyao Zhu
# simple phase plot for rusty loops

import yt
from yt.mods import *
from yt.units import kpc
from yt.units import Zsun
import matplotlib.pyplot as plt
import numpy as np
import sys
from astropy import constants as const
from astropy import units as u
from sys import getsizeof
# hide warnings for cleaner outputs
import warnings
warnings.filterwarnings("ignore")
from yt.data_objects.particle_filters import add_particle_filter
import matplotlib as mpl
plt.rc('font', size=13)
plt.rcParams["font.family"] = "serif"

plt_dir = './png/phaseplots/'

# gas
# define gas cylindrical radius and z-height in kpc

# cylindrical radius
@derived_field(name="cylindrical_r", sampling_type="cell", units="kpc",force_override=True)
def _cylindrical_r(field, data):
    # define the side length of the simulation domain in kpc
    box_side_length = (data.ds.domain_width[0].in_units('kpc'))/2.
    cylindrical_r   = np.sqrt((data['gas', 'x'].in_units("kpc") - box_side_length)**2 + \
                              (data['gas', 'y'].in_units("kpc") - box_side_length)**2)
    return (cylindrical_r)


# cylindrical z height
@derived_field(name="cylindrical_z", sampling_type="cell", units="kpc",force_override=True)
def _cylindrical_z(field, data):
    box_side_length = (data.ds.domain_width[0].in_units('kpc'))/2.
    cylindrical_z   = data['gas', 'z'].in_units("kpc") - box_side_length
    return (cylindrical_z)



# ICM/wind fraction -> need further testing on rusty
# for yt version 4.0+, the Zsun unit handling is different
'''
@derived_field(name="ICMf", sampling_type="cell", force_override=True)
def _ICMf(field, data):
    metal = data['gas', 'metallicity'].in_units('Zsun')
    icm_fraction = (0.3*Zsun - metal)/0.2
    
    # overwrite ISM and ICM values
    ism_mask = metal>=0.3*Zsun
    icm_fraction[ism_mask] = 0.
    
    icm_mask = metal<=0.1*Zsun
    icm_fraction[icm_mask] = 1.

    return (icm_fraction)
'''


# file input
fn  = sys.argv[1]
fn_short = fn[-3:]
print (fn,fn_short)
ds = yt.load(fn)
ad = ds.all_data()

# galaxy disk
galaxy_disk = ds.disk(ds.domain_center, [0.0, 0.0, 1.0], 18 * kpc, 2 * kpc)

sf_density = 10 * const.u.cgs.value # in g/cm3

profile2d = yt.create_profile(
    galaxy_disk,
    [("gas", "cylindrical_r"), ("gas", "density")],
    #n_bins=[64, 64],
    fields=[("gas", "metallicity"), ("gas", "cell_mass")],
    #weight_field=None,
    units = {("gas", "cylindrical_r"): "kpc", ("gas", "density"):  "g/cm**3"},
    logs={("gas", "cylindrical_r"): False, ("gas", "density"): True},
    extrema = {("gas", "cylindrical_r"): (0, 18),
               ("gas", "density"):  (8e-30, 5e-22)}
)

gas_metal_profile = profile2d["gas", "metallicity"]
gas_mass_profile  = profile2d["gas", "cell_mass"]



# plot metal profile
fig, ax = plt.subplots(figsize=(7,6), dpi=400)
plt.rc('font', size=13)
plt.rcParams["font.family"] = "serif"
opts = {'vmin':0.1, 'vmax':1.0, 'edgecolors':'none'}
plt.xlim(0, 18)
plt.ylim(8e-30, 5e-22)

plt.yscale('log')

# phase image
im = plt.pcolormesh(profile2d.x, profile2d.y,
                  gas_metal_profile.d.T, cmap='magma',
                   norm=mpl.colors.LogNorm(),
                  **opts)

# contour of ISM metallicity
plt.contour(profile2d.x, profile2d.y,
            gas_metal_profile.d.T,
            extent=[profile2d.x[0],profile2d.x[-1],profile2d.y[0], profile2d.y[-1]],
            linewidths=2, 
            cmap = 'Greys_r',
            norm=mpl.colors.LogNorm(),
            levels = [0.3],
            linestyles='solid',**opts)


# add a line annotating star forming density
plt.plot((0,18), (sf_density, sf_density), ls='-', color='black', lw=2)
plt.annotate(r'$\rho_{\rm min}$ for star formation',
           xy=(9, sf_density*1.2),color='black')

plt.ylabel(r'Density ($\rm g~cm^{-3}$)')
plt.xlabel(r'Cylindrical Radius R (kpc)')

fig.colorbar(im, label=r'Gas Metallicity ($Z_{\odot}$)')

plt.tight_layout()
plt.savefig(plt_dir+fn_short+'_density_R_metal_phase.png', bbox_inches='tight', pad_inches=0.1)


ds.close()

