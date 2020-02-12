from os.path import dirname, join

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from bokeh.io import curdoc
from bokeh.layouts import column, layout
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput, Panel
from bokeh.models.widgets import Tabs, DataTable, DateFormatter, TableColumn
from bokeh.plotting import figure

def player_tab(df):
	# Grab list of stats/columns from dataframe
	#stats = sorted(df.columns.values)
	stats = list(df.columns.values)

	# Grab list of teams
	teams = np.unique(df.team.values)
	teams = np.insert(teams, 0, 'All')
	teams = np.insert(teams, 1, 'Multiple')
	teams = teams[teams != 'TOT']
	teams = list(teams)

	# Grab the minimum and maximum player ages
	age_low = min(df.age.values)
	age_high = max(df.age.values)

	#axis_map = {
	#	"2 PT %": "2PP_PH",
	#	"3 PT %": "3PP_PH",
	#}

	player_sel = TextInput(title="Player Names:")
	min_age = Slider(title="Min Age", start=age_low, end=age_high, value=age_low, step=1)
	max_age = Slider(title="Max Age", start=age_low, end=age_high, value=age_high, step=1)
	team_sel = Select(title="Team:", options=teams, value='All')
	min_year = Slider(title="Starting Season", start=2016, end=2020, value=2016, step=1)
	max_year = Slider(title="Ending Season", start=2016, end=2020, value=2019, step=1)
	#x_axis = Select(title="X Axis", options=sorted(axis_map.keys()), value="2 PT %")
	#y_axis = Select(title="Y Axis", options=sorted(axis_map.keys()), value="3 PT %")
	x_axis = Select(title="X Axis", options=stats, value="height")
	y_axis = Select(title="Y Axis", options=stats, value="weight")

	source = ColumnDataSource(data=dict(x=[], y=[], name=[], year=[], team=[], color=[], alpha=[]))

	def PlayerMask(dfc):
		player = player_sel.value
		team = team_sel.value
		
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
		mask_age = ((dfc.age >= min_age.value) & (dfc.age <= max_age.value))
		
		mask = np.logical_and(mask_player, mask_team)
		mask = np.logical_and(mask, mask_year)
		mask = np.logical_and(mask, mask_age)

		return mask

	def SelectPlayers():
		dfc = df.copy()
		mask = PlayerMask(dfc)
		dfc["color"] = np.where(mask, "red", "grey")
		dfc["alpha"] = np.where(mask, 0.9, 0.25)
		return dfc

	def UpdatePlot():
		dfp = SelectPlayers()

		#x_name = axis_map[x_axis.value]
		#y_name = axis_map[y_axis.value]
		x_name = x_axis.value
		y_name = y_axis.value

		# Title 
		#p.title.text = "%d players selected" % len(df)
		#p.title.text_font_size = '20pt'
		#p.title.text_font = 'serif'
		#p.title.align = 'center'

    # Axis titles
		p.xaxis.axis_label = x_axis.value
		p.yaxis.axis_label = y_axis.value
		p.xaxis.axis_label_text_font_size = '12pt'
		p.xaxis.axis_label_text_font_style = 'bold'
		p.yaxis.axis_label_text_font_size = '12pt'
		p.yaxis.axis_label_text_font_style = 'bold'

    # Tick labels
		p.xaxis.major_label_text_font_size = '12pt'
		p.yaxis.major_label_text_font_size = '12pt'

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

	p = figure(plot_height=600, plot_width=700, title="", tooltips=TOOLTIPS, sizing_mode="scale_both")
	p.circle(x="x", y="y", source=source, size=7, line_color=None, color='color', fill_alpha='alpha')

	controls = [ player_sel, min_age, max_age, team_sel, min_year, max_year, x_axis, y_axis ]
	for control in controls:
			control.on_change('value', lambda attr, old, new: UpdatePlot())

	inputs = column(*controls, width=250, height=600)
	inputs.sizing_mode = "fixed"

	columns = [
		TableColumn(field="name", title='Name'),
		TableColumn(field="year", title='Season'),
		TableColumn(field="x", title=x_axis.value),
		TableColumn(field="y", title=y_axis.value),
	]
	data_table = DataTable(source=source, columns=columns, width=275, height=600)

	def UpdateTable():
		x_name = x_axis.value
		y_name = y_axis.value
		
		data_table.columns = [
			TableColumn(field="name", title='Name'),
			TableColumn(field="year", title='Season'),
			TableColumn(field="x", title=x_axis.value),
			TableColumn(field="y", title=y_axis.value),
		]
	
		dfp = SelectPlayers()
		mask = PlayerMask(dfp)
		df_masked = dfp.where(mask)
		source.data = dict(
			x = df_masked[x_name],
			y = df_masked[y_name],
			name = df_masked['name'],
			year = df_masked['year'],
			team = df_masked['team'],
			color = df_masked['color'],
			alpha = df_masked['alpha'] 
		)
	
	for control in controls:
			control.on_change('value', lambda attr, old, new: UpdateTable())

	l = layout([
			#[desc],
			[inputs, p, data_table],
	#], sizing_mode="scale_both")
	])

	# Make a tab with the layout 
	tab = Panel(child=l, title = 'Player Stats')
	
	UpdatePlot()
	UpdateTable()

	return tab

