#/usr/bin/python
# plot slices
# created 08/30/2022: high-resolution density plots for movie and presentation

import yt
from yt.mods import *
import matplotlib.pyplot as plt
import numpy as np
import sys
# hide warnings for cleaner outputs
import warnings
warnings.filterwarnings("ignore")


fn  = sys.argv[1]
fn_short = fn[-3:]
plt_dir = './png/fancyslices/'
print (fn,fn_short)
ds = yt.load(fn)
cmin  = 2.e-29 # lower than ambient halo pre-shock density, increased for the 1e13 run
#cmin_ref =  # minimum refinment density
cmax  = 1.e-24


slcx = yt.SlicePlot(ds, 'x', 'density',fontsize=32)
slcx.set_width((120, "kpc"))
# vary the buff_size -- the number of resolution elements in the actual visualization
# set it to 4000x4000
buff_size = 3000
slcx.set_buff_size(buff_size)

# set the figure size in inches
figure_size = 12
slcx.set_figure_size(figure_size)

# density x-slice (entire box) without grids
slcx.annotate_timestamp(corner='upper_left', time_format='t = {time:.1f} {units}', time_unit='Myr')
slcx.annotate_scale(corner='upper_right')

slcx.annotate_title(r"13W 'Group' Halo Wind: Density Edge-on View")
slcx.set_cmap('density','inferno')
slcx.set_zlim("density",cmin,cmax)
#slcx.save(plt_dir+fn_short+'_xdens_fancy.png')
slcx.save(plt_dir+fn_short+'_xdens_fancy.png',
          mpl_kwargs=dict(dpi=250,bbox_inches='tight', pad_inches=0.1))

# close the dataset when done
ds.close()


