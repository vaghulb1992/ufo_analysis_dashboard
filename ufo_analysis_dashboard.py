# UFO Analysis dashboard
# Author: Vaghul Aditya Balaji

from textblob import TextBlob
import plotly.graph_objs as go
import pandas as pd

#############################################################
# DATA CLEANUP
#############################################################

df = pd.read_csv("ufo_data.csv", low_memory = False)s

# first, let's drop some of the columns we won't be using in the visualizations
df.drop(columns = ['duration (seconds)', 'duration (hours/min)', 'date posted', 'shape'], inplace = True)

# since our analysis is only restricted to North America, let's filter our data first
df = df[(df['country'] == 'us') | (df['country'] == 'ca')]

# capitalizing the names of cities
df.city = df.city.apply(str.capitalize)

# let's drop all the rows where the state is NaN
df.dropna(subset = ['state'], axis = 0, inplace = True)

# let's convert the datetime column to the appropriate type
df['datetime'] = pd.to_datetime(df['datetime'], errors = "coerce")

# now, let's drop all the rows where the datetime field is NaT and sort data by datetime
df.dropna(subset = ['datetime'], axis = 0, inplace = True)
df.sort_values(by = 'datetime', inplace = True)

# let's convert the latitude column to float64
df.latitude = df.latitude.astype(float)

# removing the space in the longitude column
df.rename(columns = {'longitude ': 'longitude'}, inplace = True)

# finally, we'd want to restrict our data to recent times (so we will stick to the last 60 years)
df = df[df.datetime.dt.year >= 1960]

# let's perform sentiment analysis on the comments field
def get_sentiment_polarity(x):
    return TextBlob(x).polarity

df['sentiment-polarity'] = df.comments.astype(str).apply(get_sentiment_polarity)

# let's drop the comments field as we don't need it anymore
df.drop(columns = ['comments'], inplace = True)

#############################################################
# DATA VISUALIZATIONS
#############################################################

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

#############################
# Data Preparation
#############################

province_list = list(map(str.upper, df.groupby('state').size().index.tolist()))

province_dict_list = []
province_dict_list.append(dict(label = "All provinces", value = "All provinces"))
for province in province_list:
    prov_dict = dict(label = province, value = province)
    province_dict_list.append(prov_dict)

sentiment_location_list = []
sentiment_location_list.append(dict(label = "USA", value = "us"))
sentiment_location_list.append(dict(label = "Canada", value = "ca"))
for province in province_list:
    prov_dict = dict(label = province, value = province)
    sentiment_location_list.append(prov_dict)

#############################
# Dash Layout
#############################

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

app.title = "UFO Sightings Analysis"

app.layout = html.Div([
    html.Hr(),

    dcc.Tabs(id = "tabs", children = [
        dcc.Tab(label = "Sentiment Analysis", children = [

            dcc.Graph(id = "sentiment-plot"),

            html.Section([
                html.Div(["Year", dcc.RangeSlider(id = 'sentiment-year-chooser',
                                                  min = 1960,
                                                  max = df.datetime.dt.year.max(),
                                                  value = [1976, 2014],
                                                  marks = {str(year): str(year) for year in df.datetime.dt.year.unique()[::4]}
                                                  )
                          ], style={'width': '96.75%', 'float': 'right', 'display': 'inline-block', 'padding': 30, 'padding-bottom': '35px'}),

                html.Div(["Select a country/province",
                          dcc.Dropdown(id = 'location-dropdown',
                                       options = sentiment_location_list,
                                       value = 'ca',
                                       clearable = False
                                       )
                          ], style={'width': '20%', 'display': 'inline-block', 'padding-left': '10px', 'padding-bottom': '10px'})
                          ], style={'background-color':'#F9F9F9', 'border-radius': '15px'})
        ], selected_style = {'borderTop': '1px solid #d6d6d6',
                             'borderBottom': '1px solid #d6d6d6',
                             'backgroundColor': '#119DFF',
                             'color': 'white'}
        ),

        dcc.Tab(label = "Latitude-Longitude Info", children = [

            dcc.Graph(id = "lat-long-plot"),

            dcc.Interval(id='interval-component',
                         interval = 1000 * 60 * 120,
                         n_intervals = 0),

            html.Section([
                    html.Div(["Year",
                              dcc.Slider(id = 'year-chooser',
                                         min = 1960,
                                         max = df.datetime.dt.year.max(),
                                         value = 1960,
                                         marks = {str(year): str(year) for year in df.datetime.dt.year.unique()[::4]}
                                         )
                              ], style={'width': '96.75%', 'float': 'right', 'display': 'inline-block', 'padding': 30, 'padding-bottom': '35px'}),


                    html.Button('Reset', id='reset', style = {'background-color': '#E33F06', 'color': 'white', 'padding-bottom': '35px'}),

                    html.Button('Play/Pause', id = 'play-pause', style = {'background-color': '#E3F106', 'color': 'black', 'padding-bottom': '35px'})

                        ], style={'background-color':'#F9F9F9', 'border-radius': '15px'})
                    ], selected_style = {'borderTop': '1px solid #d6d6d6',
                                         'borderBottom': '1px solid #d6d6d6',
                                         'backgroundColor': '#119DFF',
                                         'color': 'white'}),

        dcc.Tab(label = "Spatial and Temporal Info", children = [

            html.B([html.H5('Spatial and Temporal Distributions of UFO sightings')]),

            html.Div([
                    html.Div(id = "choropleth-div", children = [
                            dcc.Graph(id = 'choropleth-map')
                    ], style={'width': '50%', 'float': 'left', 'display': 'inline-block'}),

                    html.Div(id = "line-div", children = [
                            dcc.Graph(id = 'line-graph')
                    ], style={'width': '50%', 'float': 'left', 'display': 'inline-block'}),

                    html.Div([dcc.Graph(id = 'bar-plot')
                             ], style={'width': '50%', 'float': 'right', 'display': 'inline-block'})
                    ]),
            html.Section([
                    html.Div(["Year Range",
                              dcc.RangeSlider(id = 'year-slider',
                                              min = df.datetime.dt.year.min(),
                                              max = df.datetime.dt.year.max(),
                                              value = [1976, 2014],
                                              marks = {str(year): str(year) for year in df.datetime.dt.year.unique()[::4]}
                                              )
                              ], style={'width': '96.75%', 'float': 'right', 'display': 'inline-block', 'padding': 30, 'padding-bottom': '35px'}),

                    html.Div(["Select a province",
                              dcc.Dropdown(id = 'province-dropdown',
                                           options=province_dict_list,
                                           value='All provinces',
                                           clearable=False)
                              ], style={'width': '20%', 'display': 'inline-block', 'padding-left': '10px', 'padding-bottom': '10px'})
                        ], style={'background-color':'#F9F9F9', 'border-radius': '15px'})
                    ], selected_style = {'borderTop': '1px solid #d6d6d6',
                                         'borderBottom': '1px solid #d6d6d6',
                                         'backgroundColor': '#119DFF',
                                         'color': 'white'})
    ], style = {'height': '44px', 'borderBottom': '1px solid #d6d6d6', 'fontWeight': 'bold'})
], style={'width': '100%', 'display': 'inline-block'})

#############################
# Dash callbacks
#############################

##################
# First tab
##################

@app.callback(Output('sentiment-plot', 'figure'),
              [Input('sentiment-year-chooser', 'value'), Input('location-dropdown', 'value')])
def sentiment_line_callback(slider_value, location_name):
    start_year = int(slider_value[0])
    end_year = int(slider_value[1])
    subset_df = df[(df.datetime.dt.year >= start_year) & (df.datetime.dt.year <= end_year)]
    if(location_name == "ca" or location_name == "us"):
        subset_df = subset_df[subset_df.country == location_name]
    else:
        subset_df = subset_df[subset_df.state == location_name.lower()]

    # let's group our data by day
    subset_df = subset_df.groupby(subset_df.datetime.dt.date)['sentiment-polarity'].mean()

    # let's further breakdown our data into positive and negative sentiments
    positive_subset = subset_df[subset_df >= 0]
    negative_subset = subset_df[subset_df < 0]

    positive_line = go.Scatter(x = positive_subset.index,
                               y = positive_subset,
                               hoverinfo = 'x + y',
                               name = "Positive Sentiment",
                               marker = dict(color = "#30C303"))

    negative_line = go.Scatter(x = negative_subset.index,
                               y = negative_subset,
                               hoverinfo = 'x + y',
                               name = "Negative Sentiment",
                               marker = dict(color = "#F75600"))

    traces = [positive_line, negative_line]

    if(start_year == end_year):
        title = f"UFO comments sentiment analysis for {start_year}"
    else:
        title = f"UFO comments sentiment analysis between {start_year} - {end_year}"

    if(location_name == "ca"):
        title = title + " in Canada"
    elif(location_name == "us"):
        title = title + " in USA"
    else:
        title = title + f" in {location_name}"

    layout = go.Layout(title = title,
                       showlegend = True,
                       xaxis = dict(title = "Time"),
                       yaxis = dict(title = "Sentiment Polarity"))

    return dict(data = traces, layout = layout)

##################
# Second tab
##################

@app.callback(Output('interval-component', 'interval'),
              [Input('play-pause', 'n_clicks')])
def animation_play_pause_callback(n_clicks):
    if(n_clicks % 2 == 0):
        return 1000 * 60 * 120 # 2 hours - this is a hacky pause
    else:
        return 400

@app.callback(Output('play-pause', 'style'),
              [Input('play-pause', 'n_clicks')])
def animation_play_pause_color_callback(n_clicks):
    if(n_clicks % 2 == 0):
        return {'background-color': '#E3F106', 'color': 'black', 'padding-bottom': '35px'}
    else:
        return {'background-color': '#5CF106', 'color': 'black', 'padding-bottom': '35px'}

@app.callback(Output('interval-component', 'n_intervals'),
              [Input('reset', 'n_clicks')])
def animation_reset_callback(n_clicks):
    return 0

@app.callback(Output('year-chooser', 'value'),
              [Input('interval-component', 'n_intervals')])
def interval_year_callback(n_intervals):
    year_delta = n_intervals % 55
    return (1960 + year_delta)

@app.callback(Output('lat-long-plot', 'figure'),
              [Input('year-chooser', 'value')])
def dot_map_callback(year_chosen):
    # make figure
    figure = {'data': [], 'layout': {}}

    figure['layout']['geo'] = dict(showframe = False,
                                   showland = True,
                                   showcoastlines = True,
                                   showcountries = True,
                                   countrywidth = 1,
                                   landcolor = '#F4F4F4',
                                   subunitwidth = 1,
                                   showlakes = False,
                                   scope = 'north america',
                                   projection = dict(type = 'equirectangular'),
                                   countrycolor = "#BBBBBB")

    # make data
    df_by_year = df[df.datetime.dt.year == year_chosen]
    data_dict = dict(type = 'scattergeo',
                     lon = df_by_year['longitude'],
                     lat = df_by_year['latitude'],
                     hoverinfo = 'text',
                     text = "City: " + df_by_year['city'] + '<br>' +\
                            "State: " + df_by_year['state'].apply(str.upper) + '<br>' +\
                            "Latitude: " + df_by_year['latitude'].astype(str) + '<br>' +\
                            "Longitude: " + df_by_year['longitude'].astype(str),
                     mode = 'markers',
                     marker = dict(size = 4,
                                   color = "red",
                                   opacity = 0.4))
    figure['data'].append(data_dict)

    figure["layout"]["autosize"] = True
    figure["layout"]["margin"] = go.layout.Margin(l = 5, r = 5, b = 0, t = 100, pad = 0)
    figure["layout"]["title"] = f"UFO sightings in North America in {year_chosen}"

    return figure

##################
# Third tab
##################

@app.callback(Output('choropleth-div', 'style'),
              [Input('province-dropdown', 'value')])
def choropleth_toggle_callback(province_name):
    if(province_name != "All provinces"):
        return {'display': 'none', 'width': '50%', 'float': 'left'}
    else:
        return {'display': 'inline-block', 'width': '50%', 'float': 'left'}

@app.callback(Output('line-div', 'style'),
              [Input('province-dropdown', 'value')])
def line_toggle_callback(province_name):
    if(province_name == "All provinces"):
        return {'display': 'none', 'width': '50%', 'float': 'left'}
    else:
        return {'display': 'inline-block', 'width': '50%', 'float': 'left'}

@app.callback(Output('line-graph', 'figure'),
              [Input('year-slider', 'value'), Input('province-dropdown', 'value')])
def line_callback(slider_value, province_name):
    start_year = int(slider_value[0])
    end_year = int(slider_value[1])
    subset_df = df[(df.datetime.dt.year >= start_year) & (df.datetime.dt.year <= end_year)]
    if(province_name != "All provinces"):
        subset_df = subset_df[subset_df.state == province_name.lower()]

    # let's group our data to see how the sightings vary by year
    year_data = subset_df.groupby(subset_df.datetime.dt.year).size()
    line_trace = go.Scatter(x = year_data.index,
                            y = year_data,
                            name = "UFO sightings by year",
                            marker = dict(color = "#C54646", symbol = 'x'))
    traces = [line_trace]
    if(start_year == end_year):
        title = f"UFO sightings in {start_year}"
    else:
        title = f"UFO sightings between {start_year} - {end_year}"

    if(province_name != "All provinces"):
        title = title + f" in {province_name}"

    layout = go.Layout(title = title,
                       xaxis = dict(title = "Year"),
                       yaxis = dict(title = "Count"))

    return dict(data = traces, layout = layout)

@app.callback(Output('bar-plot', 'figure'),
              [Input('year-slider', 'value'), Input('province-dropdown', 'value')])
def barplot_callback(slider_value, province_name):
    start_year = int(slider_value[0])
    end_year = int(slider_value[1])
    subset_df = df[(df.datetime.dt.year >= start_year) & (df.datetime.dt.year <= end_year)]
    if(province_name != "All provinces"):
        subset_df = subset_df[subset_df.state == province_name.lower()]
    else:
        subset_df = subset_df[subset_df.country == 'us']

    # let's group our data to see how the sightings vary by month
    month_data = subset_df.groupby(subset_df.datetime.dt.month).size()
    bar_trace = go.Bar(x = month_data.index,
                       y = month_data,
                       name = "UFO sightings by month",
                       marker = dict(color = "#F4D03F"))

    traces = [bar_trace]
    if(start_year == end_year):
        title = f"UFO sightings by month in {start_year}"
    else:
        title = f"UFO sightings by month between {start_year} - {end_year}"

    if(province_name != "All provinces"):
        title = title + f" in {province_name}"

    layout = go.Layout(title = title,
                       xaxis = dict(title = "Month",
                                    tickmode = "array",
                                    tickvals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                                    ticktext = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
                       yaxis = dict(title = "Count"))

    return dict(data = traces, layout = layout)

@app.callback(Output('choropleth-map', 'figure'),
             [Input('year-slider', 'value')])
def choropleth_callback(slider_value):
    start_year = int(slider_value[0])
    end_year = int(slider_value[1])
    subset_df = df[(df.datetime.dt.year >= start_year) & (df.datetime.dt.year <= end_year)]

    scl = [[0.0, 'rgb(165,0,38)'], [0.1111111111111111, 'rgb(215,48,39)'], [0.2222222222222222, 'rgb(244,109,67)'], [0.3333333333333333, 'rgb(253,174,97)'], [0.4444444444444444, 'rgb(254,224,144)'], [0.5555555555555556, 'rgb(224,243,248)'], [0.6666666666666666, 'rgb(171,217,233)'], [0.7777777777777778, 'rgb(116,173,209)'], [0.8888888888888888, 'rgb(69,117,180)'], [1.0, 'rgb(49,54,149)']]

    data = [dict(type='choropleth',
                 colorscale = scl,
                 autocolorscale = False,
                 locations = list(map(str.upper, subset_df.groupby('state').size().index.tolist())),
                 z = subset_df.groupby('state').size(),
                 locationmode = 'USA-states',
                 marker = dict(line = dict(color = 'rgb(255,255,255)',
                                           width = 2)),
                 colorbar = dict(title = "No. of sightings"))]

    if(start_year == end_year):
        title = f"UFO sightings by state in {start_year}"
    else:
        title = f"UFO sightings by state between {start_year} - {end_year}"
    layout = dict(title = title,
                  geo = dict(scope = 'usa',
                             projection = dict( type='albers usa' ),
                             showlakes = False))

    return dict(data = data, layout = layout)

#############################
# Launching the server
#############################

if __name__ == '__main__':
    app.run_server(debug=True)

#############################################################
#############################################################
