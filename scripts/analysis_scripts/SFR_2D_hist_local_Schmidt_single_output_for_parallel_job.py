#!/usr/anaconda/python3
# a python wrapper for the ipython notebook under the same name
# created 0825/2022 Jingyao Zhu

# created 0804/2022, adapted from local_SFR_and_gas_density.py
# adapted from 'SFR_2D_hist' notebook
# modified version for isolated run: Testing local SFR-gas phase differences among time frames in the isolated run

# selected time frames:
# 1. checkpoint=160: 1600 Myr, onset of 14W run
# 2. checkpoint=222: 2220 Myr, onset of RP stripping
# 3. checkpoint=259: 2590 Myr, enhancement of SFR in group wind run, decrease of SFR in cluster wind run

# update 08/25/2022, adapted from 'SFR_2D_hist_isolated_time_evolution' (see above)
# now systematically comparing among iso, 13W, 14W runs, and stacking multiple timesteps
# vim trick: set: paste and set: nopaste to avoid strange indentations

# update 09/25/2022: new version->SFR_2D_hist_local_Schmidt_single_output_for_parallel_job.py 
# output single data file for single data snapshot (then edit/combine in command line using cat)
# including six columns: time stamp, log(Sigma gas, Sigma sfr, Sigma formed star), x, y


import yt
from yt.mods import *
from yt.units import kpc
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
from yt.units import kpc
plt.rc('font',size=13)

# constants, units, etc
kpc_to_cm = u.kpc.to(u.cm)
Msun = const.M_sun.cgs.value
Myr_to_sec = u.yr.to(u.s)*1e6
sfr_unit_factor = u.g.to(u.Msun)*(u.kpc.to(u.cm))**2 /(10*1e6) 
# averaging over 10 Myrs, going from column density (g/cm^2) to SFR galactic unit (Msun/yr/kpc^2)

surf_dens_unit_factor = u.g.to(u.Msun)*(u.pc.to(u.cm))**2 
# converting from cgs column density (g/cm^2) to galactic gas/formed star density units (M_sun/pc^2)

# simulation specific constants
box_length = 5.e23/kpc_to_cm
fluff_dens = 8.7e-30 # g/cm^3
R_disk = 18. # kpc, truncation radius
#z_disk = 2.  # kpc, upper limit at all time frames
z_disk = 1.

# define just formed stars
def young_stars(pfilter, data):
    age = data.ds.current_time - data[pfilter.filtered_type, "creation_time"]
    # young star age limit (e.g., 10 Myr, 30 Myr, 100 Myr) can potentially be a variable
    filter = np.logical_and(age.in_units("Myr") <= 10, age >= 0)
    return filter

yt.add_particle_filter(
    "young_stars",
    function=young_stars,
    filtered_type="all",
    requires=["creation_time"])



# define all formed stars
def formed_star(pfilter, data):
    filter = data["all", "creation_time"] > 0
    return filter


add_particle_filter(
    "formed_star", function=formed_star, filtered_type="all", requires=["creation_time"]
)


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




# pipeline: make a function version of the frb i/o
# outputs: flattened sfr, gas density, coordinate (x and y) arrays
# optional outputs: sfr and gas map plots
# update 0825: for local Schmidt purposes, make the x and y coord outputs optional
# update 0925: added formed star surface densities (and its optional plot)

def frb_io(dataset, patch_length=1., plotter=True, output_coord=False):
    
    my_galaxy = dataset.disk(dataset.domain_center, [0.0, 0.0, 1.0], 
                             #radius= R_disk *np.sqrt(2)* kpc, height=z_disk * kpc)
                             # selecting a slightly larger region to deal with corner errors
                             radius= (R_disk+2) *np.sqrt(2)* kpc, height=z_disk * kpc)
        
    ############## define unit conversion constants if haven't already #####################
    # averaging over 10 Myrs, going from column density (g/cm^2) to SFR galactic unit (Msun/yr/kpc^2)
    sfr_unit_factor = u.g.to(u.Msun)*(u.kpc.to(u.cm))**2 /(10*1e6) 
    
    

    # converting from cgs column density (g/cm^2) to galactic gas density units (M_sun/pc^2)
    surf_dens_unit_factor = u.g.to(u.Msun)*(u.pc.to(u.cm))**2 

    kpc_to_cm = u.kpc.to(u.cm)
    box_length = 5.e23/kpc_to_cm
    
    ############ resolution settings ###############
    # defining width and res for frb
    width = (2*R_disk, "kpc") 
    
    # by default 1-kpc patch size 
    patch_count = int(2*R_disk/patch_length)
    res = [patch_count, patch_count]      
    
    ########### projections ###############
    # density projection
    dens_proj = dataset.proj(("gas", "density"), axis="z",
                             weight_field=None, data_source=my_galaxy)

    # generic projection (not cumulating anything, will be used for coordinate fields)
    proj = dataset.proj(("gas", "density"), axis="z",
                        weight_field = ("gas", "density"), data_source=my_galaxy)

    
    # local sfr projection
    lsfr_proj = dataset.proj(("deposit", "young_stars_cic"), axis="z",
                            weight_field=None, data_source=my_galaxy)
    
    # all formed star projection
    formed_star_proj = dataset.proj(("deposit", "formed_star_cic"), axis="z",
                            weight_field=None, data_source=my_galaxy)

    ################ frbs ######################
    # create frbs
    dens_frb = dens_proj.to_frb(width, res)
    generic_frb = proj.to_frb(width,res)
    lsfr_frb = lsfr_proj.to_frb(width, res)
    formed_star_frb = formed_star_proj.to_frb(width, res)


    ############### array outputs #################
    # flattened arrays
    # log10(gas dens, sfr, formed star dens)
    dens_arr = np.log10(dens_frb["gas", "density"].value * surf_dens_unit_factor).flatten()
    lsfr_arr = np.log10(lsfr_frb['deposit', 'young_stars_cic'] * sfr_unit_factor).flatten()
    formed_star_arr = np.log10(formed_star_frb['deposit', 'formed_star_cic'].value*surf_dens_unit_factor).flatten()

    xcoord_arr = (generic_frb['gas', 'x'].value/kpc_to_cm - box_length/2.).flatten()
    ycoord_arr = (generic_frb['gas', 'y'].value/kpc_to_cm - box_length/2.).flatten()
    
    ############### image outputs if applicable ################
    if plotter == True:
        # plot gas map
        fig, ax = plt.subplots(figsize=(7,6), dpi=300)
        plt.imshow(np.log10(dens_frb["gas", "density"].value * surf_dens_unit_factor),
                   cmap='coolwarm',extent=[-R_disk,R_disk,R_disk,-R_disk],clim=(-1,2.5))
        plt.xlabel('x [kpc]')
        plt.ylabel('y [kpc]')
        cbar = plt.colorbar()
        plt.hlines(y=0, xmin=-18, xmax=18, color='k',lw=1.5)
        cbar.set_label(r'$\log \Sigma_{gas}$ [$M_{\odot}/pc^{2}$]', rotation=270,labelpad=15)
        plt.tight_layout()
        plt.title(r'Gas Surface Density--'+str(patch_length)+' $kpc^{2}$ fixed resolution')
        plt.gca().invert_yaxis()
        plt.show()
        
        # plot sfr map
        fig, ax = plt.subplots(figsize=(7,6), dpi=300)
        plt.imshow(np.log10(lsfr_frb['deposit', 'young_stars_cic'] * sfr_unit_factor),
                   cmap='plasma',extent=[-R_disk,R_disk,R_disk,-R_disk])
        plt.xlabel('x [kpc]')
        plt.ylabel('y [kpc]')
        plt.gca().invert_yaxis()
        cbar = plt.colorbar()
        cbar.set_label(r'$\log \Sigma_{SFR}$ [$M_{\odot}/(yr \cdot kpc^{2})$]', rotation=270,labelpad=15)
        plt.hlines(y=0, xmin=-18, xmax=18, color='k',lw=1.5)
        plt.tight_layout()
        plt.title(r'Local SFR--'+str(patch_length)+' $kpc^{2}$ fixed resolution')
        plt.show()
        
        # plot formed star map
        fig, ax = plt.subplots(figsize=(7,6), dpi=300)
        plt.imshow(np.log10(formed_star_frb["deposit", "formed_star_cic"].value * surf_dens_unit_factor),
                   extent=[-R_disk,R_disk,R_disk,-R_disk])
                   #,clim=(-1,2.5))
        plt.xlabel('x [kpc]')
        plt.ylabel('y [kpc]')
        cbar = plt.colorbar()
        plt.hlines(y=0, xmin=-18, xmax=18, color='k',lw=1.5)
        cbar.set_label(r'$\log \Sigma_{\rm formed~star}$ [$M_{\odot}/pc^{2}$]', rotation=270,labelpad=15)
        plt.tight_layout()
        plt.title(r'Formed Star Surface Density--'+str(patch_length)+' $kpc^{2}$ fixed resolution')
        plt.gca().invert_yaxis()
        plt.show()        
    
    if output_coord == True:
        return dens_arr, lsfr_arr, formed_star_arr, xcoord_arr, ycoord_arr
    else:
        return dens_arr, lsfr_arr, formed_star_arr


# data i/o --> single data input
# file input
fn  = sys.argv[1]
fn_short = fn[-3:]
data_dir = './frbs/'
print (fn,fn_short)
ds = yt.load(fn)
ds.add_particle_filter("formed_star")
ds.add_particle_filter("young_stars")
ad = ds.all_data()


# calculate surface densities
dens_arr, lsfr_arr, star_arr, x_arr, y_arr = frb_io(ds, plotter=False, output_coord=True)

# generate time stamp column, same shape, repeating the data time
time_arr = np.array([ds.current_time] * len(dens_arr)) 


# write to a data file
np.savetxt(data_dir+'sfr_gas_star_local_patch_'+fn_short+'.dat', np.c_[time_arr, dens_arr, lsfr_arr, star_arr, x_arr, y_arr],header='time, gas_dens, local_sfr, star_dens, xmid_coord, ymid_coord')

