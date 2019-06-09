"""Create a Dash app within a Flask app."""
import glob
from pathlib import Path
from dash import Dash
import dash_table
import dash_html_components as html
import pandas as pd
from .layout import html_layout
import json
from textwrap import dedent as d
import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import matplotlib as mpl
mpl.use('Agg') # headless!
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import time
import sys
import os
from dateutil import tz
from tzlocal import get_localzone


def Add_Dash(server=None):
    """Create a Dash app.
    Moved everything needed inside this function since otherwise the globals
    that need to be stored locally
    are not accessible during app operation and updates fail
    """
    from .loadcelldata import loadCellData
    
    def figUpdate(useFrac,filePath):
        lcd = loadCellData(NSD,filePath)
        nr = lcd.df.shape[0]
        if nr == 0:
            return {}
        if nr > 2000:
            useFrac = 2000.0/nr
            dat = lcd.df.sample(frac=useFrac)
        else:
            dat = lcd.df
        
        useFrac = float(useFrac)
        if useFrac == 0.0:
            useFrac = 0.0001
        nr = lcd.df.shape[0]
        if useFrac < 1:
            dat = lcd.df.sample(frac=useFrac)
            dat = dat.sort_index()
        else:
            dat = lcd.df
        figure = {
        'data': [
            {
                'x': dat.iloc[:,0],
                'y': dat.iloc[:,1],
                'mode': 'markers',
                'marker': {'size': 2}
            }
            ],
        'layout': {
            'clickmode': 'event+select',
            'title': '%.2f fraction of %d rows from %s' % (useFrac,nr,lcd.infile),
            'xaxis': {'title':'Time',

                        'titlefont':{
                        'family':'Arial, sans-serif',
                        'size':18,
                        'color':'darkblue'
                        },
                'showticklabels': True,
                'tickangle':45,
                'tickfont':{
                    'family':'Arial',
                    'size':9,
                    'color':'black'
                        }
                    },
            'yaxis': {'title':'Reported Mass (g)',
                      'titlefont':{
                        'family':'Arial, sans-serif',
                        'size':18,
                        'color':'darkblue'
                        },
                    },
                }
        }
        return figure

    def fileChooser():
        """something like [
                    {'label': 'New York City', 'value': 'NYC'},
                    {'label': 'Montreal', 'value': 'MTL'},
                    {'label': 'San Francisco', 'value': 'SF'}
                ]
        """
        dpath ="/home/ross/rossgit/dashInFlask/data/*.xls"
        fl = glob.glob(dpath)
        ddl = []
        for fn in fl:
            ddl.append({'label':fn.split('/')[-1],'value': fn})
        print('##s = ',ddl)
        return ddl


    
    external_stylesheets = ['/static/dist/css/styles.css',
                            'https://fonts.googleapis.com/css?family=Lato',
                            'https://use.fontawesome.com/releases/v5.8.1/css/all.css']
    external_scripts = ['/static/dist/js/includes/jquery.min.js',
                        '/static/dist/js/main.js']
    dash_app = Dash(server=server,
                    external_stylesheets=external_stylesheets,
                    external_scripts=external_scripts,
                    routes_pathname_prefix='/localdata/')

    # Override the underlying HTML template
    dash_app.index_string = html_layout
    tzl = get_localzone().zone
    mdates.rcParams['timezone'] = tzl
    NSD = 2.0
    useFrac = 1.0
    filePath = '/home/ross/rossgit/dashInFlask/data/loadcellsample55k.xls'
    # setup before anything else
    lcd = loadCellData(NSD,filePath)
    lastFilePath = filePath
    nr = lcd.df.shape[0]
    if nr > 2000:
        useFrac = 2000.0/nr
        dat = lcd.df.sample(frac=useFrac)
    else:
        dat = lcd.df
   
    # Create Dash Layout comprised of Data Tables
    dash_app.layout = html.Div([

        html.Div( 
            dcc.Graph(
                id='aplot',
                figure = {} 
                ),
            ), 
               
            html.Div(style={'width': 300, 'textAlign':'center'}, children = [
                html.Div(style={'width': 300, 'textAlign':'center'}, children = [
                    dcc.Store(id='localstore', storage_type='session',
                        data={'filePath': filePath, 'useFrac': 1}),
                    html.Div('File path to load when reload button pressed',
                      style={"fontSize":"small", "width":299, "textAlign":"center", "color": "darkred"}),
                    dcc.Dropdown(
                    id='chooser',
                    options=fileChooser(),
                    value = []),
                    ]),
                html.Div('Fraction of all data to sample randomly when reload button pressed',
                  style={"fontSize":"small", "width":299, "textAlign":"center", "color": "darkred"}),
                html.Div(dcc.Slider(id='frac', min=0.0,max=1,step=0.001,marks={i/10.0: "{}".format(i/10.0) for i in range(1,11)},
                    value=useFrac),title="Set fraction to reload",n_clicks=0),
                html.Br(),
                html.Button('Reload data sample', id='reloadbutton',n_clicks_timestamp=None,
                 style={'width': 295, 'backgroundColor': "lightblue", "color": "darkred","fontSize":"small"})
            ])
      ])
      
    @dash_app.callback(
        Output('aplot', 'figure'),
        [Input('reloadbutton', 'n_clicks_timestamp')],
        [State('localstore', 'data'),State('frac','value'),State('chooser','value')])
    def updateFigure(reloadtime,sessdat,frac,fpath):
        return figUpdate(sessdat['useFrac'],sessdat['filePath'])
        
    @dash_app.callback(
        Output('localstore', 'data'),
        [Input('chooser','value'),Input('frac','value')],
        [State('localstore', 'data')]
        )
    def updateFigure2(fpath,frac,sessdat):
        sessdat['filePath'] = fpath
        sessdat['useFrac'] = frac
        return sessdat

    return dash_app.server

if __name__ == '__main__':
    app.run_server(debug=True,port=8051,host='0.0.0.0')
