# StintAnalyzer - Project Overview

## Improvements

### Converter
- [ ] Validate the seperation in several stints

### Import
- [ ] Delete In-/Outlap
- [ ] verify the analyze button input 
- [ ] possibility to name a stint
- [ ] possibility to change a stint
- [ ] Delete Laps > 107% of fastest lap
- [ ] Delete Laps with min_speed < x
- [ ] verify the delete laps input

### Graphs
- [ ] Zoom when you click on a graph

### RACING LINE
- [ ] Implement overview of the racing line in a great figure

### Export
- [ ] Save data with deleted laps to disk

### ibtConverter
- [ ] check the required data type to save memory space
- [ ] test the stint divide feature

### index.html
- [ ] save the fonts Roboto local

### Plotly
- [ ] proof the new plotly symbols
- [ ] change the height of a figure if the window size change 
- [ ] change the horizontal spacing between figures according to the window width


### Additional Data out of .ibt-file

POTENTIAL DATA:
Alt (m) -> Track Profil Altitude / Track Map with up/down color / 3D Track Map
Brake (%) -> Brake Profile per Lap (Fastest / Mean / Slowest) / Difference to BrakeRaw?
EnterExitReset -> Understand the functionality (0 = enter / 1 = exit / 2 = reset) -> no added value compared to OnPitRoad
FogLevel (%) / Skies / WindDir / WindVel -> Weather data
LapBestLap -> Find the best lap of a session
LapBestLapTime -> Find the best lap time of a session
LapCurrentLapTime -> Relative to the fastest / average time
OilTemp / OilPressure / WaterTemp -> makes any sense?
ShiftIndicatorPct -> show the shifting points
SteeringWheelAngle / SteeringWheelPctTorque / SteeringWheelPctTorqueSign / SteeringWheelTorque -> unterstand steering
Velocity X Y Z -> Track Map
LFtempCM -> carcass temp after stop
LFwearM -> Tire Wear after stop?

EXAMINE FURTHER
LapDeltaToBestLap_OK / LapDeltaToOptimalLap_OK / LapDeltaToSessionBestLap_OK / LapDeltaToSessionLastlLap_OK / LapDeltaToSessionOptimalLap_OK -> find Laps with Offtrack?
Pitch / PitchRate -> Steigung of the track?
Roll / RollRate -> ???
PlayerCarPosition / PlayerCarClassPosition -> show race position
IsOnTrack !!! always true, doesn't work !!!
IsOnTrackCar !!! always true, doesn't work !!!
LatAccel
LongAccel / VertAccel
YAW