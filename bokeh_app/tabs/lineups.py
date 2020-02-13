from os.path import dirname, join

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from bokeh.io import curdoc
from bokeh.layouts import column, layout
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput, Panel
from bokeh.models.widgets import Tabs, DataTable, DateFormatter, TableColumn
from bokeh.plotting import figure

def ControlUpdate(df, source, controls, plot, table):
	mask = LineupMask(df, controls)
	x_name = controls[4].value
	y_name = controls[5].value

	#df["color"] = np.where(mask, "red", "grey")
	#df["alpha"] = np.where(mask, 0.9, 0.25)
	df_mask = df[mask]

	# Title 
	#plot.title.text = "%d lineups selected" % len(df_mask)
	#plot.title.text_font_size = '20pt'
	#plot.title.text_font = 'serif'
	#plot.title.align = 'center'

  # Axis titles
	plot.xaxis.axis_label = x_name 
	plot.yaxis.axis_label = y_name 
	plot.xaxis.axis_label_text_font_size = '12pt'
	plot.xaxis.axis_label_text_font_style = 'bold'
	plot.yaxis.axis_label_text_font_size = '12pt'
	plot.yaxis.axis_label_text_font_style = 'bold'

  # Tick labels
	plot.xaxis.major_label_text_font_size = '12pt'
	plot.yaxis.major_label_text_font_size = '12pt'

	table.columns = [
		TableColumn(field="name", title='Lineup'),
		TableColumn(field="year", title='Season'),
		TableColumn(field="x", title=x_name),
		TableColumn(field="y", title=y_name),
	]
	
	source.data = dict(
		x = df_mask[x_name],
		y = df_mask[y_name],
		name = df_mask['lineup_name'],
		year = df_mask['year'],
		team = df_mask['team']
	)

def LineupMask(df, controls):
	player = controls[0].value.lower()
	team = controls[1].value
	
	if player == '':
		mask_player = np.ones(len(df.index), dtype=bool)
	else:
		mask_player = df.lineup_name.str.lower().str.contains(player)
	
	if team == 'All':
		mask_team = np.ones(len(df.index), dtype=bool)
	else:
		if team == 'Multiple':
			mask_team = (df.team == 'TOT')
		else:
			mask_team = (df.team == team)

	mask_year = ((df.year >= controls[2].value) & (df.year <= controls[3].value))
	
	mask = np.logical_and(mask_player, mask_team)
	mask = np.logical_and(mask, mask_year)

	return mask


def lineup_tab(dfl):
	# Grab list of stats/columns from dataframe
	stats = list(dfl.columns.values)

	# Grab list of teams
	teams = np.unique(dfl.team.values)
	teams = np.insert(teams, 0, 'All')
	teams = np.insert(teams, 1, 'Multiple')
	teams = teams[teams != 'TOT']
	teams = list(teams)

	player_sel = TextInput(title="Lineup Contains Player:")
	team_sel = Select(title="Team:", options=teams, value='All')
	min_year = Slider(title="Starting Season", start=2016, end=2020, value=2016, step=1)
	max_year = Slider(title="Ending Season", start=2016, end=2020, value=2019, step=1)
	x_axis = Select(title="X Axis", options=stats, value="GPT")
	y_axis = Select(title="Y Axis", options=stats, value="NETRTGT")

	# Create a data source dictionary for storing data with each update
	source = ColumnDataSource(data=dict(x=[], y=[], name=[], year=[], team=[]))

	# Create tooltips object for hover variables,
	# and create figure for scatterplot
	TOOLTIPS=[
		("Name", "@name"),
		("Year", "@year"),
		("Team", "@team")
	]

	p = figure(plot_height=600, plot_width=700, title="", tooltips=TOOLTIPS, sizing_mode="scale_both")
	p.circle(x="x", y="y", source=source, size=7, line_color=None, fill_alpha=0.8)

	columns = [
		TableColumn(field="name", title='Name'),
		TableColumn(field="year", title='Season'),
		TableColumn(field="x", title=x_axis.value),
		TableColumn(field="y", title=y_axis.value),
	]
	data_table = DataTable(source=source, columns=columns, width=275, height=550)

	# Create controls for filtering plotted/table data
	controls = [ player_sel, team_sel, min_year, max_year, x_axis, y_axis ]
	for control in controls:
			control.on_change('value', lambda attr, old, new: ControlUpdate(dfl, source, controls, p, data_table))

	# Do a preliminary update of plot and table
	ControlUpdate(dfl, source, controls, p, data_table)

	# Create layout by column
	inputs = column(*controls, width=250, height=600)
	inputs.sizing_mode = "fixed"
	l = layout([
			[inputs, p, data_table],
	#], sizing_mode="scale_both")
	])

	# Make a tab with the layout 
	tab = Panel(child=l, title = 'Lineup Stats')
		
	return tab

