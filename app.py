import pandas as pd
import numpy as np
import plotly.graph_objs as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State, MATCH
from datetime import datetime, timedelta
from scipy.interpolate import interp1d
from figures import *

# -------------------------------- DATA PREP -------------------------------- #

def make_long(df):
    # Pivoting the DataFrame from wide to long format
    dflong = df.melt(id_vars=['AVIBASEID', 'yr_db'],
                     var_name='week',
                     value_name='count')
    # Removing the 'Week-' prefix and converting the 'week' column to numeric
    dflong['week'] = dflong['week'].str.replace('Week-', '').astype(int)
    return dflong


# Bird id's:
birdids_df = pd.read_csv("data/birdids.csv")
birdids = birdids_df['x'].tolist()

#skip these bird ids:
skipid = ["0B1B2EB6", "77567086", "930E8874", "115F04DD", "B12B8816", "9BEECB7E"] #["Fox Sparrow", "Selasphorus sp.", "Ridgway's Rail (obsoletus)","green-winged teal", "western flycatcher", "american coot"]

# Bird dictionary:
bird_dict = pd.read_pickle("data/name_aviD_dict_22.pickle")

# Raw data:
ebird19rel = pd.read_csv("data/raw/ebird19rel_raw.csv")
ebird22rel = pd.read_csv("data/raw/ebird22rel_raw.csv")
inat19rel = pd.read_csv("data/raw/inat19rel_raw.csv")
inat22rel = pd.read_csv("data/raw/inat22rel_raw.csv")

# Smoothed data:
ebird19rel_smoothed = pd.read_csv("data/smoothed/ebird19rel_fsmoothed.csv")
ebird22rel_smoothed = pd.read_csv("data/smoothed/ebird22rel_fsmoothed.csv")
inat19rel_smoothed = pd.read_csv("data/smoothed/inat19rel_fsmoothed.csv")
inat22rel_smoothed = pd.read_csv("data/smoothed/inat22rel_fsmoothed.csv")

# Transforming data to long format
ebird19rel_long = make_long(ebird19rel)
ebird22rel_long = make_long(ebird22rel)
inat19rel_long = make_long(inat19rel)
inat22rel_long = make_long(inat22rel)

ebird19rel_smoothed_long = make_long(ebird19rel_smoothed)
ebird22rel_smoothed_long = make_long(ebird22rel_smoothed)
inat19rel_smoothed_long = make_long(inat19rel_smoothed)
inat22rel_smoothed_long = make_long(inat22rel_smoothed)

# Combining all long format data into one DataFrame
allbirdsrel_long = pd.concat([ebird19rel_long,
                              ebird22rel_long,
                              inat19rel_long,
                              inat22rel_long],
                             ignore_index=True)

allbirdsrel_smoothed_long = pd.concat([ebird19rel_smoothed_long,
                                       ebird22rel_smoothed_long,
                                       inat19rel_smoothed_long,
                                       inat22rel_smoothed_long],
                                      ignore_index=True)


# ----------------------------------- APP ----------------------------------- #
app = Dash(__name__)
server = app.server
app.title = "Bird Dash"  # Tab Name


def create_bird_controls():
    """
    Creates a set of controls for selecting and configuring visualizations
    in side-by-side plot.

    Returns:
        html.Div: A Div containing the following controls:
            - Dropdown for selecting a bird from a sorted list of bird IDs and names.
            - RadioItems for selecting the type of data to display (smooth or raw).
            - RadioItems for selecting the scale type (fixed or relative).
            - Checklist for selecting which database years to include in the visualization.
    """
    # Only include birds w/ data in drop down
    bird_dict_data = {}
    for b_id in bird_dict.keys():
        if b_id in skipid:
            pass
        elif b_id in allbirdsrel_long['AVIBASEID'].unique():
            bird_dict_data[b_id] = bird_dict[b_id]
    sorted_bird_ids = sorted(bird_dict_data.items(), key=lambda item: item[1])
    
    return html.Div([
        dcc.Dropdown(
            id='bird-dropdown',
            options=[{'label': bird_name, 'value': bird_id} for bird_id, bird_name in sorted_bird_ids],
            value=sorted_bird_ids[0][0] if sorted_bird_ids else None
        ),
        dcc.RadioItems(
            id='data-type-radio',
            options=[
                {'label': 'Smooth Data', 'value': 'smooth'},
                {'label': 'Raw Data', 'value': 'raw'}
            ],
            value='smooth',
            inline=True
        ),
        dcc.RadioItems(
            id='scale-type-radio',
            options=[
                {'label': 'Fix Scale', 'value': 'fixed'},
                {'label': 'Relative Scale', 'value': 'relative'}
            ],
            value='relative',
            inline=True
        ),
        dcc.Checklist(
            id='database-year-checklist',
            options=[
                {'label': 'eBird 2019', 'value': 'ebird19'},
                {'label': 'eBird 2022', 'value': 'ebird22'},
                {'label': 'iNat 2019', 'value': 'inat19'},
                {'label': 'iNat 2022', 'value': 'inat22'}
            ],
            value=['ebird19', 'ebird22', 'inat19', 'inat22'],  # Default: all selected
            inline=True
        )
    ])


def create_comparison_controls():
    """
    Creates a set of controls for selecting and configuring visualizations
    in multiple comparison plot.

    Returns:
        html.Div: A Div containing the following controls:
            - Dropdown for selecting multiple birds from a sorted list of bird IDs and names.
            - RadioItems for selecting the plot type (rectangular or circular).
            - RadioItems for selecting the type of data to display (smooth or raw).
            - RadioItems for selecting the scale type (fixed or relative).
            - Checklist for selecting which database years to include in the visualization.
            - Div for displaying the comparison plots.
    """
    # Only include birds w/ data in drop down
    bird_dict_data = {}
    for b_id in bird_dict.keys():
        if b_id in skipid:
            pass
        elif b_id in allbirdsrel_long['AVIBASEID'].unique():
            bird_dict_data[b_id] = bird_dict[b_id]  
    sorted_bird_ids = sorted(bird_dict_data.items(), key=lambda item: item[1])

    return html.Div([
        dcc.Dropdown(
            id='multi-bird-dropdown',
            options=[{'label': bird_name, 'value': bird_id} for bird_id, bird_name in sorted_bird_ids],
            value=[],
            multi=True
        ),
        dcc.RadioItems(
            id='plot-type-radio',
            options=[
                {'label': 'Rectangular Plot', 'value': 'rectangular'},
                {'label': 'Circular Plot', 'value': 'circular'}
            ],
            value='rectangular',
            inline=True
        ),
        dcc.RadioItems(
            id='data-type-radio-multi',
            options=[
                {'label': 'Smooth Data', 'value': 'smooth'},
                {'label': 'Raw Data', 'value': 'raw'}
            ],
            value='smooth',
            inline=True
        ),
        dcc.RadioItems(
            id='scale-type-radio-multi',
            options=[
                {'label': 'Fix Scale', 'value': 'fixed'},
                {'label': 'Relative Scale', 'value': 'relative'}
            ],
            value='relative',
            inline=True
        ),
        dcc.Checklist(
            id='database-year-checklist-multi',
            options=[
                {'label': 'eBird 2019', 'value': 'ebird19'},
                {'label': 'eBird 2022', 'value': 'ebird22'},
                {'label': 'iNat 2019', 'value': 'inat19'},
                {'label': 'iNat 2022', 'value': 'inat22'}
            ],
            value=['ebird19', 'ebird22', 'inat19', 'inat22'],  # Default: all selected
            inline=True
        ),
        html.Div(id='comparison-plot-container')
    ])


# App layout
app.layout = html.Div([
    # Title
    html.Div(children='NorCal Bird Dashboard',
             style={'fontSize': 50, 'fontWeight': 'bold'}),
     
    html.Br(),  # Line Break

    # About section
    html.Div(children='''
        Welcome to the NorCal Bird Dashboard, an interactive tool for visualizing bird population trends.
        This dashboard allows you to explore data for 260 bird species with ease. Enhance your analysis by:
    '''),
    html.Ul([
        html.Li([
            html.B('Data Type: '),
            'Choose between raw data for precise readings or smoothed data for trend analysis.'
        ], style={'margin-bottom': '5px'}),
        html.Li([
            html.B('Scale Options: '),
            'Opt for a fixed scale to compare all birds uniformly or a relative scale to focus on individual species.'
        ], style={'margin-bottom': '5px'}),
        html.Li([
            html.B('Filtering: '),
            'Refine your view by selecting specific databases and customizing the time range to suit your needs.'
        ], style={'margin-bottom': '5px'}),
        html.Li([
            html.B('Theoretical Baseline: '),
            'The dashed gray line on the graphs represents the relative frequency of a theoretical bird whose prevalence is uniform over the entire year.'
        ], style={'margin-bottom': '5px'})
    ]),

    html.Br(),  # Line Break
    html.Div(children='''
    To cite this app, use the following citation:
    C. Carroll and S. Waterman. "NorCal Bird Dashboard." 2024. https://birds-dash-547zxcr6ea-uc.a.run.app/
    '''),

    html.Br(),  # Line Break
    html.Br(),

    html.Div([
        html.H2('Bird Seasonality Pattern', style={'textAlign': 'left', 'fontWeight': 'bold'}),
        create_bird_controls(),
        html.Div(id='plot-container')
    ], style={'backgroundColor': '#f1f8f9', 'padding': '10px', 'border': '2px solid #2a5f6d'}),

    html.Br(),  # Line Break
    html.Br(),

    html.Div([
        html.H2('Compare Multiple Birds', style={'textAlign': 'left', 'fontWeight': 'bold'}),
        create_comparison_controls()
    ], style={'backgroundColor': '#f1f8f9', 'padding': '10px', 'border': '2px solid #2a5f6d'})
])

@app.callback(
    Output('plot-container', 'children'),
    Input('bird-dropdown', 'value'),
    Input('data-type-radio', 'value'),
    Input('scale-type-radio', 'value'),
    Input('database-year-checklist', 'value')
)
def update_bird_plot(bird_id, data_type, scale_type, selected_databases):
    """
    Updates the side-by-side bird plot based on user selections.
    """
    birds_df = allbirdsrel_smoothed_long if data_type == 'smooth' else allbirdsrel_long
    birds_df = birds_df[birds_df['yr_db'].isin(selected_databases)]
    fig_rect_polar = create_sidebysideplot(bird_dict, birds_df, bird_id, scale_type)
    return html.Div([
        html.Div(dcc.Graph(figure=fig_rect_polar, 
                           config={"toImageButtonOptions": {"width": 1500, "height": 500, "scale": 2, "filename": 'bird_szn_figure'}}))
    ], style={'textAlign': 'center', 'backgroundColor': 'white', 'padding': '10px', 'border': '1px solid lightgrey'})

@app.callback(
    Output('comparison-plot-container', 'children'),
    Input('multi-bird-dropdown', 'value'),
    Input('plot-type-radio', 'value'),
    Input('data-type-radio-multi', 'value'),
    Input('scale-type-radio-multi', 'value'),
    Input('database-year-checklist-multi', 'value')
)
def update_comparison_plot(bird_ids, plot_type, data_type, scale_type, selected_databases):
    """
    Updates the comparison bird plot based on user selections.
    """
    if not bird_ids:
        return html.Div("No birds selected")

    birds_df = allbirdsrel_smoothed_long if data_type == 'smooth' else allbirdsrel_long
    birds_df = birds_df[birds_df['yr_db'].isin(selected_databases) & birds_df['AVIBASEID'].isin(bird_ids) & ~birds_df['AVIBASEID'].isin(skipid)]

    # Calculate the maximum y-value for relative scaling
    max_y_value = birds_df['count'].max() * 1.1 if scale_type == 'relative' else None

    plots = []
    for bird_id in bird_ids:
        if plot_type == 'rectangular':
            fig = rectangular_plot(bird_dict, birds_df, [bird_id], scale_type, max_y_value)
        else:
            fig = circular_plot(bird_dict, birds_df, [bird_id], scale_type, max_y_value)
        
        plots.append(dcc.Graph(figure=fig, 
                               config={"toImageButtonOptions": {"width": 750, "height": 600, "scale": 3, "filename": 'bird_szn_figure2'}},
                               style={'display': 'inline-block', 'width': '45%', 'margin': '10px', 'border': '1px solid lightgrey'}))

    return html.Div(plots, style={'textAlign': 'center'})


if __name__ == '__main__':
    app.run_server(debug=True)
