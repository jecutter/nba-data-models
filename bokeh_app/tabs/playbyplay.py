from os.path import dirname, join

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from bokeh.io import curdoc
from bokeh.layouts import column, layout
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput, Panel, BoxAnnotation
from bokeh.models.widgets import Tabs, DataTable, DateFormatter, TableColumn
from bokeh.plotting import figure


global_boxes = []

def ControlUpdate(df, source, controls, plot):
	global global_boxes

	mask, starts, ends = PBPMask(df, controls)
	team = controls[0].value
	game = controls[2].value
	y_name = controls[4].value

	df_mask = df[mask]

	if len(starts) > 0:
		keep_starts = np.ones(len(starts), dtype=bool)
		keep_ends = np.ones(len(ends), dtype=bool)
		prev_end = -1
		for i in np.arange(len(starts)):
			#print(starts[i], ends[i])
			if starts[i] == ends[i]:
				#print('throwing out equal starts ends:', starts[i], ends[i])
				keep_starts[i] = False
				if ends[i] != 2880.:
					keep_ends[i] = False
			if i > 0:
				if starts[i] - prev_end <= 2.:
					#print('throwing out overlapping intervals, deleting:', ends[i-1], starts[i])
					keep_starts[i] = False
					keep_ends[i-1] = False
			#print('setting previous end to', ends[i])
			prev_end = ends[i]
		#print(keep_starts, keep_ends)
		#print(np.array(starts)[keep_starts])
		#print(np.array(ends)[keep_ends])
		starts = list(np.array(starts)[keep_starts])
		ends = list(np.array(ends)[keep_ends])

	boxes = []
	for start,end in zip(starts, ends):
		#print('made it', start, end)
		box = BoxAnnotation(left=start, right=end,
											line_width=1, line_color='black', line_dash='dashed',
											fill_alpha=0.2, fill_color='orange')
		print('box', box)
		plot.add_layout(box)
		boxes.append(box)

	#if len(boxes) != 0:
	#	plot.renderers.extend(boxes)
	#	global_boxes += boxes
	#else:
	#	if len(global_boxes) > 0:
	#		plot.renderers.remove(global_boxes)
	#	#for i, r in enumerate(plot.renderers):
	#	#	print(r)
	#	#	if i > 0:
	#	#		plot.renderers.remove(r)

	# Title
	if df_mask.home_team.values[0] == team:
		title = "Game " + game + " for " + team + ": At Home (vs. " + df_mask.vis_team.values[0] + ")"
	else:
		title = "Game " + game + " for " + team + ": Away Team (vs. " + df_mask.home_team.values[0] + ")"

	plot.title.text = title
	plot.title.text_font_size = '20pt'
	plot.title.text_font = 'serif'
	plot.title.align = 'center'

  # Axis titles
	plot.xaxis.axis_label = 'Time (seconds)' 
	plot.yaxis.axis_label = y_name 
	plot.xaxis.axis_label_text_font_size = '12pt'
	plot.xaxis.axis_label_text_font_style = 'bold'
	plot.yaxis.axis_label_text_font_size = '12pt'
	plot.yaxis.axis_label_text_font_style = 'bold'

  # Tick labels
	plot.xaxis.major_label_text_font_size = '12pt'
	plot.yaxis.major_label_text_font_size = '12pt'

	# Update source data
	source.data = dict(
		x = df_mask['time_sec'],
		y = df_mask[y_name],
		home_play = df_mask['ht_play'],
		away_play = df_mask['vt_play']
		#color = df_mask["color"],
		#alpha = df_mask["alpha"]
	)

def PBPMask(df, controls):
	# Group dataframe by team and establish for which games
	# the team is at home or away
	team = controls[0].value
	mask_team = ((df.home_team == team) | (df.vis_team == team))

	year = int(controls[1].value)
	mask_year = (df.year == year)

	game_idx = int(controls[2].value)-1
	team_games = np.unique(df[mask_team & mask_year].groupby(['game'], as_index=False).mean().game)
	mask_game = (df.game == team_games[game_idx])
	
	mask = np.logical_and(mask_team, mask_year)
	mask = np.logical_and(mask, mask_game)

	df_masked = df[mask]
	
	# Create player mask
	player = controls[3].value.lower()
	if player == '':
		player_starts = []
		player_ends = []
	else:
		dfhead = df_masked.groupby((df_masked[['ht_lineup','vt_lineup']] != df_masked[['ht_lineup','vt_lineup']].shift(1)).any(axis=1).cumsum()).head(1).reset_index(drop=True)
		dftail = df_masked.groupby((df_masked[['ht_lineup','vt_lineup']] != df_masked[['ht_lineup','vt_lineup']].shift(1)).any(axis=1).cumsum()).tail(1).reset_index(drop=True)
		player_start_mask = ((dfhead.ht_lineup.str.lower().str.contains(player) & (dfhead.home_team == team)) | (dfhead.vt_lineup.str.lower().str.contains(player) & (dfhead.vis_team == team)))
		player_end_mask = ((dftail.ht_lineup.str.lower().str.contains(player) & (dftail.home_team == team)) | (dftail.vt_lineup.str.lower().str.contains(player) & (dftail.vis_team == team)))
		player_starts = list(dfhead[player_start_mask].time_sec.values)
		player_ends = list(dftail[player_end_mask].time_sec.values)

	return mask, player_starts, player_ends


def playbyplay_tab(dft):
	# Grab list of stats/columns from dataframe
	stats = list(dft.columns.values)

	# Grab list of teams
	teams = np.unique(dft.home_team.values)
	teams = teams[teams != 'TOT']
	teams = list(teams)

	# Grab list of years/seasons
	years = list(np.unique(dft.year.values).astype(str))

	# Create a list of games (each team plays games 1-82)
	games = list(np.arange(1,83).astype(str))

	team_sel = Select(title="Team:", options=teams, value='ATL')
	year_sel = Select(title="Season:", options=years, value='2017')
	game_sel = Select(title="Game:", options=games, value='1')
	stint_sel = TextInput(title="Stints Containing Player:")
	y_axis = Select(title="Y Axis", options=stats, value="ht_margin")

	# Create a data source dictionary for storing data with each update
	#source = ColumnDataSource(data=dict(x=[], y=[], home_play=[], away_play=[], color=[], alpha=[]))
	source = ColumnDataSource(data=dict(x=[], y=[], home_play=[], away_play=[]))

	# Create tooltips object for hover variables,
	# and create figure for scatterplot
	TOOLTIPS=[
		("H.T. Play:", "@home_play"),
		("A.T. Play:", "@away_play")
	]

	p = figure(plot_height=550, plot_width=1000, title="", tooltips=TOOLTIPS, sizing_mode="scale_both")
	#p.line(x="x", y="y", source=source, line_width=2, color='color', line_alpha='alpha')
	p.line(x="x", y="y", source=source, line_width=2, color='black')

	# Create controls for filtering plotted data
	controls = [ team_sel, year_sel, game_sel, stint_sel, y_axis ]
	for control in controls:
			control.on_change('value', lambda attr, old, new: ControlUpdate(dft, source, controls, p))

	# Do a preliminary update of plot
	ControlUpdate(dft, source, controls, p)

	# Create layout by column
	inputs = column(*controls, width=250, height=600)
	inputs.sizing_mode = "fixed"
	l = layout([
			[inputs, p],
	#], sizing_mode="scale_both")
	])

	# Make a tab with the layout 
	tab = Panel(child=l, title = 'Game Play-By-Play')
		
	return tab

