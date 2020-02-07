import psycopg2
import csv
import plotly
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import numpy as np
import pandas as pd
import pandasql as ps
from dash.dependencies import Input, Output
from pandas.api.types import CategoricalDtype

con = psycopg2.connect(
			host = "db1.cakrcx1k6r20.us-west-2.rds.amazonaws.com",
			database = "postgres",
			user = "postgres",
			password = "postgres")

cur = con.cursor()

def df_query(col):
	query = "SELECT " + col + ", SUM(count) AS counts FROM df GROUP BY " + col
	return query

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

external_stylesheets = ['https://codepen.io/anon/pen/mardKv.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.config['suppress_callback_exceptions']=True

app.layout = html.Div([
    html.H1('Safety Butler for Travelers',style={'text-align': 'center'}),

    html.Label('Choose a City'),
    html.Br(),

    dcc.Dropdown(
    	id = 'first-dropdown',
        options = [
        {'label': 'Austin', 'value': 'Austin', 'disabled': True},
        {'label': 'Baltimore', 'value': 'Baltimore', 'disabled': True},
        {'label': 'Boston', 'value': 'Boston', 'disabled': True},
        {'label': 'Baton Rouge', 'value': 'BR', 'disabled': True},
        {'label': 'Chicago', 'value': 'Chicago', 'disabled': True},
        {'label': 'Dallas', 'value': 'Dallas', 'disabled': True},
        {'label': 'Los Angeles', 'value': 'LA', 'disabled': True},
        {'label': 'New York', 'value': 'NY', 'disabled': True},
        {'label': 'Orlando', 'value': 'Orlando', 'disabled': True},
        {'label': 'Philladelphia', 'value': 'Philladelphia', 'disabled': True},
        {'label': 'Seattle', 'value': 'Seattle', 'disabled': True},
        {'label': 'San Francisco', 'value': 'SF'},
        {'label': 'St.Louis', 'value': 'SL', 'disabled': True}
        ],
        placeholder = 'Select a City'
        ),


    dcc.Tabs(id="tabs-navigation", value='graph-collection', children=[
        dcc.Tab(label='General Info', value='general-info'),
        dcc.Tab(label='Visualize on Map', value='map'),
        dcc.Tab(label='Prediction', value='prediction'),
    ]),
    html.Div(id='graphs')
])

#These are the main and secondary pages in tab 1 and 2
@app.callback(Output('graphs', 'children'),
	[Input('tabs-navigation', 'value'),
	Input('first-dropdown', 'value')])

def update_graph(tab, dropdown):
	city = '"' + str(dropdown) + '"'
	# if dropdown == '"None"':
	# 	return
	df = pd.read_sql("SELECT * FROM " + city, con)
	df_Districts = ps.sqldf(df_query("district"),locals()).sort_values(by=['counts'])
	df_Day = ps.sqldf(df_query("dayofweek"),locals())
	sorter = [ 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
	sorterIndex = dict(zip(sorter,range(len(sorter))))
	df_Day['Day_id'] = df_Day.index
	df_Day['Day_id'] = df_Day['Day_id'].map(sorterIndex)
	df_Day.sort_values('Day_id', inplace=True)
	df_Month = ps.sqldf(df_query("month"),locals()).sort_values(by=['month'])
	df_Hour = ps.sqldf(df_query("hour"),locals()).sort_values(by=['hour'])

	city_full = '"' + str(dropdown) + '_full"'
	dist = df_Districts['district'][1]
	df_full = pd.read_sql("SELECT date, longitude, latitude FROM " + city_full + ' WHERE pddistrict = "' + dist + '"', con)
	#df_full['tag'] = np.where(df_full['pddistrict']== dist, 1, 0)

	if tab == 'general-info':
		return html.Div(id='General',children=[
			html.H2(children='Safety Ranking',style={'text-align': 'center'}),
			html.Br(),
			html.Div([
				#builds graphs
				dcc.Graph(
					id='RankingofDistrict-graph', 
					animate = True,
					figure={
						'data': [
							{'x': df_Districts['district'], 'y': df_Districts['counts'], 'type': 'bar', 'name': 'DistrictsRanking'},
						],
						'layout': {
							'plot_bgcolor': colors['background'],
                			'paper_bgcolor': colors['background'],
							'hovermode': 'closest',
							'title': 'Ranking for Districts',
							'font': {
                    		'color': colors['text']
                    		}
						}
					}
				)
			]),

			html.Br(),

			html.Div([
				dcc.Graph(
					id='RankingofDay-graph',
					animate=True,
					figure={
						'data': [
							{'x': df_Day.dayofweek, 'y': df_Day.counts, 'type': 'scatter', 'name': 'DayRankingDot'},
                    	],
                    	'layout': {
                    		'hovermode': 'closest',
                    		'title': 'Ranking for Day of Week',
                    		'plot_bgcolor': colors['background'],
                			'paper_bgcolor': colors['background'],
                			'font': {
                    		'color': colors['text']
                    		}
                     	}
                    }
                )
            ]),

            html.Br(),

			html.Div([
				dcc.Graph(
					id='RankingofMonth-graph',
					animate=True,
					figure={
						'data': [
							{'x': df_Month.month, 'y': df_Month.counts, 'type': 'bar', 'name': 'MonthRanking'},
                     	],
                    	'layout': {
                    		'hovermode': 'closest',
                    		'title': 'Ranking for Months',
                    		'plot_bgcolor': colors['background'],
                			'paper_bgcolor': colors['background'],
                			'font': {
                    		'color': colors['text']
                    		}
                    	}
                    }
                )
            ]),

            html.Br(),

			html.Div([
				dcc.Graph(
					id='RankingofHour-graph',
					animate=True,
					figure={
						'data': [
							{'x': df_Hour.hour, 'y': df_Hour.counts, 'type': 'scatter', 'name': 'HourRanking'},
                     	],
                     	'layout': {
                     		'hovermode': 'closest',
                    		'title': 'Ranking for Hours',
                    		'plot_bgcolor': colors['background'],
                			'paper_bgcolor': colors['background'],
                			'font': {
                    		'color': colors['text']
                    		}
                    	}
                    }
                )
            ]),
		])

     	#building the Map tab
    # elif tab == 'map':
    # 	return {'data':[go.Scattergeo(
    # 				lon = df_full['Long'],
    # 				lat = df_full['Lat'],
    # 				text = df_full['district'],
    # 				mode = 'markers',
    # 				marker_color = df_full['tag']),],
    # 			'layout':{go.Layout(title='Map',
    # 				geo_scope='usa')}}
#             	html.Br(),
#             	html.H2(children='Top React Native Posts Discussing all Three Technologies',style={'text-align': 'center'}),
#             	dash_table.DataTable(
#                     	style_data={'whiteSpace': 'normal'},
#                     	css=[{'selector': '.dash-cell div.dash-cell-value', 'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'}],
#                 	id='react-native-cross-table',
#                 	columns=[{'name':"mentions", 'id':'total_link_id_count'},{'name':"Title", 'id':'title'},{'name':'url','id':'full_link'}],
#                 	data=df_react_native_cross_posts_full.to_dict("rows"),
#             	),
#             	html.Br(),
#             	html.H2(children='Top Flutter Posts Discussing all Three Technologies',style={'text-align': 'center'}),
#             	dash_table.DataTable(
#                     	style_data={'whiteSpace': 'normal'},
#                     	css=[{'selector': '.dash-cell div.dash-cell-value', 'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'}],
#                 	id='flutter-cross-table',
#                 	columns=[{'name':"mentions", 'id':'total_link_id_count'},{'name':"Title", 'id':'title'},{'name':'url','id':'full_link'}],
#                 	data=df_flutter_cross_posts_full.to_dict("rows")
#             	)]            
#         	)
    
#     	#the third search tab with update logic found lower
#     	elif tab == 'topic-search':
#         	return html.Div(children=[
#             	html.H5(children='Search for related technologies (example: seaborn, plotly, and ggplot)'),
#             	html.Div(dcc.Input(id='input-box-1', type='text')),
#             	html.Div(dcc.Input(id='input-box-2', type='text')),
#             	html.Div(dcc.Input(id='input-box-3', type='text')),
#             	html.Button('Submit', id='button'),
#             	html.Div(children='Enter a value and press submit'),

#             	html.Div(id='search-graph-and-table-container')
#         	])
            

#@app.callback(
#   dash.dependencies.Output('HackerNews-hover-text', 'children'),
#  [dash.dependencies.Input('HackerNews-graph', 'hoverData')])

if __name__  == '__main__':
	app.run_server(debug=True)






