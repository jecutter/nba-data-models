import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from bokeh.io import curdoc
from bokeh.layouts import column, layout
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput, Panel
from bokeh.models.widgets import Tabs
from bokeh.plotting import figure
#from bokeh import mpl

from tabs.players import player_tab
from tabs.lineups import lineup_tab
from tabs.playbyplay import playbyplay_tab


# Grab relative path to datasets
current_file = os.path.abspath(os.path.dirname(__file__))
player_csv_file = os.path.join(current_file, '../CompleteNBAPlayerStats.csv')
lineup_csv_file = os.path.join(current_file, '../NBALineupStats.csv')
pbp_csv_file = os.path.join(current_file, '../NBA_PBP_Data_PlusMinus.csv')

# Load NBA player data
df_player = pd.read_csv(player_csv_file)
df_lineup = pd.read_csv(lineup_csv_file)
df_pbp = pd.read_csv(pbp_csv_file)

# Create each of the tabs
tab1 = player_tab(df_player)
tab2 = lineup_tab(df_lineup)
tab3 = playbyplay_tab(df_pbp)

# Collect created tabs
tabs = Tabs(tabs = [tab1, tab2, tab3])

# Add tabs to the Bokeh document
#curdoc().add_root(l)
curdoc().add_root(tabs)
curdoc().title = "NBAStats"

