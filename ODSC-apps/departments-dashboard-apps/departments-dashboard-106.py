import pandas as pd

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox, column
from bokeh.models import (
    ColumnDataSource, Select, HoverTool, CategoricalColorMapper,
    Slider
)
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.plotting import figure
from bokeh.tile_providers import CARTODBPOSITRON_RETINA


# read the dataset
service_requests = pd.read_csv(
    '../../datasets/department-sr-ao.csv', index_col=0)

# create a blank ColumnDataSource object
source = ColumnDataSource(
    data={'x': [], 'y': [], 'dept': [], 'days_open': [], 'status': [],
          'case_title': [], 'source': [], 'id': [], 'photo': []})

# create the blank figure & use webgl to use GPU rendering in browser
p = figure(webgl=True)

# create a department drop down
dept = Select(title="Departments", value="INFO", options=[
              'INFO', 'ISD', 'PWDx', 'BTDT', 'PARK', 'PROP', 'ANML'])

max_days_open = service_requests['days_open'].max()

# round down to the nearest 100 to ensure there is always at least one point
max_number_100 = max_days_open - (max_days_open % 100)

# create a slider
days_slider = Slider(title='# of days open', value=0,
                     start=0, end=max_number_100, step=100)


# create the hover tool
hover = HoverTool(tooltips=[
    ('Days Open', '@days_open'),
    ('Status', '@status'),
    ('Case Title', '@title'),
    ('Source', '@source')],)

# add layers to the figure
p.add_tile(CARTODBPOSITRON_RETINA)
p.add_tools(hover)


# add a data table
columns = [
    TableColumn(field='id', title='Case ID'),
    TableColumn(field="days_open", title="Days Open"),
    TableColumn(field="title", title="Title "),
    TableColumn(field='queue', title='Work Queue')
]
data_table = DataTable(source=source, columns=columns, width=600, height=500)


status_list = ['ONTIME', 'OVERDUE']
color_mapper = CategoricalColorMapper(
    palette=['#377eb8', '#e41a1c'], factors=status_list)


# create circle glyphs with wm_y and wm_x coordinates as x and y
p.circle('x', 'y', source=source, alpha=0.8, color={
         'field': 'status', 'transform': color_mapper})

# filter the DataFrame based on the Department Title


def select_requests():
    dept_val = dept.value
    filtered_df = service_requests[
        (service_requests['days_open'] >= days_slider.value)
    ]
    filtered_df = filtered_df[
        filtered_df.Department.str.contains(dept_val) == True]
    return filtered_df

# update the ColumnDataSource values based on the new filtered df


def update():
    df = select_requests()
    source.data = {
        'x': df['wm_x'],
        'y': df['wm_y'],
        'dept': df['Department'],
        'days_open': df['days_open'],
        'status': df['OnTime_Status'],
        'title': df['CASE_TITLE'],
        'source': df['Source'],
        'id': df['CASE_ENQUIRY_ID'],
        'queue': df['QUEUE']}

dept.on_change('value', lambda attr, old, new: update())
days_slider.on_change('value', lambda attr, old, new: update())

update()  # initial load of the data

# create a layout with one row
layout = row(p, column(widgetbox(dept, days_slider, data_table)))

# add the layout to the current document
curdoc().add_root(layout)
