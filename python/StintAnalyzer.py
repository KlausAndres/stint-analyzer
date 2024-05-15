# region ---- IMPORTS ----
import pandas as pd
# TODO delete after replacement of matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
# Track Data for naming of the turns
from TrackData import TRACKDATA
# General Constants
from Params import *
# Config Parameters for Plotly
from PlotlyConfig import *
# endregion

class StintAnalyzer:

    def __init__(self) -> None:

        # DataFrames for the datasets / use load_df1 and load_df2 to implement    
        self.df1 : pd.DataFrame
        self.df2 : pd.DataFrame

        self.df1_name : str
        self.df2_name : str
        self.df1_skip_laps : list = []
        self.df2_skip_laps : list = []

        # lap number of the fastest / slowest lap of a stint
        self.df1_fastest_lap : int
        self.df1_slowest_lap : int
        self.df2_fastest_lap : int
        self.df2_slowest_lap : int

        # dict for the storage of the static session data         
        self.sessiondata_df1 : dict = dict()
        self.sessiondata_df2 : dict = dict()


    def load_df1(self, buffer):
        self.df1=pd.read_csv(buffer)
        self.df1_name = 'Stint 1'


    def load_df2(self, buffer):
        self.df2=pd.read_csv(buffer)
        self.df2_name = 'Stint 2'


    def setup_stintanalyzer(self):

        # TODO delete after replacement of matplotlib
        self._set_matplotlib_params()
        
        # save the session data in the dicts [self.sessiondata_df1] and [self.sessiondata_df2]
        self._set_session_data()

        # create column [LapActualTime] in df1 and df2 with the laptime of the current lap
        self._set_actual_lap_time()

        # update the value for self.dfx_fastest_lap and self.dfx_slowest_lap
        self._update_fastest_and_slowest_lap()


    def _set_session_data(self):
        # saves the session data in the dicts self.sessiondata_df1 and self.sessiondata_df2
        sessiondata_keys_df1 = self.df1.SessionData[0].split('*')
        sessiondata_keys_df2 = self.df2.SessionData[0].split('*')
        sessiondata_values_df1 = self.df1.SessionData[1].split('*')
        sessiondata_values_df2 = self.df2.SessionData[1].split('*')

        for index in range(len(sessiondata_keys_df1)):
            self.sessiondata_df1[sessiondata_keys_df1[index]] = sessiondata_values_df1[index]

        for index in range(len(sessiondata_keys_df2)):
            self.sessiondata_df2[sessiondata_keys_df2[index]] = sessiondata_values_df2[index]


    def _set_actual_lap_time(self):
        # create column [LapActualTime] in df1 and df2 with the laptime of the current lap
        # different values for "LastLapTime" are displayed for each lap. The value with the most entries is the correct one.
        time_data_df1 = self.df1.groupby('Lap')['LapLastLapTime'].value_counts()
        time_data_df2 = self.df2.groupby('Lap')['LapLastLapTime'].value_counts()

        # saves the correct lap times, but still assigned to the wrong laps        
        time_dict_df1={}
        time_dict_df2={}

        # correct assignment of lap times to the laps        
        final_dict_df1={}
        final_dict_df2={}

        # creates a dictionary from the value_counts overview
        for index in range(time_data_df1.index.get_level_values(0).min(), time_data_df1.index.get_level_values(0).max()+1):
            time_dict_df1[index] = time_data_df1[index].to_dict()
        for index in range(time_data_df2.index.get_level_values(0).min(), time_data_df2.index.get_level_values(0).max()+1):
            time_dict_df2[index] = time_data_df2[index].to_dict()

        # selects the lap time with the most entries
        for key in time_dict_df1.keys():
            final_dict_df1[key - 1] = max(time_dict_df1[key], key=time_dict_df1[key].get)
        for key in time_dict_df2.keys():
            final_dict_df2[key - 1] = max(time_dict_df2[key], key=time_dict_df2[key].get)

        # delete in-/out-lap in the DataFrame, because there is no valid data        
        self.df1.drop(self.df1[self.df1.Lap == self.df1.Lap.min()].index, inplace = True)
        self.df1.drop(self.df1[self.df1.Lap == self.df1.Lap.max()].index, inplace = True)
        self.df2.drop(self.df2[self.df2.Lap == self.df2.Lap.min()].index, inplace = True)
        self.df2.drop(self.df2[self.df2.Lap == self.df2.Lap.max()].index, inplace = True)

        # assign the laptime to each row
        self.df1['LapActualTime'] = self.df1.Lap.apply(lambda lap: final_dict_df1[lap])
        self.df2['LapActualTime'] = self.df2.Lap.apply(lambda lap: final_dict_df2[lap])


    def _update_fastest_and_slowest_lap(self):
        # update the value for self.dfx_fastest_lap and self.dfx_slowest_lap
        self.df1_fastest_lap = self.df1.groupby('Lap').LapActualTime.max().idxmin() 
        self.df2_fastest_lap = self.df2.groupby('Lap').LapActualTime.max().idxmin()
        self.df1_slowest_lap = self.df1.groupby('Lap').LapActualTime.max().idxmax()
        self.df2_slowest_lap = self.df2.groupby('Lap').LapActualTime.max().idxmax()

    # TODO delete after replacement of matplotlib
    def _set_matplotlib_params(self):
        plt.rcParams['font.family'] = ['Roboto', 'Arial', 'sans-serif']


    def _convert_in_min(self, seconds : float) -> str:
        # converts the laptime in seconds (float) to a string(mm:ss:msmsms)
        value = int(seconds*1000%1000)
        if value == 0:
            ms = '000'
        elif value < 10:
            ms = '00' + str(value)
        elif value < 100:
            ms = '0' + str(value)
        else:
            ms = str(value)
        return time.strftime('%M:%S.{}'.format(ms), time.gmtime(seconds))


    def _get_figure_height(self, _window_width) -> int:
        # returns the height of a figure according to the width of the window
        if _window_width > FIGURE_HEIGHT.XL['width']:
            height = FIGURE_HEIGHT.XL['height']
        elif _window_width > FIGURE_HEIGHT.L['width']:
            height = FIGURE_HEIGHT.L['height']
        elif _window_width > FIGURE_HEIGHT.M['width']:
            height = FIGURE_HEIGHT.M['height']
        elif _window_width > FIGURE_HEIGHT.S['width']:
            height = FIGURE_HEIGHT.S['height']
        elif _window_width > FIGURE_HEIGHT.XS['width']:
            height = FIGURE_HEIGHT.XS['height']
        else:
            height = FIGURE_HEIGHT.XXS['height']
        return height


    def delete_laps_df1(self, laps : list) -> None:
        for lap in laps:
            self.df1.drop(self.df1[self.df1.Lap == int(lap)].index, inplace=True)
        self._update_fastest_and_slowest_lap()    


    def delete_laps_df2(self, laps: list) -> None:
        for lap in laps:
            self.df2.drop(self.df2[self.df2.Lap == int(lap)].index, inplace=True)
        self._update_fastest_and_slowest_lap()


    def get_laps_overview(self, dataframe : str) -> pd.DataFrame:
        if dataframe == 'df1':
            data = self.df1.groupby('Lap').LapActualTime.max().to_frame()
        elif dataframe == 'df2':
            data = self.df2.groupby('Lap').LapActualTime.max().to_frame()
        data.columns=['Laptime']
        return data.Laptime.apply(self._convert_in_min).to_frame()


    def get_sessiondata(self) -> tuple:
        return (self.sessiondata_df1, self.sessiondata_df2)        


    def get_laptime_graph(self):
        
        lap_data_df1 = self.df1.groupby('Lap')['LapActualTime']
        lap_data_df2 = self.df2.groupby('Lap')['LapActualTime']

        fig, axes = plt.subplots(1, 2, sharey=True, figsize=(8,5))
        fig.suptitle('Lap Times', fontsize=14, fontweight=600)

        axes[0].set_title(self.df1_name, fontsize=10, fontweight=300)
        axes[1].set_title(self.df2_name, fontsize=10, fontweight=300)


        lap_data_df1.mean().plot(ax=axes[0], color='red', linewidth=2, drawstyle="steps-mid", label='laptime')
        axes[0].plot(lap_data_df1.max().index, [lap_data_df1.max().mean()] * len(lap_data_df1.max().index), label='mean')
        axes[0].plot(lap_data_df1.max().index, [lap_data_df1.max().median()] * len(lap_data_df1.max().index), label='median')

        lap_data_df2.mean().plot(ax=axes[1], color='red', linewidth=2, drawstyle="steps-mid", label='')
        axes[1].plot(lap_data_df2.max().index, [lap_data_df2.max().mean()] * len(lap_data_df2.max().index))
        axes[1].plot(lap_data_df2.max().index, [lap_data_df2.max().median()] * len(lap_data_df2.max().index))

        axes[0].set_ylabel('Laptime in sec.', fontsize=9)

        for axe in axes:
            for value in 'top right'.split():
                axe.spines[value].set_visible(False)
            axes[1].spines['left'].set_visible(False)
            axe.grid(axis='y', linestyle='--', linewidth=0.5)
            axe.tick_params(labelsize=9, length=0)
            axe.set_xlabel('Lap', fontsize=9)

        formatter = mpl.ticker.FuncFormatter(lambda s, x: time.strftime('%M:%S:{}'.format(int(s*100%100)), time.gmtime(s)))
        axes[0].yaxis.set_major_formatter(formatter)

        axes[0].legend(frameon = False)
        plt.tight_layout()
        return fig

    # region ----- SPEED GRAPH -----
    def get_speed_per_lap(self, _window_width) -> go.Figure:
        # returns a figure that shows the max/mean/min speed per lap

        # get the figure height according to the window width
        height = self._get_figure_height(_window_width)

        # DataGroup per lap with Speed data
        df1_speed = self.df1.groupby(by='Lap').Speed
        df2_speed = self.df2.groupby(by='Lap').Speed

        # list of laps from df1 / df2
        x1_values = list(df1_speed.groups.keys())
        x2_values = list(df2_speed.groups.keys())

        # Create Figure
        fig = make_subplots(
            rows = 1, cols=2, 
            shared_yaxes=True,
            horizontal_spacing=HORIZONTAL_SPACING,
            subplot_titles=[self.df1_name, self.df2_name])

        # region ----- ADD DATA FOR MAX SPEED -----
        fig.add_trace(go.Scatter(
            x = x1_values, 
            y = df1_speed.max().round(1),
            line_shape = 'hvh',
            mode = 'lines', 
            name = self.df1_name, 
            line=dict(color=COLOR.BLUE, width=LINE_WIDTH.L), 
            visible = True,
            hovertemplate="Speed: %{y} km/h"),
            row = 1, col = 1)

        fig.add_trace(go.Scatter(
            x = x2_values,
            y = df2_speed.max().round(1), 
            line_shape = 'hvh',
            mode = 'lines',
            name = self.df2_name, 
            line=dict(color=COLOR.RED, width=LINE_WIDTH.L), 
            visible = True,
            hovertemplate="Speed: %{y} km/h"),
            row = 1, col = 2)

        fig.add_trace(go.Scatter(
             x = x1_values,
             y = [df1_speed.max().mean().round(1)]*len(x1_values),
             mode = 'lines',
             line=dict(color=COLOR.CYAN, width=LINE_WIDTH.S),
             visible = True,
             name = 'mean',
             hovertemplate='Mean: %{y} km/h'),
             row = 1, col = 1)

        fig.add_trace(go.Scatter(
             x = x1_values,
             y = [df1_speed.max().median().round(1)]*len(x1_values),
             mode = 'lines',
             line=dict(color=COLOR.GREEN, width=LINE_WIDTH.S),
             visible = True,
             name = 'median',
             hovertemplate='Median: %{y} km/h'),
             row = 1, col = 1)

        fig.add_trace(go.Scatter(
             x = x2_values,
             y = [df2_speed.max().mean().round(1)]*len(x2_values),
             mode = 'lines',
             line=dict(color=COLOR.CYAN, width=LINE_WIDTH.S),
             visible = True,
             hovertemplate='Mean: %{y} km/h',
             showlegend = False),
             row = 1, col = 2)

        fig.add_trace(go.Scatter(
             x = x2_values,
             y = [df2_speed.max().median().round(1)]*len(x2_values),
             mode = 'lines',
             line=dict(color=COLOR.GREEN, width=LINE_WIDTH.S),
             visible = True,
             hovertemplate='Median: %{y} km/h',
             showlegend = False),
             row = 1, col = 2)
        #endregion

        # region ----- ADD DATA FOR MEAN SPEED -----
        fig.add_trace(go.Scatter(
            x = x1_values, 
            y = df1_speed.mean().round(1),
            line_shape = 'hvh',
            mode = 'lines', 
            name = self.df1_name, 
            line=dict(color=COLOR.BLUE, width=LINE_WIDTH.L), 
            visible = False,
            hovertemplate="Speed: %{y} km/h"),
            row = 1, col = 1)

        fig.add_trace(go.Scatter(
            x = x2_values, 
            y = df2_speed.mean().round(1), 
            line_shape = 'hvh',
            mode = 'lines',
            name = self.df2_name, 
            line=dict(color=COLOR.RED, width=LINE_WIDTH.L), 
            visible = False,
            hovertemplate="Speed: %{y} km/h"),
            row = 1, col = 2)

        fig.add_trace(go.Scatter(
             x = x1_values,
             y = [df1_speed.mean().mean().round(1)]*len(x1_values),
             mode = 'lines',
             line=dict(color=COLOR.CYAN, width=LINE_WIDTH.S),
             visible = False,
             name = 'mean',
             hovertemplate='Mean: %{y} km/h'),
             row = 1, col = 1)

        fig.add_trace(go.Scatter(
             x = x1_values,
             y = [df1_speed.mean().median().round(1)]*len(x1_values),
             mode = 'lines',
             line=dict(color=COLOR.GREEN, width=LINE_WIDTH.S),
             visible = False,
             name = 'median',
             hovertemplate='Median: %{y} km/h'),
             row = 1, col = 1)

        fig.add_trace(go.Scatter(
             x = x2_values,
             y = [df2_speed.mean().mean().round(1)]*len(x2_values),
             mode = 'lines',
             line=dict(color=COLOR.CYAN, width=LINE_WIDTH.S),
             visible = False,
             hovertemplate='Mean: %{y} km/h',
             showlegend = False),
             row = 1, col = 2)

        fig.add_trace(go.Scatter(
             x = x2_values,
             y = [df2_speed.mean().median().round(1)]*len(x2_values),
             mode = 'lines',
             line=dict(color=COLOR.GREEN, width=LINE_WIDTH.S),
             visible = False,
             hovertemplate='Median: %{y} km/h',
             showlegend = False),
             row = 1, col = 2)
        #endregion

        # region ----- ADD DATA FOR MIN SPEED -----
        fig.add_trace(go.Scatter(
            x = x1_values, 
            y = df1_speed.min().round(1),
            line_shape = 'hvh',
            mode = 'lines', 
            name = self.df1_name, 
            line=dict(color=COLOR.BLUE, width=LINE_WIDTH.L), 
            visible = False,
            hovertemplate="Speed: %{y} km/h"),
            row = 1, col = 1)

        fig.add_trace(go.Scatter(
            x = x2_values, 
            y = df2_speed.min().round(1), 
            line_shape = 'hvh',
            mode = 'lines',
            name = self.df2_name, 
            line=dict(color=COLOR.RED, width=LINE_WIDTH.L), 
            visible = False,
            hovertemplate="Speed: %{y} km/h"),
            row = 1, col = 2)

        fig.add_trace(go.Scatter(
             x = x1_values,
             y = [df1_speed.min().mean().round(1)]*len(x1_values),
             mode = 'lines',
             line=dict(color=COLOR.CYAN, width=LINE_WIDTH.S),
             visible = False,
             name = 'mean',
             hovertemplate='Mean: %{y} km/h'),
             row = 1, col = 1)

        fig.add_trace(go.Scatter(
             x = x1_values,
             y = [df1_speed.min().median().round(1)]*len(x1_values),
             mode = 'lines',
             line=dict(color=COLOR.GREEN, width=LINE_WIDTH.S),
             visible = False,
             name = 'median',
             hovertemplate='Median: %{y} km/h'),
             row = 1, col = 1)

        fig.add_trace(go.Scatter(
             x = x2_values,
             y = [df2_speed.min().mean().round(1)]*len(x2_values),
             mode = 'lines',
             line=dict(color=COLOR.CYAN, width=LINE_WIDTH.S),
             visible = False,
             hovertemplate='Mean: %{y} km/h',
             showlegend = False),
             row = 1, col = 2)

        fig.add_trace(go.Scatter(
             x = x2_values,
             y = [df2_speed.min().median().round(1)]*len(x2_values),
             mode = 'lines',
             line=dict(color=COLOR.GREEN, width=LINE_WIDTH.S),
             visible = False,
             hovertemplate='Median: %{y} km/h',
             showlegend = False),
             row = 1, col = 2)
        #endregion

        # region ----- UPDATE LAYOUT -----
        fig.update_layout(LAYOUT_STANDARD)

        fig.update_layout(
            height=height * 0.7,
            title = dict(x=0.5, xanchor = 'center', text='Lap Overview: Maximum Speed'),
            legend_title_text='Stint',
            hovermode='x',         
            margin = dict(t=FIGURE_MARGIN.M))

        fig.update_xaxes(title_text='Lap', row=1, col=1)
        fig.update_xaxes(title_text='Lap', row=1, col=2)
        fig.update_xaxes(showline=True, linewidth=LINE_WIDTH.S, linecolor=COLOR.BLACK, row=1, col=1)
        fig.update_xaxes(showline=True, linewidth=LINE_WIDTH.S, linecolor=COLOR.BLACK, row=1, col=2)
        fig.update_yaxes(title_text='km/h', row=1, col=1)
        fig.update_yaxes(showline=True, linewidth=LINE_WIDTH.S, linecolor=COLOR.BLACK, row=1, col=1)
        # endregion

        # region ----- BUTTONS -----
        # 6* MAX_GRAPH, 6* MEAN_GRAPH, 6* MIN_GRAPH
        button1 = dict(method='update', 
               args=[{"visible": [True]*6 + [False]*6 + [False]*6},
                     {'title.text': 'Lap Overview: Maximum Speed'}], 
               label="Maximum Speed" )
        button2 = dict(method='update', 
               args=[{"visible": [False]*6 + [True]*6 + [False]*6},
                     {'title.text': 'Lap Overview: Average Speed'}], 
               label="Average Speed" )   
        button3 = dict(method='update', 
               args=[{"visible": [False]*6 + [False]*6 + [True]*6 },
                     {'title.text': 'Lap Overview: Minimum Speed'}], 
               label="Minimum Speed")

        fig.update_layout(
                 updatemenus =[dict(type='buttons',
                                    direction='left',
                                    buttons=[button1, button2, button3],
                                    x=0.00,
                                    xanchor="left",
                                    y=1.25,
                                    yanchor="top")])
        #endregion

        return fig


    def get_speed_comparision(self, _window_width):

        height = self._get_figure_height(_window_width)

        # region ----- GENERATE DATA -----
        # Data for mean laps
        mean_value_df1 = self.df1.groupby('LapDistPct').Speed.mean().round(1)
        mean_value_df2 = self.df2.groupby('LapDistPct').Speed.mean().round(1)
        
        # Data for fastest laps
        fastest_value_df1 = self.df1[self.df1.Lap == self.df1_fastest_lap].groupby('LapDistPct').Speed.mean().round(1)
        fastest_value_df2 = self.df2[self.df2.Lap == self.df2_fastest_lap].groupby('LapDistPct').Speed.mean().round(1)

        # Data for slowest lap
        slowest_value_df1 = self.df1[self.df1.Lap == self.df1_slowest_lap].groupby('LapDistPct').Speed.mean().round(1)
        slowest_value_df2 = self.df2[self.df2.Lap == self.df2_slowest_lap].groupby('LapDistPct').Speed.mean().round(1)
        # endregion

        # region ----- GENERATE CORNER NAMES -----
        # show corer names if both tracks are the same and trackdata is available
        if (self.sessiondata_df1['TrackName'] in TRACKDATA.keys() and 
            self.sessiondata_df1['TrackName'] == self.sessiondata_df2['TrackName']):
            is_trackdata_available : bool = True
           
            track_points = TRACKDATA[self.sessiondata_df1['TrackName']]
            annotations_data = dict(zip(mean_value_df1.index, mean_value_df1.values))

            annotations = []
            for key in track_points.keys():
                annotations.append({'x': key, 'y':annotations_data[key], 'text':track_points[key],
                           'align': 'center', 'font':{'family':"Roboto, sans-serif", 'size':ANNOTATION_FONT_SIZE},
                           'xanchor': 'center', 'showarrow': False, 'yshift': ANNOTATION_Y_SHIFT})
        else:
            annotations = []
            is_trackdata_available = False
        # endregion

        # region ----- CREATE FIGURE -----
        fig = make_subplots(
            rows = 2, cols=1,
            subplot_titles=['Total Speed + Speed Difference'],             
            row_heights=[0.8, 0.2],
            shared_xaxes=True,
            vertical_spacing=VERTICAL_SPACING)
        # endregion

        # region ----- ADD DATA FOR MEAN LAP -----
        fig.add_trace(go.Scatter(
            x = mean_value_df1.index, 
            y = mean_value_df1.values, 
            name = self.df1_name, 
            line=dict(color=COLOR.BLUE, width=LINE_WIDTH.M), 
            visible = True,
            hovertemplate="Speed: %{y} km/h"),
            row = 1, col = 1)

        fig.add_trace(go.Scatter(
            x = mean_value_df2.index, 
            y = mean_value_df2.values, 
            name = self.df2_name, 
            line=dict(color=COLOR.RED, width=LINE_WIDTH.M), 
            visible = True,
            hovertemplate="Speed: %{y} km/h"),
            row = 1, col = 1)

        fig.add_trace(go.Scatter(
            x = mean_value_df1.index,
            y = mean_value_df1.values - mean_value_df2.values,
            fill = 'tozeroy',
            name = 'Diff',
            line=dict(color=COLOR.BLUE, width=LINE_WIDTH.S),
            visible = True,
            hovertemplate="Diff: %{y} km/h"),
            row = 2, col = 1)
        # endregion

        # region ----- ADD DATA FOR FASTEST LAP -----
        fig.add_trace(go.Scatter(
            x = fastest_value_df1.index, 
            y = fastest_value_df1.values, 
            name = self.df1_name, 
            line=dict(color=COLOR.BLUE, width=LINE_WIDTH.M),
            visible = False),
            row = 1, col = 1)

        fig.add_trace(go.Scatter(
            x = fastest_value_df2.index, 
            y = fastest_value_df2.values, 
            name = self.df2_name, 
            line=dict(color=COLOR.RED, width=LINE_WIDTH.M),
            visible = False),
            row = 1, col = 1)

        fig.add_trace(go.Scatter(
            x = fastest_value_df1.index,
            y = fastest_value_df1.values - fastest_value_df2.values,
            fill = 'tozeroy',
            name = 'Diff',
            line=dict(color=COLOR.BLUE, width=LINE_WIDTH.S),
            visible = False),
            row = 2, 
            col = 1)
        # endregion

        # region ----- ADD DATA FOR SLOWEST LAP -----
        fig.add_trace(go.Scatter(
            x = slowest_value_df1.index, 
            y = slowest_value_df1.values, 
            name = self.df1_name, 
            line=dict(color=COLOR.BLUE, width=LINE_WIDTH.M),
            visible = False),
            row = 1, col = 1)

        fig.add_trace(go.Scatter(
            x = slowest_value_df2.index, 
            y = slowest_value_df2.values, 
            name = self.df2_name, 
            line=dict(color=COLOR.RED, width=LINE_WIDTH.M),
            visible = False),
            row = 1, col = 1)

        fig.add_trace(go.Scatter(
            x = slowest_value_df1.index,
            y = slowest_value_df1.values - slowest_value_df2.values,
            fill = 'tozeroy',
            name = 'Diff',
            line=dict(color=COLOR.BLUE, width=LINE_WIDTH.S),
            visible = False),
            row = 2, 
            col = 1)
        # endregion

        # region ----- UPDATE LAYOUT -----
        fig.update_xaxes(title_text='Lap Distance in Percentage', row=2, col=1)
        fig.update_yaxes(title_text='km/h', row=1, col=1)
        fig.update_yaxes(title_text='km/h', row=2, col=1)
        fig.update_xaxes(showline=True, linewidth=LINE_WIDTH.S, linecolor=COLOR.BLACK, row=2, col=1)
        fig.update_yaxes(showline=True, linewidth=LINE_WIDTH.S, linecolor=COLOR.BLACK, row=1, col=1)
        fig.update_yaxes(showline=True, linewidth=LINE_WIDTH.S, linecolor=COLOR.BLACK, row=2, col=1)

        fig.update_layout(LAYOUT_STANDARD)

        fig.update_layout(
            height=height,
            title = dict(x=0.5, xanchor = 'center', text='Speed Comparision: All Laps (mean)'),
            legend_title_text='Stint',
            hovermode='x',         
            margin = dict(t=FIGURE_MARGIN.M),
            annotations=annotations)
        
        fig.update_annotations(
            visible = False)
        # endregion

        # region ----- BUTTONS -----
        button1 = dict(method='update', 
               args=[{"visible": [True]*3 + [False]*6},
                     {'title.text': 'Speed Comparision: All Laps (mean)'}], 
               label="All Laps (mean)" )
        button2 = dict(method='update', 
               args=[{"visible": [False]*3 + [True]*3 + [False]*3 },
                     {'title.text': 'Speed Comparision - Fastest Laps (' + str(self.df1_name) + ': Lap ' + str(self.df1_fastest_lap) + ' / ' + str(self.df2_name) + ': Lap ' + str(self.df2_fastest_lap) + ')'}],
               label="Fastest Lap" )   
        button3 = dict(method='update', 
               args=[{"visible": [False]*6 + [True]*3 },
                     {'title.text': 'Speed Comparision - Slowest Laps (' + str(self.df1_name) + ': Lap ' + str(self.df1_slowest_lap) + ' / ' + str(self.df2_name) + ': Lap ' + str(self.df2_slowest_lap) + ')'}], 
               label="Slowest Lap" )
        button4 = dict(label="Corner names ON",
                       method='update',
                       args=[{'annotations.visible': True},
                             {'annotations': annotations}])
        button5 = dict(label="Corner names OFF",
                       method='update',
                       args=[{'annotations.visible': False},
                             {'annotations': []}])

        if is_trackdata_available:
            actual_buttons = [button1, button2, button3, button4, button5]
        else:
            actual_buttons = [button1, button2, button3]

        fig.update_layout(
                 updatemenus =[dict(type='buttons',
                                    direction='left',
                                    buttons=actual_buttons,
                                    x=0.00,
                                    xanchor="left",
                                    y=1.10,
                                    yanchor="top")])
        # endregion

        return fig


    def get_speed_track_map(self, _window_width):

        # gets the height of a figure according to the window width
        height = self._get_figure_height(_window_width)

        # TODO Delete if not necessary any more
        self.df1['LDP_round']=self.df1.LapDistPct.round(1)
        self.df2['LDP_round']=self.df2.LapDistPct.round(1)
        
        # region CREATE FIGURE
        fig = make_subplots(
            rows = 1, cols=2, 
            shared_yaxes=True,
            shared_xaxes=True,
            horizontal_spacing=HORIZONTAL_SPACING,
            subplot_titles=[self.df1_name, self.df2_name])
        # endregion

        # region ADD DATA FOR FASTEST LAP
        data_fastest_lap_df1 = self.df1[self.df1.Lap == self.df1_fastest_lap]
        # track map fastest lap
        fig.add_trace(go.Scatter(
            x=data_fastest_lap_df1.Lon,
            y=data_fastest_lap_df1.Lat,
            mode='markers',
            marker = dict(size=TRACK_MAP_SIZE, color=data_fastest_lap_df1.Speed, colorscale='YlOrRd', showscale=True),
            name = '',
            customdata=data_fastest_lap_df1.Speed.round(1),
            hovertemplate="Speed: %{customdata} km/h",
            visible = True,
            showlegend = False),
            row=1, col=1)
        # start finish line
        fig.add_trace(go.Scatter(
            x=[data_fastest_lap_df1.iloc[0].Lon],
            y=[data_fastest_lap_df1.iloc[0].Lat],
            mode = 'markers',
            marker = dict(size=TRACK_MAP_START_MARKER_SIZE, color=COLOR.BLACK),
            name = 'Start/Finish Line',
            showlegend = True,
            visible = True,
            hovertemplate="Start/Finish Line"), 
            row=1, col=1)
        
        fig.update_layout(legend=dict(
            yanchor="top",
            y=0.01,
            xanchor="left",
            x=0.99))
        
        data_fastest_lap_df2 = self.df2[self.df2.Lap == self.df2_fastest_lap]
        fig.add_trace(go.Scatter(
            x=data_fastest_lap_df2.Lon,
            y=data_fastest_lap_df2.Lat,
            mode='markers',
            marker = dict(size=TRACK_MAP_SIZE, color=data_fastest_lap_df2.Speed, colorscale='YlOrRd',showscale=False),
            visible = True,
            name='',
            customdata=data_fastest_lap_df2.Speed.round(1),
            hovertemplate="Speed: %{customdata} km/h",
            showlegend = False),
            row=1, col=2)

        fig.add_trace(go.Scatter(
            x=[data_fastest_lap_df2.iloc[0].Lon],
            y=[data_fastest_lap_df2.iloc[0].Lat],
            mode = 'markers',
            marker = dict(size=TRACK_MAP_START_MARKER_SIZE, color=COLOR.BLACK),
            name = 'Start/Finish Line',
            showlegend = False,
            visible = True,
            hovertemplate="Start/Finish Line"), 
            row=1, col=2)
        # endregion
      
        # region ADD DATA FOR SLOWEST LAP
        data_slowest_lap_df1 = self.df1[self.df1.Lap == self.df1_slowest_lap]
        fig.add_trace(go.Scatter(
            x=data_slowest_lap_df1.Lon,
            y=data_slowest_lap_df1.Lat,
            mode='markers',
            marker = dict(size=TRACK_MAP_SIZE, color=data_slowest_lap_df1.Speed, colorscale='YlOrRd', showscale=True),
            name = '',
            customdata=data_slowest_lap_df1.Speed.round(1),
            hovertemplate="Speed: %{customdata} km/h",
            visible = False,
            showlegend = False),
            row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=[data_slowest_lap_df1.iloc[0].Lon],
            y=[data_slowest_lap_df1.iloc[0].Lat],
            mode = 'markers',
            marker = dict(size=TRACK_MAP_START_MARKER_SIZE, color=COLOR.BLACK),
            name = 'Start/Finish Line',
            showlegend = True,
            visible = False,
            hovertemplate="Start/Finish Line"), 
            row=1, col=1)

        data_slowest_lap_df2 = self.df2[self.df2.Lap == self.df2_slowest_lap]
        fig.add_trace(go.Scatter(
            x=data_slowest_lap_df2.Lon,
            y=data_slowest_lap_df2.Lat,
            mode='markers',
            marker = dict(size=TRACK_MAP_SIZE, color=data_slowest_lap_df2.Speed, colorscale='YlOrRd',showscale=False),
            visible = False,
            name='',
            customdata=data_slowest_lap_df2.Speed.round(1),
            hovertemplate="Speed: %{customdata} km/h",
            showlegend = False),
            row=1, col=2)

        fig.add_trace(go.Scatter(
            x=[data_slowest_lap_df2.iloc[0].Lon],
            y=[data_slowest_lap_df2.iloc[0].Lat],
            mode = 'markers',
            marker = dict(size=TRACK_MAP_START_MARKER_SIZE, color=COLOR.BLACK),
            name = 'Start/Finish Line',
            showlegend = False,
            visible = True,
            hovertemplate="Start/Finish Line"), 
            row=1, col=2)
        # endregion

        # region UPDATE LAYOUT
        fig.update_layout(LAYOUT_STANDARD)
       
        fig.update_layout(
            height = height, 
            title = dict(x=0.5, xanchor = 'center', text='Speed Map - Fastest Laps (' + str(self.df1_name) + ': Lap ' + str(self.df1_fastest_lap) + ' / ' + str(self.df2_name) + ': Lap ' + str(self.df2_fastest_lap) + ')'),
            hovermode='closest',            
            margin = dict(t=FIGURE_MARGIN.M),
            xaxis=dict(scaleanchor='y', scaleratio=SCALE_RATIO_Y), 
            xaxis2=dict(scaleanchor='y2', scaleratio=SCALE_RATIO_Y2))

        fig.update_yaxes(
            visible = False,
            row=1, col=1)

        fig.update_yaxes(
            visible = False,
            row=1, col=2)

        fig.update_xaxes(
            visible = False)
        # endregion

        # region ANNOTATION UPDATE
        track_points = TRACKDATA['roadatlanta full']
        annotations = []
        for key in track_points.keys():
            x_value = self.df1[self.df1.LDP_round == key].iloc[0].Lon
            y_value = self.df1[self.df1.LDP_round == key].iloc[0].Lat

            annotations.append({'x':x_value, 'y':y_value, 'text':track_points[key],
                       'align': 'center', 'font':{'family':"Roboto Condensed, sans-serif", 'size':ANNOTATION_FONT_SIZE},
                       'xanchor': 'center', 'showarrow': False, 'yshift': 0, 'xshift': 0, 'xref': 'x1', 'yref': 'y1'})

            annotations.append({'x': x_value, 'y':y_value, 'text':track_points[key],
                       'align': 'center', 'font':{'family':"Roboto Condensed, sans-serif", 'size':ANNOTATION_FONT_SIZE},
                       'xanchor': 'center', 'showarrow': False, 'yshift': 0, 'xshift': 0, 'xref': 'x2', 'yref': 'y2'})
        # endregion

        # region BUTTON
        button1 = dict(method='update', 
               args=[{"visible": [True]*4 + [False]*4 },
                     {'title.text': 'Speed Map - Fastest Laps (' + str(self.df1_name) + ': Lap ' + str(self.df1_fastest_lap) + ' / ' + str(self.df2_name) + ': Lap ' + str(self.df2_fastest_lap) + ')'}], 
               label="Fastest Lap" )   
        button2 = dict(method='update', 
               args=[{"visible": [False]*4 + [True]*4 },
                     {'title.text': 'Speed Map - Slowest Laps (' + str(self.df1_name) + ': Lap '+ str(self.df1_slowest_lap) + ' / ' + str(self.df1_name) + ': Lap ' + str(self.df2_slowest_lap) + ')'}], 
               label="Slowest Lap" )
        
        button3 = dict(label="Corner names ON",
                       method='update',
                       args=[{'annotations.visible': True},
                             {'annotations': [fig.layout.annotations[0]]+ [fig.layout.annotations[1]] + annotations}])
        button4 = dict(label="Corner names OFF",
                       method='update',
                       args=[{'annotations.visible': True},
                             {'annotations': [fig.layout.annotations[0]]+ [fig.layout.annotations[1]]}])

        fig.update_layout(
                 updatemenus =[dict(type='buttons',
                                    direction='left',
                                    buttons=[button1, button2, button3, button4],
                                    x=0.00,
                                    xanchor="left",
                                    y=1.10,
                                    yanchor="top")])
        # endregion

        return fig


    def get_constancy_comparision(self, _window_width):

        # region WIDTH
        if _window_width > 1400:
            height = 800
        elif _window_width > 1200:
            height = 700
        elif _window_width > 992:
            height = 600
        elif _window_width > 768:
            height = 500
        elif _window_width > 576:
            height = 400
        else:
            height = 300
        # endregion

        # Create 1000 datasets for LapDistancePercentage -> round on 1 decimal
        self.df1['LDP_round']=self.df1.LapDistPct.round(1)
        self.df2['LDP_round']=self.df2.LapDistPct.round(1)

        # region CREATE FIGURE
        fig = go.Figure(
            layout=go.Layout(
                title=go.layout.Title(text='Speed Constancy Comparision'),
                height = height * 0.5))
        # endregion

        max_value_1 = self.df1.groupby('LDP_round').Speed.max()
        mean_value_1 = self.df1.groupby('LDP_round').Speed.mean()
        min_value_1 = self.df1.groupby('LDP_round').Speed.min()
        std_value_1 = self.df1.groupby('LDP_round').Speed.var()
        lon_value_1 = self.df1.groupby('LDP_round').Lon.max()
        lat_value_1 = self.df1.groupby('LDP_round').Lat.max()
        index_1 = max_value_1.index

        max_value_2 = self.df2.groupby('LDP_round').Speed.max()
        mean_value_2 = self.df2.groupby('LDP_round').Speed.mean()
        min_value_2 = self.df2.groupby('LDP_round').Speed.min()
        std_value_2 = self.df2.groupby('LDP_round').Speed.var()
        lon_value_2 = self.df2.groupby('LDP_round').Lon.max()
        lat_value_2 = self.df2.groupby('LDP_round').Lat.max()

        new_data = pd.DataFrame(data={'max_val_1': max_value_1, 'mean_val_1': mean_value_1, 'min_val_1': min_value_1, 'std_val_1': std_value_1, 'lon_val_1': lon_value_1, 'lat_val_1': lat_value_1, 'max_val_2': max_value_2, 'mean_val_2': mean_value_2, 'min_val_2': min_value_2, 'std_val_2': std_value_2, 'lon_val_2': lon_value_2, 'lat_val_2': lat_value_2, }, index = index_1)

        new_data['x_value'] = new_data.index
        new_data['var_coeff_1'] = new_data.std_val_1 / new_data.mean_val_1
        new_data['var_coeff_2'] = new_data.std_val_2 / new_data.mean_val_2
        new_data['mean_diff'] = new_data.mean_val_1 - new_data.mean_val_2

        
        fig.add_trace(go.Scatter(
            x = new_data.x_value,
            y = new_data.var_coeff_1.round(2),
            fill = 'tozeroy',
            fillcolor='rgba(30, 68, 136, 0.1)',
            name = self.df1_name,
            line=dict(color=COLOR.BLUE, width=0.5),
            visible = True,
            hovertemplate="variance %{y}"))
        
        fig.add_trace(go.Scatter(
            x = new_data.x_value,
            y = new_data.var_coeff_2.round(2),
            fill = 'tozeroy',
            fillcolor='rgba(253, 40, 38, 0.1)',
            name = self.df2_name,
            line=dict(color=COLOR.RED, width=0.5),
            visible = True,
            hovertemplate="variance %{y}"))
        
        fig.add_trace(go.Scatter(
            x = new_data.x_value,
            y = [new_data.var_coeff_1.mean()] * len(new_data.x_value),
            name = 'Mean ' + self.df1_name,
            line=dict(color=COLOR.BLUE, width=0.5),
            visible = True,
            hovertemplate=""))

        fig.add_trace(go.Scatter(
            x = new_data.x_value,
            y = [new_data.var_coeff_2.mean()] * len(new_data.x_value),
            name = 'Mean ' + self.df2_name,
            line=dict(color=COLOR.RED, width=0.5),
            visible = True,
            hovertemplate=""))

      
        fig.update_xaxes(title_text='Lap Distance in Percentage')
        fig.update_yaxes(title_text='Variance')

        fig.update_layout(
            autosize=True,
            separators=',.',
            minreducedwidth = 400,
            font_family = "'Roboto Condensed',sans-serif",
            title_font_size = TITLE_SIZE,
            font_color = COLOR.BLACK,
            title = dict(x=0.5, xanchor = 'center'),
            legend_title_text='Stint',
            hovermode='x',            
            modebar_remove = ['resetScale'],
            modebar_add = ['drawline', 'drawopenpath', 'drawcircle', 'drawrect', 'eraseshape'],         
            margin = dict(t=140),
            template = 'plotly_white')


        # region CREATE TRACKMAP
        fig2 = make_subplots(
            rows = 1, cols=2, 
            shared_yaxes=True,
            shared_xaxes=True,
            horizontal_spacing=0.05,
            subplot_titles=[self.df1_name, self.df2_name])
        # endregion

        # region ADD DATA
        fig2.add_trace(go.Scatter(
            x=new_data.lon_val_1,
            y=new_data.lat_val_1,
            mode='markers',
            marker = dict(size=16, color=new_data.var_coeff_1, colorscale='Aggrnyl', showscale=True),
            name = '',
            customdata=new_data.var_coeff_1.round(2),
            # CHANGE FOR EVALUATE THE TRACK CORNERS
            # customdata=data_fastest_lap_df1.LDP_round,
            hovertemplate="Variance: %{customdata}",
            visible = True,
            showlegend = False),
            row=1, col=1)

        fig2.add_trace(go.Scatter(
            x=new_data.lon_val_2,
            y=new_data.lat_val_2,
            mode='markers',
            marker = dict(size=16, color=new_data.var_coeff_2, colorscale='Aggrnyl', showscale=False),
            name = '',
            customdata=new_data.var_coeff_2.round(2),
            # CHANGE FOR EVALUATE THE TRACK CORNERS
            # customdata=data_fastest_lap_df1.LDP_round,
            hovertemplate="Variance: %{customdata}",
            visible = True,
            showlegend = False),
            row=1, col=2)


        
        fig2.update_layout(legend=dict(
            yanchor="top",
            y=0.01,
            xanchor="left",
            x=0.99))

        fig2.update_layout(
            autosize = True,
            height = height, 
            font_family = "'Roboto Condensed',sans-serif",
            title_font_size = TITLE_SIZE,
            font_color = COLOR.BLACK,
            title = dict(x=0.5, xanchor = 'center', text='Speed Constanciy Map'),
            legend_title_text='Stint',
            hovermode='closest',            
            modebar_remove = ['resetScale'],
            modebar_add = ['drawline', 'drawopenpath', 'drawcircle', 'drawrect', 'eraseshape'],         
            margin = dict(t=140),
            template = 'plotly_white',
            xaxis=dict(scaleanchor='y', scaleratio=1.0), 
            xaxis2=dict(scaleanchor='y2', scaleratio=1.0))

        fig2.update_yaxes(
            visible = False,
            row=1, col=1)

        fig2.update_yaxes(
            visible = False,
            row=1, col=2)

        fig2.update_xaxes(
            visible = False)
        # endregion


        
        return (fig, fig2)
    # endregion

    def get_computer_performance_graph(self):
        fig, axes = plt.subplots(4, 2, figsize=(8,12), sharey='row')
        fig.suptitle('Computer Performance', fontsize=14, fontweight=600)

        self.df1.FrameRate.plot(title='Frame Rate '+self.df1_name, kind='hist', ax=axes[0, 0], bins=25, xlabel='frames per second', yticks=[], ylabel='')
        self.df2.FrameRate.plot(title='Frame Rate '+self.df2_name, kind='hist', ax=axes[0, 1], bins=25, xlabel='frames per second', yticks=[], ylabel='')
        self.df1.GpuUsage.plot(title='GPU Usage '+self.df1_name, kind='hist', ax=axes[1, 0], bins=25, xlabel='Percent of available thread took with a 1 sec avg', yticks=[], ylabel='')
        self.df2.GpuUsage.plot(title='GPU Usage '+self.df2_name, kind='hist', ax=axes[1, 1], bins=25, xlabel='Percent of available thread took with a 1 sec avg', yticks=[], ylabel='')
        self.df1.CpuUsageFG.plot(title='CPU Usage FG '+self.df1_name, kind='hist', ax=axes[2, 0], bins=25, xlabel='Percent of available tim fg thread took with a 1 sec avg', yticks=[], ylabel='')
        self.df2.CpuUsageFG.plot(title='CPU Usage FG '+self.df2_name, kind='hist', ax=axes[2, 1], bins=25, xlabel='Percent of available tim fg thread took with a 1 sec avg', yticks=[], ylabel='')
        self.df1.CpuUsageBG.plot(title ='CPU Usage BG '+self.df1_name, kind='hist', ax=axes[3, 0], bins=25, xlabel='Percent of available tim bg thread took with a 1 sec avg', yticks=[], ylabel='')
        self.df2.CpuUsageBG.plot(title ='CPU Usage BG '+self.df2_name, kind='hist', ax=axes[3, 1], bins=25, xlabel='Percent of available tim bg thread took with a 1 sec avg', yticks=[], ylabel='')

        plt.tight_layout()
        return fig


    def get_general_conditions_graph(self):

        fig, axes = plt.subplots(5, 2, figsize=(8,14), sharey='row')
        fig.suptitle('General Conditions', fontsize=14, fontweight=600)

        self.df1.TrackTemp.plot(title='Track Temp '+self.df1_name, kind='line', ax=axes[0, 0], xlabel='Session Progress', xticks=[], ylabel='°C')
        self.df2.TrackTemp.plot(title='Track Temp '+self.df2_name, kind='line', ax=axes[0, 1], xlabel='Session Progress', xticks=[], ylabel='°C')
        self.df1.AirTemp.plot(title='Air Temp '+self.df1_name, kind='line', ax=axes[1, 0], xlabel='Session Progress', xticks=[], ylabel='°C')
        self.df2.AirTemp.plot(title='Air Temp '+self.df2_name, kind='line', ax=axes[1, 1], xlabel='Session Progress', xticks=[], ylabel='°C')
        self.df1.AirDensity.plot(title='Air Density '+self.df1_name, kind='line', ax=axes[2, 0], xlabel='Session Progress', xticks=[], ylabel='kg/m^3')
        self.df2.AirDensity.plot(title='Air Density '+self.df2_name, kind='line', ax=axes[2, 1], xlabel='Session Progress', xticks=[], ylabel='kg/m^3')
        self.df1.AirPressure.plot(title='Air Pressure '+self.df1_name, kind='line', ax=axes[3, 0], xlabel='Session Progress', xticks=[], ylabel='mmHg')
        self.df2.AirPressure.plot(title='Air Pressure '+self.df2_name, kind='line', ax=axes[3, 1], xlabel='Session Progress', xticks=[], ylabel='mmHg')
        self.df1.RelativeHumidity.plot(title='Relative Humidity '+self.df1_name, kind='line', ax=axes[4, 0], xlabel='Session Progress', xticks=[], ylabel='%')
        self.df2.RelativeHumidity.plot(title='Relative Humidity '+self.df2_name, kind='line', ax=axes[4, 1], xlabel='Session Progress', xticks=[], ylabel='%')

        plt.tight_layout()
        return fig


    def get_car_setup_graph(self):

        fig, axes = plt.subplots(5, 2, figsize=(8,15), sharey='row')
        fig.suptitle('Car Setup', fontsize=14, fontweight=600)

        self.df1.dcABS.plot(title='ABS '+self.df1_name, kind='line', ax=axes[0, 0], xlabel='Session Progress', xticks=[], ylabel='Setting', drawstyle='steps-mid')
        self.df2.dcABS.plot(title='ABS '+self.df2_name, kind='line', ax=axes[0, 1], xlabel='Session Progress', xticks=[], ylabel='Setting', drawstyle='steps-mid')
        self.df1.dcTractionControl.plot(title='Traction Control '+self.df1_name, kind='line', ax=axes[1, 0], xlabel='Session Progress', xticks=[], ylabel='Setting', drawstyle='steps-mid')
        self.df2.dcTractionControl.plot(title='Traction Control '+self.df2_name, kind='line', ax=axes[1, 1], xlabel='Session Progress', xticks=[], ylabel='Setting', drawstyle='steps-mid')
        self.df1.dcBrakeBias.plot(title='Brake Bias '+self.df1_name, kind='line', ax=axes[2, 0], xlabel='Session Progress', xticks=[], ylabel='Setting', drawstyle='steps-mid')
        self.df2.dcBrakeBias.plot(title='Brake Bias '+self.df2_name, kind='line', ax=axes[2, 1], xlabel='Session Progress', xticks=[], ylabel='Setting', drawstyle='steps-mid')
        self.df1.PlayerTireCompound.plot(title='Tire Compound '+self.df1_name, kind='line', ax=axes[3, 0], xlabel='Session Progress', xticks=[], ylabel='Compound', drawstyle='steps-mid')
        self.df2.PlayerTireCompound.plot(title='Tire Compound '+self.df2_name, kind='line', ax=axes[3, 1], xlabel='Session Progress', xticks=[], ylabel='Compound', drawstyle='steps-mid')
        df1_cold_pressure = [self.df1.LFcoldPressure.min()/100, self.df1.RFcoldPressure.min()/100, self.df1.LRcoldPressure.min()/100, self.df1.RRcoldPressure.min()/100]
        df2_cold_pressure = [self.df2.LFcoldPressure.min()/100, self.df2.RFcoldPressure.min()/100, self.df2.LRcoldPressure.min()/100, self.df2.RRcoldPressure.min()/100]
        min_abs = min([min(df1_cold_pressure), min(df2_cold_pressure)])
        max_abs = max([max(df1_cold_pressure), max(df2_cold_pressure)])

        axes[4, 0].set_title('Cold Tire Pressure ' + self.df1_name)
        axes[4, 0].set_ylim([min_abs * 0.97, max_abs * 1.03])
        axes[4, 0].set_ylabel('bar')
        axes[4, 0].bar([0, 1, 2, 3], df1_cold_pressure, tick_label=['LF', 'RF', 'LR', 'RR'])
        axes[4, 1].set_title('Cold Tire Pressure ' + self.df2_name)
        axes[4, 1].bar([0, 1, 2, 3], df2_cold_pressure, tick_label=['LF', 'RF', 'LR', 'RR'])    

        plt.tight_layout()
        return fig


    def get_fuel_graph(self):

        fig, axes = plt.subplots(3, 2, figsize=(8,10), sharey='row')
        fig.suptitle('Fuel Status', fontsize=14, fontweight=600)

        df1_fuel_level = self.df1.groupby('Lap').FuelLevel
        df2_fuel_level = self.df2.groupby('Lap').FuelLevel
        df1_fuel_use_per_lap = self.df1.groupby('Lap').FuelUsePerHour
        df2_fuel_use_per_lap = self.df2.groupby('Lap').FuelUsePerHour

        df1_fuel_level.mean().plot(title='Fuel Level '+self.df1_name, kind='line', ax=axes[0, 0], xlabel='Lap', ylabel='litres', drawstyle='steps-mid', label='per lap')
        axes[0, 0].plot(df1_fuel_level.mean().index, [df1_fuel_level.mean().mean()] * len(df1_fuel_level.mean().index), label='mean')
        axes[0, 0].legend(frameon=False)
        df2_fuel_level.mean().plot(title='Fuel Level '+self.df2_name, kind='line', ax=axes[0, 1], xlabel='Lap', ylabel='litres', drawstyle='steps-mid', label='per lap')
        axes[0, 1].plot(df2_fuel_level.mean().index, [df2_fuel_level.mean().mean()] * len(df2_fuel_level.mean().index), label='mean')
        axes[0, 1].legend(frameon=False)

        df1_fuel_use_per_lap.mean().plot(title='Fuel Consumption '+self.df1_name, kind='line', ax=axes[1, 0], xlabel='Lap', ylabel='litres per hour',drawstyle='steps-mid', label='per lap')
        axes[1, 0].plot(df1_fuel_use_per_lap.mean().index, [df1_fuel_use_per_lap.mean().mean()] * len(df1_fuel_use_per_lap.mean().index), label='mean')
        axes[1, 0].legend(frameon=False)
        df2_fuel_use_per_lap.mean().plot(title='Fuel Consumption '+self.df2_name, kind='line', ax=axes[1, 1], xlabel='Lap', ylabel='litres per hour',drawstyle='steps-mid', label='per lap')
        axes[1, 1].plot(df2_fuel_use_per_lap.mean().index, [df2_fuel_use_per_lap.mean().mean()] * len(df2_fuel_use_per_lap.mean().index), label='mean')
        axes[1, 1].legend(frameon=False)

        self.df1[self.df1.Lap == self.df1_fastest_lap].plot(title='Fuel consumption ' + self.df1_name + ': Fastest lap ' + str(self.df1_fastest_lap), ax=axes[2, 0], kind='scatter', x='Lat', y='Lon', s=50, c='FuelUsePerHour', cmap=mpl.colors.LinearSegmentedColormap.from_list("", ['maroon','brown', 'orange', 'yellow']))

        self.df2[self.df2.Lap == self.df2_fastest_lap].plot(title='Fuel consumption ' + self.df2_name + ': Fastest lap ' + str(self.df2_fastest_lap), ax=axes[2, 1], kind='scatter', x='Lat', y='Lon', s=50, c='FuelUsePerHour', cmap=mpl.colors.LinearSegmentedColormap.from_list("", ['maroon','brown', 'orange', 'yellow']))

        axes[2, 0].plot(self.df1.iloc[0]['Lat'], self.df1.iloc[0]['Lon'], "ro", label='start/finish line', ms=10)
        axes[2, 1].plot(self.df2.iloc[0]['Lat'], self.df2.iloc[0]['Lon'], "ro", label='start/finsih line', ms=10)

        for axe in [axes[2, 0], axes[2, 1]]:
            for value in 'top right left bottom'.split():
                axe.spines[value].set_visible(False)
            axe.set_xlabel('')
            axe.set_ylabel('')

        axes[2, 0].tick_params(left = False, right = False, labelleft = False, labelbottom = False, bottom = False)
        axes[2, 1].tick_params(left = False, right = False, labelleft = False, labelbottom = False, bottom = False)

        axes[2, 0].legend(frameon=False)
        axes[2, 1].legend(frameon=False)

        plt.tight_layout()
        return fig


    def get_tyre_pressure_graph(self):

        fig, axes = plt.subplots(5, 2, figsize=(8,15), sharey=True)
        fig.suptitle('Tyre pressure', fontsize=14, fontweight=600)

        (self.df1.LFpressure/100).plot(ax=axes[0,0], label='Left Front', title='Tyre Pressure ' + self.df1_name, xlabel='Session Progress', xticks=[], ylabel='bar or psi?')
        (self.df1.RFpressure/100).plot(ax=axes[0,0], label='Right Front')
        (self.df1.LRpressure/100).plot(ax=axes[0,0], label='Left Rear')
        (self.df1.RRpressure/100).plot(ax=axes[0,0], label='Right Rear')
        axes[0,0].legend(frameon=False)
        (self.df2.LFpressure/100).plot(ax=axes[0,1], label='Left Front', title='Tyre Pressure ' + self.df2_name, xlabel='Session Progress', xticks=[], ylabel='bar or psi?')
        (self.df2.RFpressure/100).plot(ax=axes[0,1], label='Right Front')
        (self.df2.LRpressure/100).plot(ax=axes[0,1], label='Left Rear')
        (self.df2.RRpressure/100).plot(ax=axes[0,1], label='Right Rear')
        axes[0,1].legend(frameon=False)

        (self.df1.groupby('Lap').LFpressure.max()/100).plot(ax=axes[1,0], drawstyle='steps-mid', title='Left Front Tyre ' + self.df1_name, label='max', ylabel='bar or psi?')
        (self.df1.groupby('Lap').LFpressure.mean()/100).plot(ax=axes[1,0], label='mean')
        (self.df1.groupby('Lap').LFpressure.min()/100).plot(ax=axes[1,0], drawstyle='steps-mid', label='min')
        (self.df2.groupby('Lap').LFpressure.max()/100).plot(ax=axes[1,1], drawstyle='steps-mid', title='Left Front Tyre ' + self.df2_name, label='max', ylabel='bar or psi?')
        (self.df2.groupby('Lap').LFpressure.mean()/100).plot(ax=axes[1,1], label='mean')
        (self.df2.groupby('Lap').LFpressure.min()/100).plot(ax=axes[1,1], drawstyle='steps-mid', label='min')
        axes[1,0].legend(frameon=False)

        (self.df1.groupby('Lap').RFpressure.max()/100).plot(ax=axes[2,0], drawstyle='steps-mid', title='Right Front Tyre ' + self.df1_name, label='max', ylabel='bar or psi?')
        (self.df1.groupby('Lap').RFpressure.mean()/100).plot(ax=axes[2,0], label='mean')
        (self.df1.groupby('Lap').RFpressure.min()/100).plot(ax=axes[2,0], drawstyle='steps-mid', label='min')
        (self.df2.groupby('Lap').RFpressure.max()/100).plot(ax=axes[2,1], drawstyle='steps-mid', title='Right Front Tyre ' + self.df2_name, label='max', ylabel='bar or psi?')
        (self.df2.groupby('Lap').RFpressure.mean()/100).plot(ax=axes[2,1], label='mean')
        (self.df2.groupby('Lap').RFpressure.min()/100).plot(ax=axes[2,1], drawstyle='steps-mid', label='min')
        axes[2,0].legend(frameon=False)

        (self.df1.groupby('Lap').LRpressure.max()/100).plot(ax=axes[3,0], drawstyle='steps-mid', title='Left Rear Tyre ' + self.df1_name, label='max', ylabel='bar or psi?')
        (self.df1.groupby('Lap').LRpressure.mean()/100).plot(ax=axes[3,0], label='mean')
        (self.df1.groupby('Lap').LRpressure.min()/100).plot(ax=axes[3,0], drawstyle='steps-mid', label='min')
        (self.df2.groupby('Lap').LRpressure.max()/100).plot(ax=axes[3,1], drawstyle='steps-mid', title='Left Rear Tyre ' + self.df2_name, label='max', ylabel='bar or psi?')
        (self.df2.groupby('Lap').LRpressure.mean()/100).plot(ax=axes[3,1], label='mean')
        (self.df2.groupby('Lap').LRpressure.min()/100).plot(ax=axes[3,1], drawstyle='steps-mid', label='min')
        axes[3,0].legend(frameon=False)

        (self.df1.groupby('Lap').RRpressure.max()/100).plot(ax=axes[4,0], drawstyle='steps-mid', title='Right Rear Tyre ' + self.df1_name, label='max', ylabel='bar or psi?')
        (self.df1.groupby('Lap').RRpressure.mean()/100).plot(ax=axes[4,0], label='mean')
        (self.df1.groupby('Lap').RRpressure.min()/100).plot(ax=axes[4,0], drawstyle='steps-mid', label='min')
        (self.df2.groupby('Lap').RRpressure.max()/100).plot(ax=axes[4,1], drawstyle='steps-mid', title='Right Rear Tyre ' + self.df2_name, label='max', ylabel='bar or psi?')
        (self.df2.groupby('Lap').RRpressure.mean()/100).plot(ax=axes[4,1], label='mean')
        (self.df2.groupby('Lap').RRpressure.min()/100).plot(ax=axes[4,1], drawstyle='steps-mid', label='min')
        axes[4,0].legend(frameon=False)

        plt.tight_layout()
        return fig


    def get_tyre_temperature_graph(self):

        fig, axes = plt.subplots(5, 2, figsize=(8,15), sharey='row')
        fig.suptitle('Tyre temperature', fontsize=14, fontweight=600)

        self.df1['LFtempMean'] = (self.df1.LFtempL + self.df1.LFtempL + self.df1.LFtempR) / 3
        self.df1['RFtempMean'] = (self.df1.RFtempL + self.df1.RFtempL + self.df1.RFtempR) / 3
        self.df1['LRtempMean'] = (self.df1.LRtempL + self.df1.LRtempL + self.df1.LRtempR) / 3
        self.df1['RRtempMean'] = (self.df1.RRtempL + self.df1.RRtempL + self.df1.RRtempR) / 3
        self.df2['LFtempMean'] = (self.df2.LFtempL + self.df2.LFtempL + self.df2.LFtempR) / 3
        self.df2['RFtempMean'] = (self.df2.RFtempL + self.df2.RFtempL + self.df2.RFtempR) / 3
        self.df2['LRtempMean'] = (self.df2.LRtempL + self.df2.LRtempL + self.df2.LRtempR) / 3
        self.df2['RRtempMean'] = (self.df2.RRtempL + self.df2.RRtempL + self.df2.RRtempR) / 3

        self.df1.groupby('Lap')[['LFtempMean', 'RFtempMean', 'LRtempMean', 'RRtempMean']].mean().plot(ax=axes[0,0], title='Tyre Temp (mean) ' + self.df1_name,
                xlabel='Session Progress', xticks=[], ylabel='°C')
        axes[0,0].legend(labels=['Left Front', 'Right Front', 'Left Rear', 'Right Rear'], frameon=False, fontsize=8)
        self.df2.groupby('Lap')[['LFtempMean', 'RFtempMean', 'LRtempMean', 'RRtempMean']].mean().plot(ax=axes[0,1], title='Tyre Temp (mean) ' + self.df2_name,
                xlabel='Session Progress', xticks=[], ylabel='°C')
        axes[0,1].legend(labels=['Left Front', 'Right Front', 'Left Rear', 'Right Rear'], frameon=False, fontsize=8)

        df1_tyretemp_lf = self.df1.groupby('Lap')[['LFtempL', 'LFtempM', 'LFtempR']].mean()
        df2_tyretemp_lf = self.df2.groupby('Lap')[['LFtempL', 'LFtempM', 'LFtempR']].mean()
        tyretemp_lf_min = min(df1_tyretemp_lf.min().min(), df2_tyretemp_lf.min().min())
        tyretemp_lf_max = max(df1_tyretemp_lf.max().max(), df2_tyretemp_lf.max().max())
        df1_tyretemp_lf.plot(kind='bar', ax=axes[1,0], title='Tyre Temp Left Front ' + self.df1_name, 
                ylim=(tyretemp_lf_min * 0.98, tyretemp_lf_max * 1.02), ylabel='°C', xlabel='Lap')
        df2_tyretemp_lf.plot(kind='bar', ax=axes[1,1], title='Tyre Temp Left Front ' + self.df2_name,
                ylim=(tyretemp_lf_min * 0.98, tyretemp_lf_max * 1.02), xlabel='Lap')
        axes[1,0].legend(labels=['Left', 'Middle', 'Right'], frameon=False, fontsize=8)
        axes[1,1].legend(labels=['Left', 'Middle', 'Right'], frameon=False, fontsize=8)

        df1_tyretemp_rf = self.df1.groupby('Lap')[['RFtempL', 'RFtempM', 'RFtempR']].mean()
        df2_tyretemp_rf = self.df2.groupby('Lap')[['RFtempL', 'RFtempM', 'RFtempR']].mean()
        tyretemp_rf_min = min(df1_tyretemp_rf.min().min(), df2_tyretemp_rf.min().min())
        tyretemp_rf_max = max(df1_tyretemp_rf.max().max(), df2_tyretemp_rf.max().max())
        df1_tyretemp_rf.plot(kind='bar', ax=axes[2,0], title='Tyre Temp Right Front ' + self.df1_name, 
                ylim=(tyretemp_rf_min * 0.98, tyretemp_rf_max * 1.02), ylabel='°C', xlabel='Lap')
        df2_tyretemp_rf.plot(kind='bar', ax=axes[2,1], title='Tyre Temp Right Front ' + self.df2_name,
                ylim=(tyretemp_rf_min * 0.98, tyretemp_rf_max * 1.02), xlabel='Lap')
        axes[2,0].legend(labels=['Left', 'Middle', 'Right'], frameon=False, fontsize=8)
        axes[2,1].legend(labels=['Left', 'Middle', 'Right'], frameon=False, fontsize=8)

        df1_tyretemp_lr = self.df1.groupby('Lap')[['LRtempL', 'LRtempM', 'LRtempR']].mean()
        df2_tyretemp_lr = self.df2.groupby('Lap')[['LRtempL', 'LRtempM', 'LRtempR']].mean()
        tyretemp_lr_min = min(df1_tyretemp_lr.min().min(), df2_tyretemp_lr.min().min())
        tyretemp_lr_max = max(df1_tyretemp_lr.max().max(), df2_tyretemp_lr.max().max())
        df1_tyretemp_lr.plot(kind='bar', ax=axes[3,0], title='Tyre Temp Left Rear ' + self.df1_name, 
                ylim=(tyretemp_lr_min * 0.98, tyretemp_lr_max * 1.02), ylabel='°C', xlabel='Lap')
        df2_tyretemp_lr.plot(kind='bar', ax=axes[3,1], title='Tyre Temp Left Rear ' + self.df2_name,
                ylim=(tyretemp_lr_min * 0.98, tyretemp_lr_max * 1.02), xlabel='Lap')
        axes[3,0].legend(labels=['Left', 'Middle', 'Right'], frameon=False, fontsize=8)
        axes[3,1].legend(labels=['Left', 'Middle', 'Right'], frameon=False, fontsize=8)

        df1_tyretemp_rr = self.df1.groupby('Lap')[['RRtempL', 'RRtempM', 'RRtempR']].mean()
        df2_tyretemp_rr = self.df2.groupby('Lap')[['RRtempL', 'RRtempM', 'RRtempR']].mean()
        tyretemp_rr_min = min(df1_tyretemp_rr.min().min(), df2_tyretemp_rr.min().min())
        tyretemp_rr_max = max(df1_tyretemp_rr.max().max(), df2_tyretemp_rr.max().max())
        df1_tyretemp_rr.plot(kind='bar', ax=axes[4,0], title='Tyre Temp Right Rear ' + self.df1_name, 
                ylim=(tyretemp_rr_min * 0.98, tyretemp_rr_max * 1.02), ylabel='°C', xlabel='Lap')
        df2_tyretemp_rr.plot(kind='bar', ax=axes[4,1], title='Tyre Temp Right Rear ' + self.df2_name,
                ylim=(tyretemp_rr_min * 0.98, tyretemp_rr_max * 1.02), xlabel='Lap')
        axes[4,0].legend(labels=['Left', 'Middle', 'Right'], frameon=False, fontsize=8)
        axes[4,1].legend(labels=['Left', 'Middle', 'Right'], frameon=False, fontsize=8)

        plt.tight_layout()
        return fig

    
    def get_ride_height_graph(self):
        fig, axes = plt.subplots(4, 2, figsize=(8,15), sharey=True)
        fig.suptitle('Ride Height', fontsize=14, fontweight=600)


        (self.df1.groupby(by='Lap').LFrideHeight.max()*100).plot(ax=axes[0,0], drawstyle='steps-mid', label = 'max', ylabel='centimeter', title='Left Front Tyre ' + self.df1_name)
        (self.df1.groupby(by='Lap').LFrideHeight.mean()*100).plot(ax=axes[0,0], drawstyle='steps-mid', label = 'mean')
        (self.df1.groupby(by='Lap').LFrideHeight.min()*100).plot(ax=axes[0,0], drawstyle='steps-mid', label = 'mmin')
        axes[0,0].legend(frameon=False)

        (self.df2.groupby(by='Lap').LFrideHeight.max()*100).plot(ax=axes[0,1], drawstyle='steps-mid', label = 'max', ylabel='centimeter', title='Left Front Tyre ' + self.df2_name)
        (self.df2.groupby(by='Lap').LFrideHeight.mean()*100).plot(ax=axes[0,1], drawstyle='steps-mid', label = 'mean')
        (self.df2.groupby(by='Lap').LFrideHeight.min()*100).plot(ax=axes[0,1], drawstyle='steps-mid', label = 'mmin')


        (self.df1.groupby(by='Lap').RFrideHeight.max()*100).plot(ax=axes[1,0], drawstyle='steps-mid', label = 'max', ylabel='centimeter', title='Right Front Tyre ' + self.df1_name)
        (self.df1.groupby(by='Lap').RFrideHeight.mean()*100).plot(ax=axes[1,0], drawstyle='steps-mid', label = 'mean')
        (self.df1.groupby(by='Lap').RFrideHeight.min()*100).plot(ax=axes[1,0], drawstyle='steps-mid', label = 'mmin')
        axes[0,0].legend(frameon=False)

        (self.df2.groupby(by='Lap').RFrideHeight.max()*100).plot(ax=axes[1,1], drawstyle='steps-mid', label = 'max', ylabel='centimeter', title='Right Front Tyre ' + self.df2_name)
        (self.df2.groupby(by='Lap').RFrideHeight.mean()*100).plot(ax=axes[1,1], drawstyle='steps-mid', label = 'mean')
        (self.df2.groupby(by='Lap').RFrideHeight.min()*100).plot(ax=axes[1,1], drawstyle='steps-mid', label = 'mmin')


        (self.df1.groupby(by='Lap').LRrideHeight.max()*100).plot(ax=axes[2,0], drawstyle='steps-mid', label = 'max', ylabel='centimeter', title='Left Rear Tyre ' + self.df1_name)
        (self.df1.groupby(by='Lap').LRrideHeight.mean()*100).plot(ax=axes[2,0], drawstyle='steps-mid', label = 'mean')
        (self.df1.groupby(by='Lap').LRrideHeight.min()*100).plot(ax=axes[2,0], drawstyle='steps-mid', label = 'mmin')
        axes[0,0].legend(frameon=False)

        (self.df2.groupby(by='Lap').LRrideHeight.max()*100).plot(ax=axes[2,1], drawstyle='steps-mid', label = 'max', ylabel='centimeter', title='Left Rear Tyre ' + self.df2_name)
        (self.df2.groupby(by='Lap').LRrideHeight.mean()*100).plot(ax=axes[2,1], drawstyle='steps-mid', label = 'mean')
        (self.df2.groupby(by='Lap').LRrideHeight.min()*100).plot(ax=axes[2,1], drawstyle='steps-mid', label = 'mmin')


        (self.df1.groupby(by='Lap').RRrideHeight.max()*100).plot(ax=axes[3,0], drawstyle='steps-mid', label = 'max', ylabel='centimeter', title='Right Rear Tyre ' + self.df1_name)
        (self.df1.groupby(by='Lap').RRrideHeight.mean()*100).plot(ax=axes[3,0], drawstyle='steps-mid', label = 'mean')
        (self.df1.groupby(by='Lap').RRrideHeight.min()*100).plot(ax=axes[3,0], drawstyle='steps-mid', label = 'mmin')
        axes[0,0].legend(frameon=False)

        (self.df2.groupby(by='Lap').RRrideHeight.max()*100).plot(ax=axes[3,1], drawstyle='steps-mid', label = 'max', ylabel='centimeter', title='Right Rear Tyre ' + self.df2_name)
        (self.df2.groupby(by='Lap').RRrideHeight.mean()*100).plot(ax=axes[3,1], drawstyle='steps-mid', label = 'mean')
        (self.df2.groupby(by='Lap').RRrideHeight.min()*100).plot(ax=axes[3,1], drawstyle='steps-mid', label = 'mmin')

        plt.tight_layout()
        return fig
    

    def get_brake_graph(self):
     
        fig, axes = plt.subplots(6, 2, figsize=(8,22), sharey='row')
        fig.suptitle('Brake Overview', fontsize=14, fontweight=600)


        # BRAKE Intensity Total
        sns.violinplot(data=self.df1[self.df1.Brake > 0], y='Brake', cut=0, inner=None, linewidth=1, color='green', ax=axes[0, 0])
        sns.violinplot(data=self.df2[self.df2.Brake > 0], y='Brake', cut=0, inner=None, linewidth=1, color='green', ax=axes[0, 1])
        axes[0, 0].set_title('Brake Intensity Total ' + self.df1_name)
        axes[0, 0].set_ylabel('Intensity in %')
        axes[0, 0].set_xlabel('Total Count')
        axes[0, 1].set_title('Brake Intensity Total ' + self.df2_name)
        axes[0, 1].set_xlabel('Total Count')


        # BRAKE Intesity Fastest Lap
        sns.violinplot(data=self.df1[(self.df1.Brake > 0) & (self.df1.Lap == self.df1_fastest_lap)], y='Brake', cut=0, inner=None, linewidth=1, color='green', ax=axes[1, 0])
        sns.violinplot(data=self.df2[(self.df2.Brake > 0) & (self.df2.Lap == self.df2_fastest_lap)], y='Brake', cut=0, inner=None, linewidth=1, color='green', ax=axes[1, 1])
        axes[1, 0].set_title('Brake Intensity ' + self.df1_name + ' fastet lap ' + str(self.df1_fastest_lap))
        axes[1, 0].set_ylabel('Intensity in %')
        axes[1, 0].set_xlabel('Total Count')
        axes[1, 1].set_title('Brake Intensity ' + self.df2_name + ' fastet lap ' + str(self.df2_fastest_lap))
        axes[1, 1].set_xlabel('Total Count')

        # BRAKE Intensity Lap Overview
        sns.violinplot(data=self.df1[self.df1.Brake > 0], x='Lap', y='Brake', cut=0, inner=None, linewidth=0, color='green', ax=axes[2, 0])
        sns.violinplot(data=self.df2[self.df2.Brake > 0], x='Lap', y='Brake', cut=0, inner=None, linewidth=0, color='green', ax=axes[2, 1])
        axes[2, 0].set_title('Brake Intensity ' + self.df1_name)
        axes[2, 0].set_ylabel('Intensity in %')
        axes[2, 1].set_title('Brake Intensity ' + self.df2_name)


        # BRAKE POINTS
        self.df1[self.df1.Lap == self.df1_fastest_lap].plot(title='Brake Points ' + self.df1_name + ': Fastest lap ' + str(self.df1_fastest_lap), ax=axes[3, 0], kind='scatter', x='Lat', y='Lon', s=50, c='Brake', cmap=mpl.colors.LinearSegmentedColormap.from_list("", ['maroon','brown', 'orange', 'yellow']))
        self.df2[self.df2.Lap == self.df2_fastest_lap].plot(title='Brake Points ' + self.df2_name + ': Fastest lap ' + str(self.df2_fastest_lap), ax=axes[3, 1], kind='scatter', x='Lat', y='Lon', s=50, c='Brake', cmap=mpl.colors.LinearSegmentedColormap.from_list("", ['maroon','brown', 'orange', 'yellow']))
        axes[3, 0].plot(self.df1.iloc[0]['Lat'], self.df1.iloc[0]['Lon'], "ro", label='start/finish line', ms=10)
        axes[3, 1].plot(self.df2.iloc[0]['Lat'], self.df2.iloc[0]['Lon'], "ro", label='start/finsih line', ms=10)
        for axe in [axes[3, 0], axes[3, 1]]:
            for value in 'top right left bottom'.split():
                axe.spines[value].set_visible(False)
            axe.set_xlabel('')
            axe.set_ylabel('')
        axes[3, 0].tick_params(left = False, right = False, labelleft = False, labelbottom = False, bottom = False)
        axes[3, 1].tick_params(left = False, right = False, labelleft = False, labelbottom = False, bottom = False)
        axes[3, 0].legend(frameon=False)
        axes[3, 1].legend(frameon=False)


        # ABS percentage
        x1 = list(self.df1.Lap.unique())
        y1 = []
        for lap in x1:
            denominator = self.df1[(self.df1.Lap == lap) & (self.df1.Brake > 0)].BrakeABSactive.count()
            numerator = self.df1[(self.df1.Lap == lap) & (self.df1.Brake > 0) & (self.df1.BrakeABSactive == 1)].BrakeABSactive.count()
            y1.append(numerator/denominator*100)

        x2 = list(self.df2.Lap.unique())
        y2 = []
        for lap in x2:
            denominator = self.df2[(self.df2.Lap == lap) & (self.df2.Brake > 0)].BrakeABSactive.count()
            numerator = self.df2[(self.df2.Lap == lap) & (self.df2.Brake > 0) & (self.df2.BrakeABSactive == 1)].BrakeABSactive.count()
            y2.append(numerator/denominator*100)

        axes[4,0].bar(x=x1, height=y1, label='ABS pct.', color='green')
        axes[4,0].plot(x1, [(sum(y1) / len(y1))]*len(x1), color='red', label='mean')
        axes[4,0].set_title('ABS usage ' + self.df1_name)
        axes[4,0].set_ylabel('Break under ABS in %')
        axes[4,0].set_xlabel('Lap')
        axes[4,1].bar(x=x2, height=y2)
        axes[4,1].plot(x2, [(sum(y2) / len(y2))]*len(x2), color='red', label='mean')
        axes[4,1].set_title('ABS usage ' + self.df2_name)
        axes[4,1].set_xlabel('Lap')
        axes[4,1].bar(x=x2, height=y2, color='green')
        axes[4,0].legend(frameon=False)

        y_min = min(min(y1), min(y2))
        y_max = max(max(y1), max(y2))
        axes[4,0].set_ylim(y_min * 0.90 , y_max * 1.10)


        # ABS BRAKE POINTS
        self.df1[self.df1.Lap == self.df1_fastest_lap].plot(title='ABS Brake Points ' + self.df1_name + ': Fastest lap ' + str(self.df1_fastest_lap), ax=axes[5, 0], kind='scatter', x='Lat', y='Lon', s=50, c='BrakeABSactive', cmap=mpl.colors.LinearSegmentedColormap.from_list("", ['maroon','brown', 'orange', 'yellow']))
        self.df2[self.df2.Lap == self.df2_fastest_lap].plot(title='ABS Brake Points ' + self.df2_name + ': Fastest lap ' + str(self.df2_fastest_lap), ax=axes[5, 1], kind='scatter', x='Lat', y='Lon', s=50, c='BrakeABSactive', cmap=mpl.colors.LinearSegmentedColormap.from_list("", ['maroon','brown', 'orange', 'yellow']))
        axes[5, 0].plot(self.df1.iloc[0]['Lat'], self.df1.iloc[0]['Lon'], "ro", label='start/finish line', ms=10)
        axes[5, 1].plot(self.df2.iloc[0]['Lat'], self.df2.iloc[0]['Lon'], "ro", label='start/finsih line', ms=10)
        for axe in [axes[5, 0], axes[5, 1]]:
            for value in 'top right left bottom'.split():
                axe.spines[value].set_visible(False)
            axe.set_xlabel('')
            axe.set_ylabel('')
        axes[5, 0].tick_params(left = False, right = False, labelleft = False, labelbottom = False, bottom = False)
        axes[5, 1].tick_params(left = False, right = False, labelleft = False, labelbottom = False, bottom = False)
        axes[5, 0].legend(frameon=False)
        axes[5, 1].legend(frameon=False)
        plt.tight_layout()
        return fig


    def get_throttle_graph(self):

        fig, axes = plt.subplots(7, 2, figsize=(8,27), sharey='row')
        fig.suptitle('Throttle Overview', fontsize=14, fontweight=600)

        # Throttle Intensity Total
        sns.violinplot(data=self.df1, y='ThrottleRaw', cut=0, inner=None, linewidth=1, color='blue', ax=axes[0, 0])
        sns.violinplot(data=self.df2, y='ThrottleRaw', cut=0, inner=None, linewidth=1, color='blue', ax=axes[0, 1])
        axes[0, 0].set_title('Throttle Intensity Total ' + self.df1_name)
        axes[0, 0].set_ylabel('Intensity in %')
        axes[0, 0].set_xlabel('Total Count')
        axes[0, 1].set_title('Throttle Intensity Total ' + self.df2_name)
        axes[0, 1].set_xlabel('Total Count')

        # Hist fastest lap
        self.df1[self.df1.Lap == self.df1_fastest_lap].ThrottleRaw.plot(ax=axes[1, 0], title='Throttle ' + self.df1_name + ' Fastest Lap ' + str(self.df1_fastest_lap), xlabel='Throttle in % ', kind='hist', bins=20, ylabel='count')
        axes[1, 0].tick_params(left = False, right = False, labelleft = False)
        self.df2[self.df2.Lap == self.df2_fastest_lap].ThrottleRaw.plot(ax=axes[1, 1], title='Throttle ' + self.df2_name + ' Fastest Lap ' + str(self.df2_fastest_lap), xlabel='Throttle in % ', kind='hist', bins=20, ylabel='count')
        axes[1, 1].tick_params(left = False, right = False, labelleft = False)

        # Throttle Map
        self.df1[self.df1.Lap == self.df1_fastest_lap].plot(title='Throttle Map ' + self.df1_name + ': Fastest lap ' + str(self.df1_fastest_lap), ax=axes[2, 0], kind='scatter', x='Lat', y='Lon', s=50, c='ThrottleRaw', cmap=mpl.colors.LinearSegmentedColormap.from_list("", ['maroon','brown', 'orange', 'yellow']))
        self.df2[self.df2.Lap == self.df2_fastest_lap].plot(title='Throttle Map ' + self.df2_name + ': Fastest lap ' + str(self.df2_fastest_lap), ax=axes[2, 1], kind='scatter', x='Lat', y='Lon', s=50, c='ThrottleRaw', cmap=mpl.colors.LinearSegmentedColormap.from_list("", ['maroon','brown', 'orange', 'yellow']))
        axes[2, 0].plot(self.df1.iloc[0]['Lat'], self.df1.iloc[0]['Lon'], "ro", label='start/finish line', ms=10)
        axes[2, 1].plot(self.df2.iloc[0]['Lat'], self.df2.iloc[0]['Lon'], "ro", label='start/finsih line', ms=10)
        for axe in [axes[2, 0], axes[2, 1]]:
            for value in 'top right left bottom'.split():
                axe.spines[value].set_visible(False)
            axe.set_xlabel('')
            axe.set_ylabel('')
        axes[2, 0].tick_params(left = False, right = False, labelleft = False, labelbottom = False, bottom = False)
        axes[2, 1].tick_params(left = False, right = False, labelleft = False, labelbottom = False, bottom = False)
        axes[2, 0].legend(frameon=False)
        axes[2, 1].legend(frameon=False)

        # Gear Usage
        self.df1.groupby('Gear').Gear.count().plot(kind='bar', ax=axes[3,0], title='Gear Usage ' + self.df1_name, ylabel='count')
        self.df2.groupby('Gear').Gear.count().plot(kind='bar', ax=axes[3,1], title='Gear Usage ' + self.df2_name, ylabel='count')
        axes[3, 0].tick_params(left = False, right = False, labelleft = False)
        axes[3, 1].tick_params(left = False, right = False, labelleft = False)

        # Gear Map
        self.df1[self.df1.Lap == self.df1_fastest_lap].plot(title='Gear Map ' + self.df1_name + ': Fastest lap ' + str(self.df1_fastest_lap), ax=axes[4, 0], kind='scatter', x='Lat', y='Lon', s=50, c='Gear', cmap=mpl.colors.LinearSegmentedColormap.from_list("", ['maroon','brown', 'orange', 'yellow']))
        self.df2[self.df2.Lap == self.df2_fastest_lap].plot(title='Gear Map ' + self.df2_name + ': Fastest lap ' + str(self.df2_fastest_lap), ax=axes[4, 1], kind='scatter', x='Lat', y='Lon', s=50, c='Gear', cmap=mpl.colors.LinearSegmentedColormap.from_list("", ['maroon','brown', 'orange', 'yellow']))
        axes[4, 0].plot(self.df1.iloc[0]['Lat'], self.df1.iloc[0]['Lon'], "ro", label='start/finish line', ms=10)
        axes[4, 1].plot(self.df2.iloc[0]['Lat'], self.df2.iloc[0]['Lon'], "ro", label='start/finsih line', ms=10)
        for axe in [axes[4, 0], axes[4, 1]]:
            for value in 'top right left bottom'.split():
                axe.spines[value].set_visible(False)
            axe.set_xlabel('')
            axe.set_ylabel('')
        axes[4, 0].tick_params(left = False, right = False, labelleft = False, labelbottom = False, bottom = False)
        axes[4, 1].tick_params(left = False, right = False, labelleft = False, labelbottom = False, bottom = False)
        axes[4, 0].legend(frameon=False)
        axes[4, 1].legend(frameon=False)

        # RPM box plot
        self.df1.RPM.plot(ax=axes[5, 0], title='RPM ' + self.df1_name, xlabel='RPM', kind='hist', bins=20, ylabel='count')
        axes[5, 0].tick_params(left = False, right = False, labelleft = False)
        self.df2.RPM.plot(ax=axes[5, 1], title='RPM ' + self.df2_name, xlabel='RPM', kind='hist', bins=20, ylabel='count')
        axes[5, 1].tick_params(left = False, right = False, labelleft = False)

        # RPM Map
        self.df1[self.df1.Lap == self.df1_fastest_lap].plot(title='RPM Map ' + self.df1_name + ': Fastest lap ' + str(self.df1_fastest_lap), ax=axes[6, 0], kind='scatter', x='Lat', y='Lon', s=50, c='RPM', cmap=mpl.colors.LinearSegmentedColormap.from_list("", ['maroon','brown', 'orange', 'yellow']))
        self.df2[self.df2.Lap == self.df2_fastest_lap].plot(title='RPM Map ' + self.df2_name + ': Fastest lap ' + str(self.df2_fastest_lap), ax=axes[6, 1], kind='scatter', x='Lat', y='Lon', s=50, c='RPM', cmap=mpl.colors.LinearSegmentedColormap.from_list("", ['maroon','brown', 'orange', 'yellow']))
        axes[6, 0].plot(self.df1.iloc[0]['Lat'], self.df1.iloc[0]['Lon'], "ro", label='start/finish line', ms=10)
        axes[6, 1].plot(self.df2.iloc[0]['Lat'], self.df2.iloc[0]['Lon'], "ro", label='start/finsih line', ms=10)
        for axe in [axes[6, 0], axes[6, 1]]:
            for value in 'top right left bottom'.split():
                axe.spines[value].set_visible(False)
            axe.set_xlabel('')
            axe.set_ylabel('')
        axes[6, 0].tick_params(left = False, right = False, labelleft = False, labelbottom = False, bottom = False)
        axes[6, 1].tick_params(left = False, right = False, labelleft = False, labelbottom = False, bottom = False)
        axes[6, 0].legend(frameon=False)
        axes[6, 1].legend(frameon=False)

        plt.tight_layout()
        return fig


