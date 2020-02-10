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
from statsmodels.tsa.stattools import arma_order_select_ic
import statsmodels as sm
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.arima_model import ARMA

def df_query(col):
    query = "SELECT " + col + ", SUM(count) AS counts FROM df GROUP BY " + col
    return query

def time_trend(df_full):
    df_pre = ps.sqldf('SELECT Date, COUNT() AS count FROM df_full GROUP BY Date ORDER BY date',locals())
    df_pre['date'] = pd.to_datetime(df_pre['date'])
    df_pre = df_pre.set_index('date').asfreq('D')
    df_train = df_pre.loc['2017-01-01':'2019-12-31']
    return df_train

def predict_trend(df_train):
    diff1 = df_train.diff().dropna()
    res = arma_order_select_ic(diff1,max_ar=6,max_ma=4,ic='aic')['aic_min_order']
    arima_mod = ARIMA(df_train, order=(res[0],1,res[1])).fit()
    # Make a prediction for 3 months
    prediction = arima_mod.predict('2020-01-01', '2020-03-31')
    return prediction

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
        #dcc.Tab(label='Visualize on Map', value='map'),
        dcc.Tab(label='Prediction', value='prediction'),
    ]),
    html.Div(id='graphs')
])

#These are the main and secondary pages in tab 1 and 2
@app.callback(
    Output('graphs', 'children'),
	[Input('tabs-navigation', 'value'),
	Input('first-dropdown', 'value')
    ]
)

def update_graph(tab, dropdown):

    con = psycopg2.connect(
        host = "db1.cakrcx1k6r20.us-west-2.rds.amazonaws.com",
        database = "postgres",
        user = "postgres",
        password = "postgres")

    cur = con.cursor()

    if dropdown is not None:
        city = '"' + str(dropdown) + '"'
        df = pd.read_sql("SELECT * FROM " + city, con)
        df_Districts = ps.sqldf(df_query('district'),locals()).sort_values(by=['counts'])
        df_Day = ps.sqldf(df_query('dayofweek'),locals())
    	#sorter = [ 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    	#sorterIndex = dict(zip(sorter,range(len(sorter))))
    	#df_Day['Day_id'] = df_Day.index
    	#df_Day['Day_id'] = df_Day['Day_id'].map(sorterIndex)
        df_Day['Day_id'] = [4,0,5,6,3,1,2]
        df_Day.sort_values('Day_id', inplace=True)
        df_Month = ps.sqldf(df_query('month'),locals()).sort_values(by=['month'])
        df_Month = df_Month[df_Month['month']<13]
        df_Hour = ps.sqldf(df_query('hour'),locals()).sort_values(by=['hour'])

        best_day = df_Day.sort_values(by = ['counts'])['dayofweek'][1]
        best_month = df_Month.sort_values(by = ['counts'])['month'][1]
        best_hour = df_Hour.sort_values(by = ['counts'])['hour'][1]

        city_full = '"' + str(dropdown) + '_full"'
        dist = df_Districts['district'][1]
        df_full = pd.read_sql("SELECT date, longitude, latitude FROM " + city_full + " WHERE pddistrict = '" + dist + "'", con)
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
    						'data': [{'x': df_Districts['district'], 'y': df_Districts['counts'], 'type': 'bar', 'name': 'DistrictsRanking'},],
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

                html.Label('From the plot above, we recommand you choose the city with the least recorded crimes'),
    			
                html.Br(),
                html.Br(),

    			html.Div([
    				dcc.Graph(
    					id='RankingofDay-graph',
    					animate=True,
    					figure={
    						'data': [{'x': df_Day.dayofweek, 'y': df_Day.counts, 'type': 'scatter', 'name': 'DayRankingDot'},],
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

                html.Label('We recommand you to take travel on ' + best_day),
                
                html.Br(),
                html.Br(),

    			html.Div([
    				dcc.Graph(
    					id='RankingofMonth-graph',
    					animate=True,
    					figure={
    						'data': [{'x': df_Month.month, 'y': df_Month.counts, 'type': 'bar', 'name': 'MonthRanking'},],
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

                html.Label('We recommand you to take travel on month ' + str(best_month)),
                
                html.Br(),
                html.Br(),

    			html.Div([
    				dcc.Graph(
    					id='RankingofHour-graph',
    					animate=True,
    					figure={
    						'data': [{'x': df_Hour.hour, 'y': df_Hour.counts, 'type': 'scatter', 'name': 'HourRanking'},],
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

                html.Br(),

                html.Label(str(best_hour) + " o'clock is the safest time in this city")
    		])

    #building the Prediction tab
        elif tab == 'prediction':
            pre_table = '"' + dropdown + "_Pre" + '"'
            train_table = '"' + dropdown + "_Train" + '"'
            df_train = pd.read_sql("SELECT * FROM " + train_table, con)
            df_pre = pd.read_sql("SELECT * FROM " + pre_table, con)

            return html.Div(id='Prediciton',children=[
                    html.H2(children='Crime Trends in the Past and Future',style={'text-align': 'center'}),
                    html.Br(),
                    html.Div([
                        #builds graphs
                        dcc.Graph(
                            id='Past-graph', 
                            animate = True,
                            figure={
                                'data': [{'x': df_train['date'], 'y': df_train['count'], 'type': 'line', 'name': 'Past'},],
                                'layout': {
                                    'plot_bgcolor': colors['background'],
                                    'paper_bgcolor': colors['background'],
                                    'hovermode': 'closest',
                                    'title': 'Past Crime Trends',
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
                        id='Future-graph',
                        animate=True,
                        figure={
                            'data': [{'x': df_pre['date'], 'y': df_pre['count'], 'type': 'line', 'name': 'Future'},],
                            'layout': {
                                'hovermode': 'closest',
                                'title': 'Crime Trends for Next 3 Months',
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


    #close the SQL 
    con.close()        


if __name__  == '__main__':
    app.run_server(debug=True)






