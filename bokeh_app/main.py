from os.path import dirname, join

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from bokeh.io import curdoc
from bokeh.layouts import column, layout
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput
from bokeh.plotting import figure
#from bokeh import mpl

# Load NBA player data
df = pd.read_csv('~/Projects/Data_Science/nba-data-models/CompleteNBAPlayerStats.csv')

# Grab list of stats/columns from dataframe
#stats = sorted(df.columns.values)
stats = list(df.columns.values)
#print(stats)

# Grab list of teams
teams = np.unique(df.team.values)
teams = np.insert(teams, 0, 'All')
teams = np.insert(teams, 1, 'Multiple')
teams = teams[teams != 'TOT']
teams = list(teams)

# Grab list of NBA seasons
years = np.unique(df.year.values)

#axis_map = {
#	"2 PT %": "2PP_PH",
#	"3 PT %": "3PP_PH",
#}

# Create description block for the page header
desc = Div(text=open(join(dirname(__file__), "title.html")).read(), sizing_mode="stretch_width")

player_sel = TextInput(title="Player Names:")
team_sel = Select(title="Team:", options=teams, value='All')
min_year = Slider(title="Starting Season:", start=2016, end=2020, value=2016, step=1)
max_year = Slider(title="Ending Season:", start=2016, end=2020, value=2019, step=1)
#x_axis = Select(title="X Axis", options=sorted(axis_map.keys()), value="2 PT %")
#y_axis = Select(title="Y Axis", options=sorted(axis_map.keys()), value="3 PT %")
x_axis = Select(title="X Axis", options=stats, value="2PP_PH")
y_axis = Select(title="Y Axis", options=stats, value="3PP_PH")

source = ColumnDataSource(data=dict(x=[], y=[], name=[], year=[]))

def SelectPlayers():
	player = player_sel.value
	team = team_sel.value
	dfc = df.copy()
	
	#if player == '' and team == 'All':
	#	dfc["color"] = 'red'
	#	dfc["alpha"] = 0.9
	#elif team != 'All':
	#	if team == 'Multiple':
	#		dfc["color"] = np.where(dfc.team == 'TOT', "red", "grey")
	#		dfc["alpha"] = np.where(dfc.team == 'TOT', 0.9, 0.25)
	#	else:
	#		dfc["color"] = np.where(dfc.team == team, "red", "grey")
	#		dfc["alpha"] = np.where(dfc.team == team, 0.9, 0.25)
	#else:
	#	dfc["color"] = np.where(dfc.name.str.lower().str.contains(player), "red", "grey")
	#	dfc["alpha"] = np.where(dfc.name.str.lower().str.contains(player), 0.9, 0.25)
	#
	#dfc = dfc[(dfc.year >= min_year.value) & (dfc.year <= max_year.value)]  
	
	if player == '':
		mask_player = np.ones(len(dfc.index), dtype=bool)
	else:
		mask_player = dfc.name.str.lower().str.contains(player)
	
	if team == 'All':
		mask_team = np.ones(len(dfc.index), dtype=bool)
	else:
		if team == 'Multiple':
			mask_team = (dfc.team == 'TOT')
		else:
			mask_team = (dfc.team == team)

	mask_year = ((dfc.year >= min_year.value) & (dfc.year <= max_year.value))
	
	mask = np.logical_and(mask_player, mask_team)
	mask = np.logical_and(mask, mask_year)

	dfc["color"] = np.where(mask, "red", "grey")
	dfc["alpha"] = np.where(mask, 0.9, 0.25)

	return dfc

def UpdatePlot():
	dfp = SelectPlayers()

	#x_name = axis_map[x_axis.value]
	#y_name = axis_map[y_axis.value]
	x_name = x_axis.value
	y_name = y_axis.value

	p.xaxis.axis_label = x_axis.value
	p.yaxis.axis_label = y_axis.value
	p.title.text = "%d players selected" % len(df)
	source.data = dict(
		x = dfp[x_name],
		y = dfp[y_name],
		name = dfp['name'],
		year = dfp['year'],
		team = dfp['team'],
		color = dfp['color'],
		alpha = dfp['alpha'] 
	)


TOOLTIPS=[
	("Name", "@name"),
	("Year", "@year"),
	("Team", "@team")
]

p = figure(plot_height=700, plot_width=800, title="", toolbar_location=None, tooltips=TOOLTIPS, sizing_mode="scale_both")
p.circle(x="x", y="y", source=source, size=7, line_color=None, color='color', fill_alpha='alpha')

controls = [ player_sel, team_sel, min_year, max_year, x_axis, y_axis ]
for control in controls:
    control.on_change('value', lambda attr, old, new: UpdatePlot())

inputs = column(*controls, width=320, height=700)
inputs.sizing_mode = "fixed"

l = layout([
    [desc],
		[inputs, p],
#], sizing_mode="scale_both")
])

UpdatePlot()

curdoc().add_root(l)
curdoc().title = "Players"

