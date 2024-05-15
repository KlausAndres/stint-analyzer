import pandas as pd
import plotly.graph_objects as go

file_name : str = str(input("Please enter the filename -> "))

df = pd.read_csv(file_name)

print(df.Lap.unique())

act_lap : int = int(input("Which lap should be drawn? -> "))

df_lap = df[df.Lap == act_lap]
height = 1000

session_keys = df.SessionData[0].split('*')
session_values = df.SessionData[1].split('*')

session_data = {}

for index in range(len(session_keys)):
    session_data[session_keys[index]] = session_values[index]

print(session_data)


fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df_lap.Lon,
    y=df_lap.Lat,
    mode='markers',
    marker = dict(size=12, color='blue', showscale=False),
    name='',
    showlegend=False,
    customdata=df_lap.LapDistPct.round(1),
    hovertemplate="LapDistPct:%{customdata}"
))

fig.add_trace(go.Scatter(
    x=[df_lap.iloc[0].Lon],
    y=[df_lap.iloc[0].Lat],
    mode = 'markers',
    marker = dict(size=20, color='red'),
    name = 'Start/Finish Line',
    showlegend = True,
    visible = True,
    hovertemplate="Start/Finish Line"))

fig.update_layout(
    title = session_data['TrackName'],
    autosize = True,
    height = height, 
    hovermode='closest',  
    template = 'plotly_white',
    xaxis=dict(scaleanchor='y', scaleratio=1.0)) 

fig.update_yaxes(
    visible = False)

fig.update_xaxes(
    visible = False)

fig.show()

input()