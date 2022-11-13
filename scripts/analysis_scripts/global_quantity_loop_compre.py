#!/usr/conda/python3
# created 08/09/2022 Jingyao Zhu
# a comprehensive script calculating the global quantities: mass, mass fluxes, ram pressure, star formation rate, radius and densities, for a given simulation checkpoint, and write to a data file
# adapted based on the scripts below
# 1. mass: gas_mass.py; will add new characterization of 'wind-facing/trailing' halves
# 2. mass flux: slice_flux.py; likely also add the flow within the disk in the wind direction (i.e., wind facing vs traling)
# 3. ram pressure: smallbox_ram_pressure.py
# 4. star formation rate: SFR_and_global_KS_law.py (tricky: bin size in time?)
# 5. radius and densities: KS_law_io.py; KS_law_io_young_star_experiment.py

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

# stars
def formed_star(pfilter, data):
    filter = data["all", "creation_time"] > 0
    return filter


add_particle_filter(
    "formed_star", function=formed_star, filtered_type="all", requires=["creation_time"]
)

# file input
fn  = sys.argv[1]
fn_short = fn[-3:]
plt_dir = './png/'
print (fn,fn_short)
ds = yt.load(fn)
ds.add_particle_filter("formed_star")
ad = ds.all_data()


# constants and scalars

current_time = ds.current_time
box_length_kpc = ds.domain_width[0].in_units('kpc').value
Msun = const.M_sun.cgs
kpc_to_cm = u.kpc.to(u.cm)

# variables
# spatial
R_disk = 18. # kpc, truncation radius of dark matter, reasonable upper bound
R_const_star_disk = 10. # kpc, our choice of a constant stellar disk radius
R_central_disk = 5. # kpc, reasonable lower bound for a central region selection

z_disk_thin = 2.  # kpc, thin 2 kpc disk (plus minus)
z_disk_thick= 5.  # kpc, thick 5 kpc disk (plus minus)
z_disk_cgm  = 10. # kpc, 10 kpc is way beyond the galaxy disk --> moving into the CGM

# metallicity
# different cuts capturing different degrees of mixing
metallicity_cut_low  = 0.2*Zsun  # 50% ICM and 50% ISM
metallicity_cut_mid  = 0.25*Zsun # 25% ICM and 75% ISM
metallicity_cut_high = 0.30*Zsun # almost entirely ISM


# arrays (no need to repeat definitions in each of the function/filter)

# gas
gas_Z      = ad['gas','metallicity']
gas_mass   = ad['gas','cell_mass']

gas_xcoord = ad['gas','x'].in_units('kpc').value - box_length_kpc/2.
gas_ycoord = ad['gas','y'].in_units('kpc').value - box_length_kpc/2.

# stars
star_mass = ad["formed_star", "particle_mass"].in_units("Msun")
formation_time = ad["formed_star", "creation_time"].in_units("yr")
star_xcoord = ad['formed_star', 'particle_position_x'].in_units("kpc").value - box_length_kpc/2.
star_ycoord = ad['formed_star', 'particle_position_y'].in_units("kpc").value - box_length_kpc/2.
star_zcoord = ad['formed_star', 'particle_position_z'].in_units("kpc").value - box_length_kpc/2.
star_radius = np.sqrt(star_xcoord**2 + star_ycoord**2)

################################### masses #######################################
# for different selections, always return the wind-facing (0<y<0.5) and trailing (0.5<y<1) side masses
# for gas and for formed stars
# can combine the two sides for total masses

def galaxy_mass(metal_cut=metallicity_cut_mid,
                disk_selection=True, disk_radius=R_disk, disk_height=z_disk_thin):


    # all galactic material by metal cut, no spatial restriction
    if disk_selection==False:

        # gas
        gas_mask = gas_Z >= metal_cut
        gas_windlead_mask  = (gas_ycoord<=0)
        gas_windtrail_mask = (gas_ycoord>0)

        gas_mass_windlead  = np.sum(gas_mass[gas_mask & gas_windlead_mask]).in_units("Msun").value
        gas_mass_windtrail = np.sum(gas_mass[gas_mask & gas_windtrail_mask]).in_units("Msun").value

        # stars
        star_windlead_mask  = star_ycoord<=0
        star_windtrail_mask = star_ycoord>0
        star_mass_windlead  = np.sum(star_mass[star_windlead_mask]).in_units("Msun").value
        star_mass_windtrail = np.sum(star_mass[star_windtrail_mask]).in_units("Msun").value

    # metal cut with spatial (disk) restriction
    else:

        # gas
        my_disk  = ds.disk(ds.domain_center, [0.0, 0.0, 1.0], disk_radius * kpc, disk_height * kpc)
        gas_mask = my_disk["gas", "metallicity"] >= metal_cut

        gas_windlead_mask  = (my_disk["gas", "y"].in_units('kpc').value - box_length_kpc/2.)<=0
        gas_windtrail_mask = (my_disk["gas", "y"].in_units('kpc').value - box_length_kpc/2.)>0

        gas_mass_windlead  = np.sum(my_disk["gas", "cell_mass"][gas_mask & gas_windlead_mask]).in_units("Msun").value
        gas_mass_windtrail = np.sum(my_disk["gas", "cell_mass"][gas_mask & gas_windtrail_mask]).in_units("Msun").value

        # stars
        star_windlead_mask  = (star_ycoord<=0) & (star_radius <= disk_radius)
        star_windtrail_mask = (star_ycoord>0)  & (star_radius <= disk_radius)
        star_mass_windlead  = np.sum(star_mass[star_windlead_mask]).in_units("Msun").value
        star_mass_windtrail = np.sum(star_mass[star_windtrail_mask]).in_units("Msun").value

    return np.array([gas_mass_windlead,gas_mass_windtrail,star_mass_windlead,star_mass_windtrail])





######################################## vertical mass fluxes ####################################
# flux calculator function
# define a vertical-flux calculator (potential density fields: density, metallicity, energy, etc)
# using dx*dy to obtain surface area
# output fluxes in the plus and minus z-directions

def vertical_flux_calculator(density_field,
                             disk_selection=False, disk_radius=R_central_disk, disk_height=z_disk_thin,
                             metal_select=True, metal_cut=metallicity_cut_mid):

    # default is no disk selection
    vertical_slice_plus  = ds.r[:, :, 0.5 + disk_height/box_length_kpc]
    vertical_slice_minus = ds.r[:, :, 0.5 - disk_height/box_length_kpc]

    if disk_selection == True:

        # the algorithm below selections a squared version instead of a circle, which is awkward

        vertical_slice_plus  = ds.r[0.5 - disk_radius/box_length_kpc:0.5 + disk_radius/box_length_kpc,
                                    0.5 - disk_radius/box_length_kpc:0.5 + disk_radius/box_length_kpc,
                                    0.5 + disk_height/box_length_kpc]

        vertical_slice_minus = ds.r[0.5 - disk_radius/box_length_kpc:0.5 + disk_radius/box_length_kpc,
                                    0.5 - disk_radius/box_length_kpc:0.5 + disk_radius/box_length_kpc,
                                    0.5 - disk_height/box_length_kpc]

        '''
        radius_mask_plus = (np.sqrt((vertical_slice_plus['gas','x'].in_units("kpc").value-box_length_kpc/2.)**2+\
                                   (vertical_slice_plus['gas','y'].in_units("kpc").value-box_length_kpc/2.)**2) \
                            < disk_radius)
        print (radius_mask_plus, vertical_slice_plus)

        vertical_slice_plus = vertical_slice_plus[radius_mask_plus]

        radius_mask_minus = (np.sqrt((vertical_slice_mius['gas','x'].in_units("kpc").value-box_length_kpc/2.)**2+\
                                   (vertical_slice_minus['gas','y'].in_units("kpc").value-box_length_kpc/2.)**2) \
                            < disk_radius)

        vertical_slice_minus = vertical_slice_minus[radius_mask_minus]
        '''
    # apply the metal-enriched cut for where we are focusing on the flows of galactic materials
    if metal_select == True:
        metal_mask_plus  = (vertical_slice_plus['metallicity']>=metal_cut)
        metal_mask_minus = (vertical_slice_minus['metallicity']>=metal_cut)

    # otherwise no metal mask: including all elements
    else:
        metal_mask_plus  = np.ones(len(vertical_slice_plus['metallicity'])).astype(bool)
        metal_mask_minus = np.ones(len(vertical_slice_minus['metallicity'])).astype(bool)

    # density array
    dens_arr_plus  = vertical_slice_plus[density_field][metal_mask_plus]
    dens_arr_minus = vertical_slice_minus[density_field][metal_mask_minus]

    # v_z array
    velz_arr_plus  = vertical_slice_plus['velocity_z'][metal_mask_plus]
    velz_arr_minus = vertical_slice_minus['velocity_z'][metal_mask_minus]


    # surface area array
    area_arr_plus  = vertical_slice_plus['dx'][metal_mask_plus] * vertical_slice_plus['dy'][metal_mask_plus]
    area_arr_minus = vertical_slice_minus['dx'][metal_mask_minus]*vertical_slice_minus['dy'][metal_mask_minus]

    # flux: scalar sum of the array
    z_flux_plus  = np.sum(dens_arr_plus * velz_arr_plus * area_arr_plus)
    z_flux_minus = np.sum(dens_arr_minus* velz_arr_minus* area_arr_minus)

    return np.array([z_flux_plus.in_units("Msun/yr").value,
                     z_flux_minus.in_units("Msun/yr").value])



##################################### ram pressures #########################################
# boxes are 1.62kpc^3

# for the 12W cases, we select a box at around  e.g.,(x,y,z)=(0,-25,-25) kpc to avoid bow shock impact
box_25 = ds.r[0.495:0.505, 0.34:0.35, 0.34:0.35]

# calculate ram pressure inside the box
rho_box_25 = box_25.mean(("gas", "density")).value

#velx_box_25 = box_25.mean(("gas", "velocity_x")).value # in cm/s
vely_box_25 = box_25.mean(("gas", "velocity_y")).value
velz_box_25 = box_25.mean(("gas", "velocity_z")).value

# only considering P_ram in the wind direction
P_ram_25 = rho_box_25 * (vely_box_25**2 + velz_box_25**2)


############################## star locations ####################################
# update 08/31/2022: write star radius and z location wrapper for three star populations: Young star 10 Myr, young star 100 Myr, all stars
# stellar radius calculation: four different recipes (1). 10 Myr young stars, (2). 30 Myr young stars (3). 100 Myr young stars (4). a constant, say a few times stellar scale radius, should be ~10 kpc

young_star_10_mask  = ds.current_time - formation_time.in_units('Myr') <= 10.
young_star_100_mask = ds.current_time - formation_time.in_units('Myr') <= 100.

# 10 Myr young star radius and height
young_star_10_r = star_radius[young_star_10_mask]
young_star_10_z = star_zcoord[young_star_10_mask]


# 100 Myr young star radius and height
young_star_100_r = star_radius[young_star_100_mask]
young_star_100_z = star_zcoord[young_star_100_mask]

# result array: R 95%, z 5%, 50%, and 95% (4 columns in total) 
# for three star populations (10, 100, and all)
def star_location_wrap(star_r, star_z):
    return np.array([np.percentile(star_r, 95),
                    np.percentile(star_z, 5),
                    np.percentile(star_z, 50),
                    np.percentile(star_z, 95)])


############################## outputs ###########################################
global_mass_arr= np.concatenate((galaxy_mass(metallicity_cut_mid, False,disk_radius=R_disk, disk_height=z_disk_thin),
                                 galaxy_mass(metallicity_cut_high, False,disk_radius=R_disk, disk_height=z_disk_thin),

                                # full gas radius, 2 kpc thin disk
                                galaxy_mass(metallicity_cut_mid, True,disk_radius=R_disk, disk_height=z_disk_thin),
                                galaxy_mass(metallicity_cut_high, True,disk_radius=R_disk, disk_height=z_disk_thin),

                                # constant stellar disk, makes sense to only consider a 2 kpc thin disk
                                galaxy_mass(metallicity_cut_mid, True,disk_radius=R_const_star_disk, disk_height=z_disk_thin),
                                galaxy_mass(metallicity_cut_high, True,disk_radius=R_const_star_disk, disk_height=z_disk_thin),

                                # central disk, thin (for mass fluxes)
                                galaxy_mass(metallicity_cut_mid, True,disk_radius=R_central_disk, disk_height=z_disk_thin),
                                galaxy_mass(metallicity_cut_high, True,disk_radius=R_central_disk, disk_height=z_disk_thin),

                                # full radius disk, thick (vertical mass distribution)
                                galaxy_mass(metallicity_cut_mid, True,disk_radius=R_disk, disk_height=z_disk_thick),
                                galaxy_mass(metallicity_cut_high, True,disk_radius=R_disk, disk_height=z_disk_thick),

                                # central radius mass, thick disk (for mass fluxes)
                                galaxy_mass(metallicity_cut_mid, True,disk_radius=R_central_disk, disk_height=z_disk_thick),
                                galaxy_mass(metallicity_cut_high, True,disk_radius=R_central_disk, disk_height=z_disk_thick)),

                                axis=0)


mass_flow_arr = np.concatenate((vertical_flux_calculator('density',False,R_disk,z_disk_thin, True,metallicity_cut_mid),
                               vertical_flux_calculator('density',False, R_disk,z_disk_thick,True,metallicity_cut_mid),
                               vertical_flux_calculator('density',False, R_disk,z_disk_cgm,  True,metallicity_cut_mid),

                               vertical_flux_calculator('density',False,R_disk,z_disk_thin,  True,metallicity_cut_high),
                               vertical_flux_calculator('density',False, R_disk,z_disk_thick,True,metallicity_cut_high),
                               vertical_flux_calculator('density',False, R_disk,z_disk_cgm,  True,metallicity_cut_high),

                               vertical_flux_calculator('density',True, R_central_disk,z_disk_thin, True,metallicity_cut_mid),
                               vertical_flux_calculator('density',True, R_central_disk,z_disk_thick,True,metallicity_cut_mid),

                               vertical_flux_calculator('density',True, R_central_disk,z_disk_thin, True,metallicity_cut_high),
                               vertical_flux_calculator('density',True, R_central_disk,z_disk_thick,True,metallicity_cut_high)),
                              axis=0)



ram_pressure_arr = np.array([rho_box_25, P_ram_25])


star_location_arr = np.concatenate((star_location_wrap(young_star_10_r, young_star_10_z),
                                  star_location_wrap(young_star_100_r, young_star_100_z),
                                  star_location_wrap(star_radius, star_zcoord)),
                                  axis=0)


results_arr = np.concatenate((global_mass_arr,
                             mass_flow_arr,
                             ram_pressure_arr,
			     star_location_arr),
                            axis=0)

# add the current time stamp at the header
results_arr = np.insert(results_arr, 0, current_time)
ds.close()

# add a memory protection step: release the big arrays no longer needed from memory
del (gas_Z,gas_mass,gas_xcoord,gas_ycoord,star_mass, formation_time, star_xcoord, star_ycoord, star_zcoord, star_radius)


# write to a text file
f_results=open('global_comprehensive.dat','a')
np.savetxt(f_results, results_arr,newline=" ")
f_results.write('\n')
f_results.close()
