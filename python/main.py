# main file for the index.html


# region ----- IMPORTS -----
from StintAnalyzer import StintAnalyzer
from pyscript import display
from js import document, FileReader, window
from pyodide.ffi import create_proxy
import io
# endregion


# region ----- DEFINE FIELD CONSTANTS -----
# define field constants
OUTPUT_ID = 'output'
IMPORT_ID = 'import'
SESSION_DATA_DF1_ID = 'session_data_df1'
SESSION_DATA_DF2_ID = 'session_data_df2'
LAPS_DF1_ID = 'laps_df1'
LAPS_DF2_ID = 'laps_df2'
INP_DEL_LAPS_DF1 = 'inp_del_laps_df1'
INP_DEL_LAPS_DF2 = 'inp_del_laps_df2'
UPLOAD_1_ID = 'upload_1'
UPLOAD_2_ID = 'upload 2'
# define input fields
OUTPUT = document.getElementById(OUTPUT_ID)
IMPORT = document.getElementById(IMPORT_ID)
INP_DEL_LAPS_DF1 = document.getElementById(INP_DEL_LAPS_DF1)
INP_DEL_LAPS_DF2 = document.getElementById(INP_DEL_LAPS_DF2)
# endregion


# implement the object
sta = StintAnalyzer()


# region ---- IMPORT DATA FILES ----
def read_complete_1(event):
    process_1(event.target.result)

def read_complete_2(event):
    process_2(event.target.result)

async def process_file_1(x):
    fileList_1 = document.getElementById('upload_1').files

    for f in fileList_1:
        # reader is a pyodide.JSProxy
        reader = FileReader.new()
        # Create a Python proxy for the callback function
        onload_event = create_proxy(read_complete_1)
        #console.log("done")
        reader.onload = onload_event
        reader.readAsText(f)
    return

async def process_file_2(x):
    fileList_2 = document.getElementById('upload_2').files

    for f in fileList_2:
        # reader is a pyodide.JSProxy
        reader = FileReader.new()
        # Create a Python proxy for the callback function
        onload_event = create_proxy(read_complete_2)
        #console.log("done")
        reader.onload = onload_event
        reader.readAsText(f)
    return

def main():
    # Create a Python proxy for the callback function
    file_event_1 = create_proxy(process_file_1)
    file_event_2 = create_proxy(process_file_2)
    # Set the listener to the callback
    e1 = document.getElementById("upload_1")
    e1.addEventListener("change", file_event_1, False)
    e2 = document.getElementById("upload_2")
    e2.addEventListener("change", file_event_2, False)

def process_1(data):
    buffer = io.StringIO(data)
    sta.load_df1(buffer)

def process_2(data):
    buffer = io.StringIO(data)
    sta.load_df2(buffer)
# endregion


# region ----- DISPLAY SESSION AND LAP DATA -----
def display_session_data():
    # clear the session data output
    display("", target=SESSION_DATA_DF1_ID, append=False)
    display("", target=SESSION_DATA_DF2_ID, append=False)
    # returns a tuple of dicts for df1 and df2 containing 'session_data_key': session_data_value 
    sessiondata_df1, sessiondata_df2 = sta.get_sessiondata()
    # shows the keys and values
    for key in sessiondata_df1.keys():
        display(key + ': ' + sessiondata_df1[key], target=SESSION_DATA_DF1_ID, append=True)
    for key in sessiondata_df2.keys():
        display(key + ': ' + sessiondata_df2[key], target=SESSION_DATA_DF2_ID, append=True)

def display_lap_data():
    # shows the overview of the lap time data
    display(sta.get_laps_overview('df1'), target=LAPS_DF1_ID, append=False)
    display(sta.get_laps_overview('df2'), target=LAPS_DF2_ID, append=False)
# endregion


# region ------ DELETE LAPS -----
def del_laps_df1(e):
    # TODO validate 'input laps'
    sta.delete_laps_df1(INP_DEL_LAPS_DF1.value.split())
    INP_DEL_LAPS_DF1.value = ''
    display_lap_data()
    # display(sta.get_laps_overview('df1'), target=LAPS_DF1_ID, append=False)


def del_laps_df2(e):
    # TODO validate 'input laps'
    sta.delete_laps_df2(INP_DEL_LAPS_DF2.value.split())
    INP_DEL_LAPS_DF2.value = ''
    display_lap_data()
    # display(sta.get_laps_overview('df2'), target=LAPS_DF2_ID, append=False)
# endregion

def analyze_data(e):
    sta.setup_stintanalyzer()
    display_session_data()
    display_lap_data()


# region ----- CALLBACK FOR SELECTION ------
def laptime(e):
    hide_import()
    show_output()
    fig = sta.get_laptime_graph()
    display(fig, target=OUTPUT_ID, append=False)

def speed(e):
    hide_import()
    show_output()
    display(sta.get_speed_per_lap(window.innerWidth), target=OUTPUT_ID, append=False)
    display(sta.get_speed_comparision(window.innerWidth), target=OUTPUT_ID, append=True)
    display(sta.get_speed_track_map(window.innerWidth), target=OUTPUT_ID, append=True)
    figures = sta.get_constancy_comparision(window.innerWidth)       
    display(figures[0], target=OUTPUT_ID, append=True)
    display(figures[1], target=OUTPUT_ID, append=True)

def computer_performance(e):
    hide_import()
    show_output()
    fig = sta.get_computer_performance_graph()
    display(fig, target=OUTPUT_ID, append=False)

def general_conditions(e):
    hide_import()
    show_output()
    fig = sta.get_general_conditions_graph()
    display(fig, target=OUTPUT_ID, append=False)

def car_setup(e):
    hide_import()
    show_output()
    fig = sta.get_car_setup_graph()
    display(fig, target=OUTPUT_ID, append=False)

def fuel(e):
    hide_import()
    show_output()
    fig = sta.get_fuel_graph()
    display(fig, target=OUTPUT_ID, append=False)    

def tyre_pressure(e):
    hide_import()
    show_output()
    fig = sta.get_tyre_pressure_graph()
    display(fig, target=OUTPUT_ID, append=False)

def tyre_temp(e):
    hide_import()
    show_output()
    fig = sta.get_tyre_temperature_graph()
    display(fig, target=OUTPUT_ID, append=False)

def ride_height(e):
    hide_import()
    show_output()
    fig = sta.get_ride_height_graph()
    display(fig, target=OUTPUT_ID, append=False)

def brake(e):
    hide_import()
    show_output()
    fig = sta.get_brake_graph()
    display(fig, target=OUTPUT_ID, append=False)

def throttle(e):
    hide_import()
    show_output()
    fig = sta.get_throttle_graph()
    display(fig, target=OUTPUT_ID, append=False)

def how_to(e):
    hide_import()
    show_output()
    display("'How to follows soon'", target=OUTPUT_ID, append=False)

def import_stint(e):
    hide_output()
    show_import()
# endregion


# region ------ DEMO DATA ------
def analyze_demo_data(e):
    sta.load_df1("stint1.csv")
    sta.load_df2("stint2.csv")
    sta.setup_stintanalyzer()
    sta.delete_laps_df1([1, 19, 20])
    sta.delete_laps_df2([1, 2, 19])
    display_session_data()
    display_lap_data()
# endregion
    

# region ----- HELPER FUNCTIONS ------
def show_import():
    IMPORT.style.display = "block";

def hide_import():
    IMPORT.style.display = "none";

def show_output():
    OUTPUT.style.display = "block";

def hide_output():
    OUTPUT.style.display = "none";
# endregion


# main()

# call if you want to start already with the demo data
analyze_demo_data(0)
