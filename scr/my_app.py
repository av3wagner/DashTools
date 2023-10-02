from datetime import datetime
import pandas as pd
import numpy as np
import sqlite3
import dash
from dash import dash_table
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash import Dash, dcc, html, Input, Output, State, callback
import plotly.express as px
import plotly.graph_objects as go
import chart_studio.plotly as py 
from jupyter_dash import JupyterDash
import flask
import json
import requests
from urllib.request import urlopen
from prophet import Prophet
from pandas_datareader import data, wb

################################## Alt-data ###############################
cnx = sqlite3.connect('data/KZAPP.db')
df=pd.read_sql_query("Select ID1, ID, IDNAME, POP, MKN, FKN FROM KZ_ALL where AGEN=1", cnx) 
pop=pd.read_sql_query("Select ID, MKN, FKN FROM KZ_POP ORDER BY AGEN DESC", cnx) 

my_list=['< 5 лет','5 - 9 лет','10 - 14 лет','15 - 19 лет','20 - 24 лет','25 - 29 лет','30 - 34 лет','35 - 39 лет',
'40 - 44 лет','45 - 49 лет','50 - 54 лет','55 - 59 лет','60 - 64 лет','65 - 69 лет','70 - 74 лет','75 - 79 лет',
'80 - 84 лет','85+ лет']

map_obj = map(str.upper, my_list)
y = list(map_obj)

age_df = pd.read_csv('data/country_data_master.csv', 
                     usecols=lambda cols: 'perc' in cols or cols == 'country' or cols == 'median_age_total')
age_df = age_df.sort_values(['median_age_total'])
age_categories = ['0-14', '15-24', '25-54', '55-64', '65+']

#df_stock= pd.read_sas(f'data/stock_price_FB.sas7bdat', encoding="latin-1")
#df_pred = pd.read_sas(f'data/pred_prophet_FB.sas7bdat', encoding="latin-1")
#FP =pd.read_sas('data/All_prophet_fb.sas7bdat', encoding="latin-1")
#pyperclip.copy("KZ-11")
################################# Neu-data ################################
country = pd.read_csv('data/country.csv')
dfkaz = pd.read_csv('data/gadm36_KAZ_2.csv')
dfkaz["unemp"]= np.random.uniform(10.4, dfkaz["IDNUM"])
districts = dfkaz.NAME_1.values
polygons = requests.get(
   'https://raw.githubusercontent.com/open-data-kazakhstan/geo-boundaries-kz/master/data/geojson/kz_1.json'
).json()
Tod_summy = pd.read_csv('data/tod_summy.csv')
tod2022 = pd.read_csv('data/tod2022.csv')
GRlist = ['Всего', 'Мужчины', 'Женщины']
tod_age = pd.read_csv('data/tod_age.csv')
GRlist = ['Всего', 'Мужчины', 'Женщины']
land = tod_age #[tod_age['F1'] != "All"]
land =  land[land['AGE'] !="Всего"]
tod1 =  land[land['GR'] !="Всего"]
tod_summy = pd.read_csv('data/tod_summy.csv')
mkb_list = ['All',  'C33-C34', 'C50', 'E10-E14',
 'E24.4, F10, G31.2, G62.1, G72.1, I42.6, K29.2, K70', 'I10-I13, I15',
 'I20-I25', 'I60-I69', 'J12, J15, J16- J18', 'J40-J44',
 'K73, K74.0-K74.2, K74.6']
mkb=tod_summy[tod_summy['GR'] != "Всего"]
tod2=mkb[mkb['F1'] != "All"]
excel_data_df = pd.read_excel('data/Pilot2022.xlsx', sheet_name='Population')
population=excel_data_df[excel_data_df['Age']!='All']
allpop = pd.read_excel('data/Pilot2022.xlsx', sheet_name='AllPopulation')
#DesktopWidth: 1920 DesktopHeight: 1080
colors = {
    'background': '#4A235A',
    'background2': 'black',
    'text': 'yellow'
}

colors = ['red', '#9C0C38', 'orange']
tabs_styles = {"height": "30px"}

tab_style = {
    "borderBottom": "1px solid #d6d6d6",
    "padding": "2px",
    "fontWeight": "bold",
    "vertical-align": "middle",
    "backgroundColor": "#111111", 
}

tab_selected_style = {
    "borderTop": "1px solid #d6d6d6",
    "borderBottom": "1px solid #d6d6d6",
    "backgroundColor": "#111111",
    "color": "yellow",
    "padding": "5px",
    "font-size": 18,
}

app = JupyterDash(external_stylesheets=[dbc.themes.SLATE])
svalue="KZ-00"
rcountry=country[country['ID'] == svalue]

app.title = "Kazakhstan Dashboard"
app.layout = html.Div([
  html.Div(className="row", children=[ 
     html.Div([html.Label(['Выберите группу для анализа:'], style={'color': 'yellow'}),
        dcc.Dropdown(id='dropdown',
                     multi=False,
                     clearable=True,
                     disabled=False,
                     style={'display': True},
                     value='Всего',
                     options=[{'label': i, 'value': i} for i in GRlist],
                    )

         ],style={'width':'12%','display':'inline-block','vertical-align':'middle',
                  'marginLeft':16,'marginRight':0,'marginTop':0,
                  'marginBottom':0, 'padding': '1px 1px 1px 1px'
      }), 
      
      html.Div([html.Label(['МКБ-10'], style={'color': 'yellow'}),
        dcc.Dropdown(id='mkb',
                     multi=False,
                     clearable=True,
                     disabled=False,
                     style={'display': True},
                     value='All',
                     options=[{'label': i, 'value': i} for i in mkb_list],
                    )

         ],style={'width':'12%','display':'inline-block','vertical-align':'middle',
                  #'background-color':'#FCE22A',
                  #'margin':'0 auto', 'height':'15px',
                  'marginLeft':16,'marginRight':0,'marginTop':0,
                  'marginBottom':0, 'padding': '1px 1px 1px 1px'
      }),  
      
     html.Div(["", 
             dcc.Input(id='my-input', value='KZ-19', type='text', placeholder='', 
             style={'display':'inline-block', 'border': '1px solid black', "height": "30px", 
                    #'background-color': 'black', 'border-color': 'white', 'color': 'yellow', 'width':'150px'})  
                    'background-color': "#111111", 'border-color': "#111111", 'color': "#111111", 'width':'5px'})  
       ],style={"background": "#111111", 'width':'5px',"height": "3px", 'marginLeft':19,'marginRight':5}),  
     ]
   ), 
       
 dcc.Tabs(id="tabs-with-classes", value='Table0', 
              parent_className='custom-tabs', 
              className='custom-tabs-container',
        children=[
            dcc.Tab(
                label="Старт",
                value="Table0",
                style=tab_style,
                selected_style=tab_selected_style,
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
  
           dcc.Tab(
                label="Смертность населения в 2022г",
                value="Table6",
                style=tab_style,
                selected_style=tab_selected_style,
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
            
            dcc.Tab(
                label="Pаспределение населения по годам",
                value="Table5",
                style=tab_style,
                selected_style=tab_selected_style,
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
            
            dcc.Tab(
                label="Демография",
                value="Table1",
                style=tab_style,
                selected_style=tab_selected_style,
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
            dcc.Tab(
                label="Популяция",
                value="Table2",
                style=tab_style,
                selected_style=tab_selected_style,
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
            dcc.Tab(
                label="Возрастное распределение по странам",
                value="Table3",
                style=tab_style,
                selected_style=tab_selected_style,
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
            dcc.Tab(
                label="Прогноз заболеваемости",
                value="Table4",
                style=tab_style,
                selected_style=tab_selected_style,
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
         ],
         style=tabs_styles,
         colors={"border": "yellow", "primary": "red",
                 "background": "#111111",},
     ),html.Div(id='tabs-content-classes')
   ],style={"background": "#111111", 'marginLeft':5,'marginRight':20}
  ) 

@app.callback(Output('tabs-content-classes', 'children'),
              Input('tabs-with-classes', 'value'))

def render_content(value): 
    tab=value
    print(tab)
    print(svalue)
    
    if tab == 'Table0':
        return [html.Div(
            children=[
                    html.H1('Карта Республики Казахстан (для обновления данных кликнике мышкой на выбранную область)', 
                            style={'textAlign': 'center', 'font-size': '42px', 'color': '#00BFFF'}),                       
                    html.Div(
                        className="six columns",
                        children=[html.Div(children=dcc.Graph(id='map_plot1',figure = fig_map(df)))
                        ],style={'width':'49.50%',"height": '610px','display':'inline-block',
                             'vertical-align':'middle',
                             'border':'3px solid','marginLeft':16,'marginRight':0,'marginTop':0,
                             'marginBottom':0, 'padding': '1px 1px 1px 2px'},
                    ),
                
                    html.Div(className="twelve columns",  
                    children=[html.Div(children=dcc.Graph(id='my-graph1')) 
                     ],style={'width':'49.50%',"height": "610px",'display':'inline-block',
                                 'vertical-align':'middle',
                                 'border':'3px solid','marginLeft':3,'marginRight':0,'marginTop':0,
                                 'marginBottom':0, 'padding': '1px 1px 1px 2px'}),
                html.Div(
                className="twelve columns", 
                children=[html.Div(children=dash_table.DataTable(id='tod2022',
                fixed_rows={"headers": True}, #, "data": 4},  
                style_cell={'backgroundColor': '#111111',
                            'color': 'yellow', 
                            'textAlign':'left','minWidth': 45, 'maxWidth': 95, 'width': 65,
                            'font_size': '16px',"fontWeight": "bold", 'whiteSpace':'normal','height':'auto'},         
                
                style_header={"backgroundColor": "#111111",
                              "color": "yellow",
                              "font-size": "18px",
                              "fontWeight": "bold"
                             },               

                style_table={"height": "400px",
                              "font-size": "18px",
                              "margin": 0,
                              "padding": "8px",
                              "backgroundColor": "#111111"
                              },
                ), style={'width':'99.5%', 'height': '400px',  
                           #'border':'3px solid',
                           'marginLeft':3,'marginRight':0,'marginTop':0,
                          },
                )
               ],style={'width':'99.5%',"height": "410px",'display':'inline-block','vertical-align':'middle',
                  'border':'3px solid','marginLeft':16,'marginRight':0,'marginTop':0,
                  'marginBottom':0, 'padding': '1px 1px 1px 2px'},      
               ),
            ])]         
    
    elif tab == 'Table1':
        print("Table1 OK!")
        return [html.Div([
             html.H1('Демография', style={'textAlign': 'center', 'font-size': '42px', 'color': '#00BFFF'}),                
             html.Div(className="six columns",
                children=[
                   html.Div(
                    children=dcc.Graph(id="pie_graph") 
                )
            ],style={'width':'40.0%','display':'inline-block','vertical-align':'middle',
                     'border':'3px solid','marginLeft':16,'marginRight':0,'marginTop':0,
                     'marginBottom':0, 'padding': '5px 0px 0px 0px'},
          ),
          html.Div(
                    className="twelve columns",
                    children=[
                        html.Div(
                            children=dcc.Graph(id='bottom-bar-graph')
                        )
                    ],style={'width':'58.0%','display':'inline-block','vertical-align':'middle',
                         'border':'3px solid','marginLeft':3,'marginRight':0,'marginTop':0,
                         'marginBottom':0, 'padding': '5px 0px 0px 0px'},
                ),
       ])]
    
    elif tab == 'Table2':
        print("Table2 OK!")
        #value='Table2'
        return [html.H1('Популяция',style={'textAlign': "center", 'font-size': '42px', 'color': '#00BFFF'}),
            html.Div(className="six columns",
                children=[html.Div(children=dcc.Graph(id="pop-graph"))
              ],style={'width':'49.5%','display':'inline-block','vertical-align':'middle',
                 'border':'3px solid','marginLeft':16,'marginRight':0,'marginTop':0,
                 'marginBottom':0, 'padding': '5px 0px 0px 0px'},  
            ),                 
            html.Div(className="twelve columns",
                    children=[html.Div(children=dcc.Graph(id='sun_graph'))    
              ],style={'width':'49.5%', 'display':'inline-block',
                             'vertical-align':'middle',
                             'horizontal-align':'middle',                                  
                             'border':'3px solid','marginLeft':3,'marginRight':0,'marginTop':0,
                             'marginBottom':0, 'padding': '5px 0px 0px 0px'},                     
             ),          
        ]
    
    elif tab == 'Table3':
        print("Table3 OK!")
        #value='Table3'
        return [html.H1('Возрастное распределение населения по данным ВОЗ (по избранным странам)',
                         style={'textAlign': "center", 'font-size': '42px', 'color': '#00BFFF'}),
           html.Div(
            className="six columns",
                children=[
                   html.Div(    
                    children=dcc.Graph(id='median_age_graph')
                   )], style={'width':'49.5%',"height": "610px", 'display':'inline-block','vertical-align':'middle',
                              'border':'3px solid','marginLeft':16,'marginRight':0,'marginTop':0,
                              'marginBottom':0, 'padding': '5px 1px 1px 1px'},                                           
                
          ),
                
            html.Div([        
             dcc.Graph(id='age_graph')
             ],style={'width':'49.5%', "height": "610px", 'display':'inline-block','vertical-align':'middle',
                      'border':'3px solid','marginLeft':3,'marginRight':0,'marginTop':0,
                      'marginBottom':0, 'padding': '5px 1px 1px 1px'},                  
          )                
        ]
     
    elif tab == 'Table4':
        return [html.H1("Прогноз заболеваемости с помощью анализа временных рядов (условные данные)", 
                 style={'textAlign': 'center', 'font-size': '42px', 'color': '#00BFFF'}),
            html.Div(
                className="row",
                children=[
                html.Div(
                  className="twelve columns",
                  children=[
                    html.Div(
                       children=dcc.Graph(id="graph_close"),
                      )
                   ],style={'width':'98.5%', "height": '508px', 
                            'border':'3px solid','marginLeft':16,'marginRight':0,'marginTop':5,
                            'marginBottom':0, 'padding': '1px 1px 1px 2px'},
                    ),
                   ] 
                  ),
            ]    
    
    elif tab == 'Table5':
        print("Table5 OK!")
        return [html.Div([
             html.H1('Анализ распределения населения области по годам наблюдения по официальным данным', style={'textAlign': 'center', 'font-size': '42px', 'color': '#00BFFF'}),                
             html.Div(
                    className="six columns",
                    children=[html.Div(children=dcc.Graph(id='my-graph5'))
                    ],style={'width':'49.5%',"height": "610px",'display':'inline-block','vertical-align':'middle',
                         'border':'3px solid','marginLeft':3,'marginRight':0,'marginTop':0,
                         'marginBottom':0, 'padding': '5px 0px 0px 0px'},
                ),
            
             html.Div(className="six  columns",  
                    children=[html.Div(children=dcc.Graph(id='popylation', figure=FigurePop(svalue))), 
                     ],style={'width':'49.50%',"height": "610px",'display':'inline-block',
                                 'vertical-align':'middle',
                                 'border':'3px solid','marginLeft':3,'marginRight':0,'marginTop':0,
                                 'marginBottom':0, 'padding': '1px 1px 1px 2px'}),  
              html.Div(
                className="twelve columns", 
                children=[html.Div(children=dash_table.DataTable(id='table-year',
               
                                                                 
                fixed_rows={"headers": True}, #, "data": 4},                                                 
                style_cell={"width": "100px",
                            'backgroundColor': '#111111',
                            'color': 'yellow'          
                             },
                
                style_header={"backgroundColor": "#111111",
                              "color": "yellow",
                              "font-size": "18px",
                              "fontWeight": "bold"
                             },               

                style_table={"height": "400px",
                              "font-size": "18px",
                              "margin": 0,
                              "padding": "8px",
                              "backgroundColor": "#111111"
                              }), style={'width':'99.5%', 'height': '405px',  
                                 #'border':'3px solid',
                                 'marginLeft':3,'marginRight':0,'marginTop':0,
                                 'marginBottom':0, 'padding': '1px 1px 1px 2px'
                                }
          )                                                  
        ],style={'width':'49.5%',"height": "410px",'display':'inline-block','vertical-align':'middle',
                  'border':'3px solid',
                  'marginLeft':3,'marginRight':0,'marginTop':0,
                  'marginBottom':0, 'padding': '5px 0px 0px 0px'},
       ),
        
       html.Div(
                className="twelve columns", 
                children=[html.Div(children=dash_table.DataTable(id='table2122',
                fixed_rows={"headers": True}, #, "data": 4},                                                 
                style_cell={"width": "100px",
                            'backgroundColor': '#111111',
                            'color': 'yellow'          
                             },
                
                style_header={"backgroundColor": "#111111",
                              "color": "yellow",
                              "font-size": "18px",
                              "fontWeight": "bold"
                             },               

                style_table={"height": "400px",
                              "font-size": "18px",
                              "margin": 0,
                              "padding": "8px",
                              "backgroundColor": "#111111"
                              }), style={'width':'99.5%', 'height': '405px',  
                                 #'border':'3px solid',
                                 'marginLeft':3,'marginRight':0,'marginTop':0,
                                 'marginBottom':0, 'padding': '1px 1px 1px 2px'
                                }
          )                                                  
        ],style={'width':'49.5%',"height": "410px",'display':'inline-block','vertical-align':'middle',
                  'border':'3px solid',
                  'marginLeft':3,'marginRight':0,'marginTop':0,
                  'marginBottom':0, 'padding': '5px 0px 0px 0px'},
       ),     
            
   ])]
    elif tab == 'Table6':
        print("Table6 OK!")
        return [html.Div([
             html.H1('Анализ смертности населения по возрасту, полу, и МКБ-10 в 2022г', style={'textAlign': 'center', 'font-size': '42px', 'color': '#00BFFF'}),                
             html.Div(className="six  columns",  
                    children=[html.Div(children=dcc.Graph(id='my-graph6')), 
                     ],style={'width':'49.50%',"height": "610px",'display':'inline-block',
                                 'vertical-align':'middle',
                                 'border':'3px solid','marginLeft':3,'marginRight':0,'marginTop':0,
                                 'marginBottom':0, 'padding': '1px 1px 1px 2px'}),  
            
             html.Div(className="twelve columns",  
                    children=[html.Div(children=dcc.Graph(id='mkb-graph', figure=FigureTod2(svalue)))
                     ],style={'width':'49.50%',"height": "610px",'display':'inline-block',
                                 'vertical-align':'middle',
                                 'border':'3px solid','marginLeft':3,'marginRight':0,'marginTop':0,
                                 'marginBottom':0, 'padding': '1px 1px 1px 2px'}),

   ])]    
    

if __name__ == '__main__':
    app.run_server(debug=False)
