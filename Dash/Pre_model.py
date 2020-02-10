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
from sqlalchemy import create_engine

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

def get_pre(dropdown):
	con = psycopg2.connect(
        host = "db1.cakrcx1k6r20.us-west-2.rds.amazonaws.com",
        database = "postgres",
        user = "postgres",
        password = "postgres")
	cur = con.cursor()
	city = '"' + str(dropdown) + '"'
	df = pd.read_sql("SELECT * FROM " + city, con)
	df_Districts = ps.sqldf(df_query('district'),locals()).sort_values(by=['counts'])
	dist = df_Districts['district'][1]
	df_full = pd.read_sql("SELECT date, longitude, latitude FROM " + city_full + " WHERE pddistrict = '" + dist + "'", con)
	return df_full

def write_out(dropdown):
	engine = create_engine('postgresql+psycopg2://postgres:postgres@db1.cakrcx1k6r20.us-west-2.rds.amazonaws.com:5432/postgres')
	df_full = get_pre(dropdown)
	df_trin = time_trend(df_full)
	df_prediction = predict_trend(df_train).to_frame()
	df_prediction = df_prediction.reset_index()
	df_prediction.columns = ['date', 'count']
	table_name = dropdown + "_Pre"
	train_table = dropdown + "_Train"
	df_prediction.to_sql(table_name, con = engine, if_exists = 'replace')
	df_train.to_sql(train_table, con = engine, if_exists = 'replace')

write_out('SF')





    	
