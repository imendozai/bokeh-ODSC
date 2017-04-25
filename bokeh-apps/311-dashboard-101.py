# "current document" where all the the plots and layouts are held
from bokeh.io import curdoc 

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
import pandas as pd

# read the dataset
service_requests = pd.read_csv('../datasets/service-requests.csv', index_col=0)

# convert the x and y coordinates from the DataFrame to a CDS
sr_cds = ColumnDataSource(data=dict(
	x = service_requests['wm_x'], 
	y = service_requests['wm_y'],
	))

# create the blank figure
p = figure()

# create circle glyphs with web mercator x and y coordinates
p.circle('x', 'y', source=sr_cds)

# add the plot to the current document
curdoc().add_root(p)
