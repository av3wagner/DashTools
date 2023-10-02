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

#excel_data_df = pd.read_excel('data/Pilot2022.xlsx', sheet_name='Population')
#population=excel_data_df[excel_data_df['Age']!='All']
#allpop = pd.read_excel('data/Pilot2022.xlsx', sheet_name='AllPopulation')
#app.layout = html.Div([
#    html.Div(children='Hello World')
#])

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
server=app.server
svalue="KZ-00"
rcountry=country[country['ID'] == svalue]
def fig_map(df):
    #print("fig_map wurde gestartet!")
    figm = px.choropleth(
        dfkaz,
        geojson=polygons,
        locations="NAME_1",
        hover_name= "ID", #"NAME_1",
        featureidkey="properties.NAME_1",
        color="unemp",
        color_continuous_scale="Viridis",
        title="Republic Kazakhstan",
        template="plotly_dark",
        range_color=(0, 12),
        width=1000, height=600,
     )
    figm.update_layout(
            autosize=False,
            margin = dict(
                    l=0,
                    r=0,
                    b=0,
                    t=0,
                    pad=4,
                    autoexpand=True
                ),
          )   
    figm.update_geos(fitbounds="locations", visible=True)
    return figm

def FigureTod1(value):
    #print("FigureStart wurde gestartet!")
    figure = px.bar(tod1,  x='AGE', y="Count",
    barmode="group",                 
    title="Распределение смертности по возрасту и полу",             
    orientation= 'v',
    height=605,                     
    hover_data={'Count': False},
    text='Count',                    
    labels=dict(y="Количество", x="Boзраст"), 
    color="GR",    
    ).update_layout(
    font=dict(family="silom",
               size=18, 
               color="Yellow"),
    plot_bgcolor = "#111111",
    paper_bgcolor= "#111111")
     
    figure.update_xaxes(tickangle=45, title_text="Возраст",title_font={"size": 18},
    title_standoff=5, tickfont=dict(family='silom', color='Yellow', size=14))
    figure.update_yaxes(title_text="Количество",title_font={"size": 18},title_standoff=5)
    
    figure.update_layout(title={
        'y':0.99,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        font=dict(family="silom",size=18,color="Yellow"))
    return figure  

def FigureTod2(value):
    print("FigureStart wurde gestartet!")
    figure = px.bar(tod2,  x='F1', y="SUMM",
    barmode="group",                 
    title="Распределение смертности по полу и МКБ-10",             
    orientation= 'v',
    height=605,                     
    hover_data={'SUMM': False},
    text='SUMM',                    
    labels=dict(y="Количество", x="Boзраст"), 
    color="GR",    
    ).update_layout(
    font=dict(family="silom",
               size=18, 
               color="Yellow"),
    plot_bgcolor = "#111111",
    paper_bgcolor= "#111111")
     
    figure.update_xaxes(tickangle=45, title_text="Возраст",title_font={"size": 18},
    title_standoff=5, tickfont=dict(family='silom', color='Yellow', size=14))
    figure.update_yaxes(title_text="Количество",title_font={"size": 18},title_standoff=5)
    
    figure.update_layout(title={
        'y':0.99,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        font=dict(family="silom",size=18,color="Yellow"))
    return figure 

def FigurePop(value):
    print("FigurepoРulation wurde gestartet!")
    figure = px.bar(population,  x='Age', y="Count",
    barmode="group",    
    title="Распределение население области по возрасту в 2021-2022гг",             
    orientation= 'v',
    height=605,                     
    hover_data={'Count': False},
    text='Count',                    
    labels=dict(y="Количество", x="Boзраст"), 
    color="Year",    
    ).update_layout(
    font=dict(family="silom",
               size=18, 
               color="Yellow"),
    plot_bgcolor = "#111111",
    paper_bgcolor= "#111111")
     
    figure.update_xaxes(tickangle=45, title_text="Возраст",title_font={"size": 18},
    title_standoff=5, tickfont=dict(family='silom', color='Yellow', size=14))
    figure.update_yaxes(title_text="Количество",title_font={"size": 18},title_standoff=5)
    
    figure.update_layout(title={
        'y':0.99,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        font=dict(family="silom",size=18,color="Yellow"))
    return figure  


def plot_countries(value):
    dfM = Tsummy[Tsummy['GR'].isin(countries)]
          
    return {
        'data': [go.Bar(x=GR_categories,
                        y=[0 for i in range(len(GR_categories))],
                        showlegend=False,
                        width=0.1,
                        hoverinfo='none')] +
                
                [go.Bar(x=age_categories,
                        y=dfM.iloc[x, 2:7],
                        name=dfM.iloc[x, 0],
                        text=dfM.iloc[x, 2:7].astype(str) + '%',
                        hoverinfo='name+y',
                        textposition='inside',
                        textfont={'color': 'Yellow'})
                 for x in range(len(dfM))],
        'layout': go.Layout(title={
                            'text': 'Возрастное (%) распределение по странам: ' + ', '.join(countries),                
                            'y':0.99,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'},
                            xaxis={}, 
                            yaxis={}, 
                            barmode='group',
                              #color='y',
                              #color_discrete_sequence=go.colors.sequential.Viridis,
                            plot_bgcolor="#111111",
                            paper_bgcolor="#111111",
                            height=600, 
                            font=dict(family="silom",
                                      size=18, color="Yellow")
                           )
        
    }    

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
#######################################################################
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
        print("Table4 OK!")
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
        
                html.Div(dash_table.DataTable(
                id='table-end',
                data=FP.to_dict('records'),    
                columns=[
                    {"name": i, "id": i, "deletable": True, "selectable": True} for i in FP.columns
                  ],
                fixed_rows={"headers": True, "data": 4},  
                style_cell={"width": "100px",
                              'backgroundColor': '#111111',
                              'color': 'yellow'          
                             },
                
                style_header={"backgroundColor": "#111111",
                              "color": "yellow",
                              "font-size": "12px",
                              "fontWeight": "bold"
                             },               

                style_table={"height": "250px",
                              "font-size": "18px",
                              "margin": 0,
                              "padding": "8px",
                              "backgroundColor": "#111111"
                              }), style={'width':'99.95%', 'height': '257px',  
                                 'border':'3px solid','marginLeft':3,'marginRight':0,'marginTop':10,
                                 'marginBottom':0, 'padding': '1px 1px 1px 2px'}
               ) 
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
    
@app.callback(Output("pie_graph", "figure"), 
              Input("my-input", "value"))

def drawFigurePie(value):
    ID1=value
    #ID = pyperclip.paste()
    df2=df[df['ID1']==ID1]
    figure = px.pie(df2,
    values='POP',
    names='IDNAME', 
    template="plotly_dark", 
    hole=.3,                                    
    height=600, 
    color_discrete_sequence = px.colors.sequential.Plasma_r)
    figure.update_layout(autosize=False, font=dict(family="silom",size=14, color="Yellow"))
    figure.update_layout(title={
        'text': "Prozentuale Verteilung der Bevölkerungszahl in der Region nach Territorium",                                    
        'y':0.99,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        font=dict(family="silom",size=18,color="Yellow"))
 
    return figure

@app.callback(Output("bottom-bar-graph", "figure"), 
              Input("my-input", "value"))

def drawFigureBar(value):
    ID1=value 
    df1=df[df['ID1']==ID1]
        
    figure = px.bar(df1, x="IDNAME", y="POP", 
    title="Absolute Verteilung der Bevölkerungszahl in der Region nach Territorium",                
    orientation= 'v',
    height=600,                     
    color = "POP", hover_data={'POP': False},
    labels=dict(POP="Anzahl", IDNAME="Territorium"),                
    color_discrete_sequence = px.colors.sequential.Plasma_r).update_layout(
    font=dict(family="silom",
               size=14, 
               color="Yellow"),
    plot_bgcolor = "#111111",
    paper_bgcolor= "#111111")
    figure.update_xaxes(tickangle=45, title_text="Territorium",title_font={"size": 14},
    title_standoff=5, tickfont=dict(family='silom', color='Yellow', size=12))
    figure.update_yaxes(title_text="Anzahl",title_font={"size": 12},title_standoff=5)
    figure.update_layout(title={
        'text': "Absolute Verteilung der Bevölkerungszahl in der Region nach Territorium",                
        'y':0.99,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        font=dict(family="silom",size=18,color="Yellow"))
        
    return figure

@app.callback(Output("pop-graph", "figure"), 
              Input("my-input", "value"))    
def pyramide(value):  
    ID1=value 
    df1=df[df['ID1']==ID1]
    df1=pop[pop['ID']==ID1] 
    men_bins = df1['MKN'].to_numpy()
    women_bins = df1['FKN'].to_numpy()
    
    layout = go.Layout(yaxis=go.layout.YAxis(title='Alter'),
                       xaxis=go.layout.XAxis(
                           range=[-5, 5],
                           tickvals=[-6, 6],
                           title=''
                           ),
                           title="Популяционная пирамида (%)",                
                           plot_bgcolor = "#111111",
                           paper_bgcolor= "#111111",
                           barmode='overlay',
                           bargap=0.1)
    
    
    data = [go.Bar(y=y,
                   x=men_bins,
                   orientation='h',
                   name='Männer',
                   hoverinfo='x',
                   marker=dict(color='powderblue')
                   ),
            go.Bar(y=y,
                   x=women_bins,
                   orientation='h',
                   name='Frauen',
                   text=-1 * women_bins.astype('int'),
                   hoverinfo='text',
                   marker=dict(color='seagreen')
                   )]
    figure = go.Figure(data=data, layout=layout)
    figure.update_layout(autosize=False, 
                         height=600, 
               font=dict(family="silom",size=14, color="Yellow"))
    figure.update_yaxes(title_text="Alter",title_font={"size": 14},
    title_standoff=5, tickfont=dict(family='silom', color='Yellow', size=12))
    figure.update_layout(title={
        'text': "Популяционная пирамида (%)",
        'y':0.99,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        font=dict(family="silom",size=18,color="Yellow"))

    return figure   

@app.callback(Output("sun_graph", "figure"), 
              Input("my-input", "value"))  

def update_sungraph(value):
    ID1=value 
    df1=df[df['ID1']==ID1]
    color_discrete_sequence=['', '#FFAA00', '#00BFFF', '#2D5F91','#819FBD','#819FBD','#91D4D2', '#96BEE6', '#C0D8F0','#E8655F','#F1A39F','#48B7B4']

    fig = px.sunburst(df1, path=["IDNAME", "POP"])
 
    figure =go.Figure(go.Sunburst(
                    labels=fig['data'][0]['labels'].tolist(),
                    parents=fig['data'][0]['parents'].tolist(),
                    marker=dict(colors=color_discrete_sequence)  #funktioniert nicht!   
                  )
                )

    figure.update_layout(title={
                'text': "Популяция по территориям",
                'y':0.99,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
                font=dict(family="silom",size=18,color="Yellow"),         
                height=600,
                margin = dict(t=0, l=50, r=0, b=0), 
                plot_bgcolor = "#111111",
                paper_bgcolor= "#111111")
      
    return figure

#Median    
@app.callback(Output('median_age_graph', 'figure'),
              Input("my-input", "value"))  

def plot_median_age(value):
    value='Afghanistan,Afghanistan,Kazakhstan,Germany,Japan,United States,Uzbekistan'
    countries = value.split(",") 
    print(countries)
    dfM = age_df[age_df['country'].isin(countries)]
    return {
        'data': [go.Scatter(x=age_df['country'],
                            y=age_df['median_age_total'],
                            mode='markers',
                            showlegend=False,
                            legendgroup='one',
                            name='',
                            hoverlabel={'font': {'size': 20}},
                            marker={'color': '#bbbbbb'})] +
                [go.Scatter(x=dfM[dfM['country']==c]['country'],
                            y=dfM[dfM['country']==c]['median_age_total'],
                            mode='markers',
                            marker={'size': 15},
                            hoverlabel={'font': {'size': 20}},
                            name=c)
                 for c in sorted(countries)],
                        'layout': go.Layout(title={
                            'text': 'Возрастная медиана по странам: ' + ', '.join(countries),                
                            'y':0.99,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'},
                                         xaxis={
                                   #'title': 'Countries', 
                                   'zeroline': False, 
                                   'showticklabels': False},
                            yaxis={
                                  'zeroline': False},
                            paper_bgcolor="#111111",
                            plot_bgcolor="#111111",
                            height=600, 
                            font=dict(family="silom",
                                      size=18, 
                                      color="Yellow")
       ),
    }
    
@app.callback(Output('age_graph', 'figure'),
             Input("my-input", "value"))   
              
def plot_countries(value):
    value='Afghanistan,Afghanistan,Kazakhstan,Germany,Japan,United States,Uzbekistan'
    countries = value.split(",") 
    print(countries)
    dfM = age_df[age_df['country'].isin(countries)]
          
    return {
        'data': [go.Bar(x=age_categories,
                        y=[0 for i in range(len(age_categories))],
                        showlegend=False,
                        width=0.1,
                        hoverinfo='none')] +
                
                [go.Bar(x=age_categories,
                        y=dfM.iloc[x, 2:7],
                        name=dfM.iloc[x, 0],
                        text=dfM.iloc[x, 2:7].astype(str) + '%',
                        hoverinfo='name+y',
                        textposition='inside',
                        textfont={'color': 'Yellow'})
                 for x in range(len(dfM))],
        'layout': go.Layout(title={
                            'text': 'Возрастное (%) распределение по странам: ' + ', '.join(countries),                
                            'y':0.99,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'},
                            xaxis={}, 
                            yaxis={}, 
                            barmode='group',
                              #color='y',
                              #color_discrete_sequence=go.colors.sequential.Viridis,
                            plot_bgcolor="#111111",
                            paper_bgcolor="#111111",
                            height=600, 
                            font=dict(family="silom",
                                      size=18, color="Yellow")
                           )
        
    }    

@app.callback(Output('graph_close', 'figure'), 
             Input("my-input", "value")) 

def drawPropeth(value):
    #from pandas_datareader import data, wb
    trace_line = go.Scatter(x=list(df_stock.ds),
                                y=list(df_stock.y),
                                name="Aktual",
                                showlegend=True)
   
    pred_line = go.Scatter(x=list(df_pred.ds),
                                y=list(df_pred.yhat_upper),
                                name="Prediction",
                                showlegend=True)
    data = [trace_line, pred_line] 
     
    layout = dict(
        height=500,
        autosize=False,
        plot_bgcolor="#111111",
        paper_bgcolor="#111111",
        legend=dict(x=0.95, y=0.99,
            traceorder="normal",
            title='Aktual & Prognose',
            font=dict(family="silom", size=14, color="yellow"),
            bgcolor='#111111',
            bordercolor='#FFFFFF',
            borderwidth=2
        ),   
        
        yaxis=dict(
        title='Общая заболеваемость',
        titlefont=dict(
            family='silom"',
            size=12,
            color='yellow'
        ),
        showticklabels=True,
        tickfont=dict(
            family='Old Standard TT, serif',
            size=12,
            color='yellow'
        ),
      ),
         
        xaxis=dict(
            showticklabels=True,
            tickfont=dict(
                family='Old Standard TT, serif',
                size=12,
                color='yellow'
            ),
            
            showgrid=True, 
            gridcolor='rgb(255, 255, 255)',
            gridwidth=1,       
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label='1m',
                         step='month',
                         stepmode='backward'),
                    dict(count=6,
                         label='6m',
                         step='month',
                         stepmode='backward'),
                    dict(count=1,
                         label='YTD',
                         step='year',
                         stepmode='todate'),
                    dict(count=1,
                         label='1y',
                         step='year',
                         stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(visible=True),
            type='date'
        ) 
    )
    return {"data": data, "layout": layout}

@app.callback(
    Output(component_id='my-graph1', component_property='children'),
    Output("my-input", "value"),
    Input(component_id='map_plot1', component_property='clickData'))

def update_graph(clickData):
    if clickData:
        city = clickData['points'][0]['hovertext']
        print("city: ", city)
        value=city
        print("value: ", value)              
        land = country[country['ID'] == city]
  
        fig1 = px.bar(land,  x='year', y="pop", 
            orientation= 'v',
            height=300,                     
            color = "pop", hover_data={'pop': False},
            labels=dict(y="Anzahl", x="Year"), 
     
        color_discrete_sequence = px.colors.sequential.Plasma_r).update_layout(
        font=dict(family="silom",
                   size=14, 
                   color="Yellow"),
        plot_bgcolor = "#111111",
        paper_bgcolor= "#111111")
         
        fig1.update_xaxes(tickangle=45, title_text="Territorium",title_font={"size": 14},
        title_standoff=5, tickfont=dict(family='silom', color='Yellow', size=12))
        fig1.update_yaxes(title_text="Anzahl",title_font={"size": 12},title_standoff=5)
        
        fig1.update_layout(title={
            'y':0.99,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
            font=dict(family="silom",size=18,color="Yellow"))
        return dcc.Graph(figure=fig1), value   
 
 
@app.callback(Output("my-graph1", "figure"),
              [Input('dropdown', 'value')])
              
def FigureStart(value):
    print("FigureStart wurde gestartet!")
    Tsummy = Tod_summy[Tod_summy['GR'] == value]
    Tsummy = Tsummy[Tsummy['F1'] != 'All'] 
    Tsummy.head() 
    
    land = Tsummy 
    print(land)
    print("FigureStart Finisch!")
       
    figure = px.bar(land,  x='F1', y="SUMM", 
    title="Распределение смертности население в 2022г. по МКБ-10",             
    orientation= 'v',
    height=605,                     
    color = "SUMM", hover_data={'SUMM': False},
    text='SUMM',                    
    labels=dict(y="Количество", x="МКБ-10"), 
        
    color_discrete_sequence = px.colors.sequential.Plasma_r).update_layout(
    font=dict(family="silom",
               size=18, 
               color="Yellow"),
    plot_bgcolor = "#111111",
    paper_bgcolor= "#111111")
     
    figure.update_xaxes(tickangle=45, title_text="МКБ-10",title_font={"size": 18},
    title_standoff=5, tickfont=dict(family='silom', color='Yellow', size=14))
    figure.update_yaxes(title_text="Количество",title_font={"size": 18},title_standoff=5)
    
    figure.update_layout(title={
        'y':0.99,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        font=dict(family="silom",size=18,color="Yellow"))
    return figure   
              
              

@app.callback(Output("my-graph5", "figure"),
              Input("my-input", "value"))

def FigureBarTable5(value):
    print("FigureBarTable5 wurde gestartet!")
    ID1=value 
    land = country[country['ID'] == ID1]
    print("Value", ID1)
    #print(land)
    figure = px.bar(land,  x='year', y="pop", 
    title="Распределение население области по годам за период 1990-2021",             
    orientation= 'v',
    height=600,                     
    color = "pop", hover_data={'pop': False},
    text='pop',                    
    labels=dict(y="Количество", x="Год"), 
        
    color_discrete_sequence = px.colors.sequential.Plasma_r).update_layout(
    font=dict(family="silom",
               size=18, 
               color="Yellow"),
    plot_bgcolor = "#111111",
    paper_bgcolor= "#111111")
     
    figure.update_xaxes(tickangle=45, title_text="Год",title_font={"size": 18},
    title_standoff=5, tickfont=dict(family='silom', color='Yellow', size=14))
    figure.update_yaxes(title_text="Количество",title_font={"size": 18},title_standoff=5)
    
    figure.update_layout(title={
        'y':0.99,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        font=dict(family="silom",size=18,color="Yellow"))
    return figure   

@app.callback([Output(component_id='table-year', component_property='data'), 
               Output(component_id='table-year', component_property='columns')],
              [Input("my-input", "value")])

def update_table(value ):
    print("FigureBarTable5 wurde gestartet!")
    ID1=value 
    land = country[country['ID'] == ID1]
    print("Value", ID1)
    columns = [{'name': col, 'id': col} for col in land.columns]
    data = land.to_dict(orient='records')
    return data, columns

@app.callback([Output(component_id='table2122', component_property='data'), 
               Output(component_id='table2122', component_property='columns')],
              [Input("my-input", "value")])

def update_table(value ):
    print("FigureBarTable5 wurde gestartet!")
    ID1=value 
    land = allpop
    print("Value", ID1)
    columns = [{'name': col, 'id': col} for col in land.columns]
    data = land.to_dict(orient='records')
    return data, columns

@app.callback([Output(component_id='tod2022', component_property='data'), 
               Output(component_id='tod2022', component_property='columns')],
              [Input('dropdown', 'value')]) 

def update_table1(value ):     
    land = tod2022[tod2022['GR'] == value]
    land.drop(['GR'], axis=1, inplace=True)
    columns = [{'name': col, 'id': col} for col in land.columns]
    data = land.to_dict(orient='records')
    style_data={
         'whiteSpace': 'normal',
         'height': 'auto',
    },
    fill_width=False 
    return data, columns

@app.callback(Output("my-graph6", "figure"),
              [Input('mkb', 'value')])

def FigureTod1(value):
    land = tod1[tod1['F1'] == value] 
    print(land)
    
    figure = px.bar(land,  x='AGE', y="Count",
    barmode="group",                 
    title="Распределение смертности по возрасту, полу и MKB-10",             
    orientation= 'v',
    height=605,                     
    hover_data={'Count': False},
    text='Count',                    
    labels=dict(y="Количество", x="Boзраст"), 
    color="GR",    
    ).update_layout(
    font=dict(family="silom",
               size=18, 
               color="Yellow"),
    plot_bgcolor = "#111111",
    paper_bgcolor= "#111111")
     
    figure.update_xaxes(tickangle=45, title_text="Возраст",title_font={"size": 18},
    title_standoff=5, tickfont=dict(family='silom', color='Yellow', size=14))
    figure.update_yaxes(title_text="Количество",title_font={"size": 18},title_standoff=5)
    
    figure.update_layout(title={
        'y':0.99,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        font=dict(family="silom",size=18,color="Yellow"))
    return figure 
#######################################################################

if __name__ == '__main__':
    app.run(debug=True)
