from enum import Enum

# Define all constants for StintAnalyzer

# TODO possibility to use the config while fig.show(config = config)?
# config for plotly
config = dict(displaylogo=False, scrollZoom=True, modeBarButtonsToRemove=['zoomIn', 'zoomOut', 'resetScale'], modeBarButtonsToAdd=['drawline', 'drawopenpath', 'drawcircle', 'eraseshape'])

BASE_FONT_SIZE = 15
TITLE_SIZE = BASE_FONT_SIZE * 1.5
SUBPLOTS_TITLE_SIZE = BASE_FONT_SIZE * 1.1
ANNOTATION_FONT_SIZE = BASE_FONT_SIZE * 0.8
XAXIS_TITLE_SIZE = 14
XAXIS_TICK_SIZE = 12
YAXIS_TITLE_SIZE = 14
YAXIS_TICK_SIZE = 12
ANNOTATION_Y_SHIFT = -50
HORIZONTAL_SPACING = 0.05
VERTICAL_SPACING = 0.05
TRACK_MAP_SIZE = 16
TRACK_MAP_START_MARKER_SIZE = 20
MINREDUCEWIDTH = 400
SCALE_RATIO_Y = 1.0
SCALE_RATIO_Y2 = 1.0

class COLOR(str, Enum):
    RED = '#FD2826'
    BLUE = '#1E4488'
    ORANGE = '#FF6600'
    YELLOW = '#FFCC00'
    GREEN = '#33CC00'
    CYAN = '#00CCCC'
    GREY = '#676767'
    BLACK = '#000000'

class FIGURE_HEIGHT(dict, Enum):
    XL = dict(width=1400, height= 800)
    L = dict(width=1200, height= 700)
    M = dict(width=992, height= 600)
    S = dict(width=768, height= 500)
    XS = dict(width=576, height= 400)
    XXS = dict(width=576, height= 300)

class FIGURE_MARGIN(int, Enum):
    M = 140

class LINE_WIDTH(float, Enum):
    XL = 3.0
    L = 2.0
    M = 1.5
    S = 1.0
    XS = 0.5


LAYOUT_STANDARD = dict(autosize=True, separators=",.", minreducedwidth = MINREDUCEWIDTH, font_family = "'Roboto Condensed',sans-serif", title_font_size = TITLE_SIZE, font_color = COLOR.BLACK, modebar_remove = ['resetScale'], modebar_add = ['drawline', 'drawopenpath', 'drawcircle', 'drawrect', 'eraseshape'], template = 'plotly_white')