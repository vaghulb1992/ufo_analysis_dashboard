# UFO Analysis dashboard
# Author: Vaghul Aditya Balaji

import plotly.graph_objs as go
import pandas as pd
import emoji
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

#############################################################
# Data Input
#############################################################

df = pd.read_csv("https://raw.githubusercontent.com/vaghulb1992/ufo_analysis_dashboard/master/ufo_input_data.csv")

# converting the datatime column to pandas datetime
df.datetime = pd.to_datetime(df.datetime)

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

server = app.server

app.layout = html.Div([
    html.H2(emoji.emojize("UFO Spotting Guide :alien:")),

    dcc.Tabs(id = "tabs", children = [
        dcc.Tab(label = "Where and when can I see it?", children = [

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
                                         'backgroundColor': '#001580',
                                         'color': 'white'}),

        dcc.Tab(label = "How do people feel about it?", children = [

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
                             'backgroundColor': '#001580',
                             'color': 'white'}
        ),

        dcc.Tab(label = "How do I find out about it?", children = [

            dcc.Graph(id = "lat-long-plot"),

            dcc.Interval(id='interval-component',
                         interval = 1000 * 60 * 120,
                         n_intervals = 0),

            html.Div(id = "communication_div",
                     style = {'text-align': 'center', 'padding-top': '30px', 'font-size': '17px'}),

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
                                         'backgroundColor': '#001580',
                                         'color': 'white'})
    ], style = {'height': '44px', 'borderBottom': '1px solid #d6d6d6', 'fontWeight': 'bold'})
], style={'width': '100%', 'display': 'inline-block'})

#############################
# Dash callbacks
#############################

###########################
# Sentiment Analysis Tab
###########################

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
        title = f"Sentiment analysis of comments made on UFO sightings for {start_year}"
    else:
        title = f"Sentiment analysis of comments made on UFO sightings between {start_year} - {end_year}"

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

###########################
# Animation Tab
###########################

# we need this variable to be able to dynamically control the year that is part of the animation
MIN_YEAR = 1960
MAX_YEAR = 2014
cur_year = MIN_YEAR

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
    global cur_year
    cur_year = MIN_YEAR
    return 0

@app.callback(Output('year-chooser', 'value'),
              [Input('interval-component', 'n_intervals')])
def interval_year_callback(n_intervals):
    global cur_year

    if(n_intervals == 0):
        return MIN_YEAR

    if(cur_year == MAX_YEAR):
        return MAX_YEAR
    else:
        cur_year = cur_year + 1
        return cur_year

@app.callback(Output('communication_div', 'children'),
              [Input('year-chooser', 'value')])
def communication_text_callback(year_chosen):
    year = int(year_chosen)
    if(year <= 1990):
        return f"Main mode of communication: Letters/Telephones"
    elif(year > 1990 and year <= 2007):
        return f"Main mode of communication: Emails/Mobile Phones"
    else:
        return f"Main mode of communication: Twitter/Facebook/Smart Phones"

@app.callback(Output('lat-long-plot', 'figure'),
              [Input('year-chooser', 'value')])
def dot_map_callback(year_chosen):
    global cur_year
    cur_year = int(year_chosen)

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

###########################
# Spatial-Temporal Tab
###########################

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
                       marker = dict(color = ["#5DADE2" if month in (12, 1, 2) else
                                              "#1ABC9C" if month in (3, 4, 5) else
                                              "#F4D03F" if month in (6, 7, 8) else
                                              "#9C2706" for month in month_data.index]))
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

    scl = [[0.0, '#E7E625'], [0.1, '#E7E625'], [0.2, '#E79A25'], [0.3, '#E79A25'],
           [0.4, '#B80707'], [0.5, '#B80707'], [0.6, '#B80707'],
           [0.7, '#B80707'], [0.8, '#B80707'], [0.9, '#B80707'], [1.0, '#B80707']]

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
