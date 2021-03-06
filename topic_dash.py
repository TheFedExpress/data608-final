# -*- coding: utf-8 -*-
"""
Created on Mon Dec 10 18:10:55 2018

@author: pgood
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import json
from dash.dependencies import Input, Output
import pandas as pd
from tab1 import render_tab1
from pymongo import MongoClient
import dash_table

connection = MongoClient('ds135714.mlab.com', 35714)
db = connection['data608-final']
db.authenticate('pgoodridge2007', 'Cunydata1')

def company_list():
    cos = get_cos()
    return cos.drop_duplicates('ticker')

def get_cos ():
        return pd.read_csv('https://raw.githubusercontent.com/TheFedExpress/data608-final/master/company_topics.csv')
    


def word_graph(word_probs, topic):
    figure={
            'data': [go.Bar(x = word_probs['word'], y = word_probs['saliency'],
                             marker = {'color':'rgba(55, 128, 191, 0.7)'}
                            )],
             
            'layout': {
                'title': 'Topic "{}" '.format(topic) + 'Word Relevance'
            }
        }
    return figure

def company_portions(co_tops, topic):
    figure={
            'data': [
                    go.Bar(
                        y = co_tops['ticker'], 
                        x = co_tops['percentage'],
                        orientation  = 'h',
                        text = co_tops['Name'],
                        marker = {'color':'rgba(55, 128, 191, 0.7)'}
                    )],
             
            'layout': {
                'xaxis': {'tickformat': ',.0%',  'range': [0,1]},
                'title': 'Topic "{}" '.format(topic) + 'Companies'
            }
        }
    return figure

side_style = {
    'height': '8%',
    'width' : '15%',
    'position': 'absolute',
    'z-index': 1,
    'top': 0,
    'left': 0,
    'padding-top': '10px',
}

graph_style = {
    'margin-left': '20%',
    'padding': '0px 10px'
}

graph_2_style = {'height': '65%', 'width': '70%', 'top' : 0,'padding-top': '20px',
                 'position' : 'absolute'}
graph_1_style = {'height': '35%', 'width': '70%',  'bottom': 0, 'padding-top': '10px', 
                 'padding-left': '10px', 'position': 'absolute'}
graph_3_style = {'height': '65%', 'width': '25%', 'bottom': 0, 'left':0, 'padding-top': '10px', 
                 'position' : 'absolute'}

graph_4_style = {
    'bottom': 0,
    'margin-left':'45%',
    'position' : 'absolute'
}

raw_style = {
        'border': 'thin lightgrey solid',
        'overflowY': 'scroll',
  
    'height' : '80%', 'width': '40%', 'bottom' : '0px', 'left' : '0px' , 'padding-left': '10px',
    'position': 'absolute'}

dd_style = {'width' : '50%', 'right': '0px', 'top': '0px', 'position': 'absolute', 'padding-top': '5px'}
sector_title = {'width' : '30%', 'left': '0px', 'top': '75px', 'position': 'absolute', 'padding-top': '5px'}

sector_style = {'width' : '20%', 'left': '0px', 'top': '120px', 'position': 'absolute', 'padding-top': '5px'}


tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}

table_style = {
    'top': '120px',
    'right': '15px',
    'position' : 'absolute'
}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'    ]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True

app.layout = html.Div(children = [
        html.Div(style = side_style, children = [
                html.H3('10-K Miner'),
                dcc.Tabs(id="tabs_input", value='tab1', children=[
                dcc.Tab(label='Topics', value='tab1', style =  tab_style, selected_style = tab_selected_style),
                dcc.Tab(label='Companies', value='tab2', style = tab_style, selected_style = tab_selected_style)
        ])
    ]),
    html.Div(id='tabs_content')
])

@app.callback(Output('tabs_content', 'children'),
              [Input('tabs_input', 'value')])

def render_tabs(tabname):
    
    raw = []
    docs = db.coords.find()
    for item in docs:
        raw.append(item)
    
    topics =  pd.DataFrame(raw)
    
    best_top = topics.sort_values('percentage').tail(1)
    best_num = best_top['top_num'].values[0]
    best_name = best_top['topic'].values[0]
    
    cos_raw = []
    docs = db.company_pct.find()
    for item in docs:
        cos_raw.append(item)
    
    cos =  pd.DataFrame(cos_raw).sort_values('MarketCap').tail(1)
    best_co = cos['ticker'].values[0]
    cos = cos[['Name', 'MarketCap', 'Sector', 'IPOyear']]
    co_vals = cos.to_dict("rows")
    cols = [{"name": i, "id": i} for i in cos.columns]
    
    
    if tabname == 'tab1': 
        return html.Div(children=[
                html.Div(style = sector_style, children = [ 
                    html.H5('Choose Color Scale:'),
                    dcc.Dropdown(
                            id = 'sector', 
                            options = [{'label' : 'Market Cap', 'value': 'Market Cap'},
                                       {'label' : 'Sector', 'value': 'Sector'}
                                      ],
                            value = 'Market Cap',
                    )]
                ),
                html.Div(style = graph_style, children=[
                    dcc.Graph(
                            id='topic_explorer', style = graph_2_style,
                            clickData={'points': [{'hoverinfo': best_num, 
                            'text': best_name}]},
                    ),
                    dcc.Graph(id='word_probs', style = graph_1_style ),
                    dcc.Graph(id = 'company_score', style = graph_3_style)
                ])
                     
            ]) 
    elif tabname == 'tab2':
       return  html.Div(children=[
                        dcc.Dropdown(
                            id = 'dd',
                            options = [{'label' : row['Name'], 'value' : row['ticker']} 
                                for index, row in company_list().iterrows()],
                            value =  best_co,
                            style = dd_style
                        ),
                       dcc.Graph(id = 'company_break', style = graph_4_style,
                                 clickData={'points': [{ 'label': '7'}]}),
                       html.Div(style = raw_style, children = [ 
                           html.H2('10-K Excerpt (topic words in bold)'),
                           html.P(id = 'raw_text')
                          ]),
                        html.Div(
                                 id = 'table', style = table_style
                            )

                   ])

@app.callback(Output('topic_explorer', 'figure'),
              [Input('sector', 'value')])

def topic_exlorer(value):
    import pandas as pd
    import numpy as np
    
    raw = []
    docs = db.coords.find()
    for item in docs:
        raw.append(item)
    
    topics =  pd.DataFrame(raw)
    
    
    raw_vals = topics['share'].quantile([i/4 for i in range(5)])
    caps = np.exp(topics['share']).quantile([i/4 for i in range(5)])
    labs = ['${:,.0f}'.format(float('{:,.1g}'.format(num))) for num in caps.values]

    if value == 'Market Cap':
        figure={
            'data': [go.Scatter(
                    x = topics['pc1'], 
                    y = topics['pc2'],
                    mode = 'markers',
                    marker={
                            'color': topics['share'], 
                            'size': topics['percentage'],
                            'sizemode' : 'area',
                            'sizeref': 2.*max(topics['percentage'])/(40.**2),
                            'sizemin': 4,
                            'colorbar' :{'title': 'Market Cap', 'tickmode': 'array',
                                         'tickvals': raw_vals,
                                         'ticktext': labs
                                         },
                            'colorscale': 'Viridis'
                    },
                    text = topics['topic'],
                    hoverinfo = topics['top_num']
                    
                )],
                     
            'layout': {
                'xaxis': {'showticklabels' :False},
                'yaxis': {'showticklabels' :False},
                'title': 'Topic Explorer'
            }
        }
    elif value == 'Sector':
        traces = []
        #2.*max(topics.loc[topics.Sector == sector, :]['percentage'])/(40.**2)
        sizeref = 2.*max(topics['percentage'])/(40.**2)
        for sector in topics['Sector'].drop_duplicates().values:
            data = go.Scatter(
                    x = topics.loc[topics.Sector == sector, :]['pc1'], 
                    y = topics.loc[topics.Sector == sector, :]['pc2'],
                    mode = 'markers',
                    name = sector,
                    marker={
                            
                            'size': topics.loc[topics.Sector == sector, :]['percentage'],
                            'sizemode' : 'area',
                            'sizeref': sizeref,
                            'sizemin': 4,
                    },
                    text = topics.loc[topics.Sector == sector, :]['topic'],
                    hoverinfo = topics.loc[topics.Sector == sector, :]['top_num']
                )
            traces.append(data)
        figure={
            'data': traces,
                     
            'layout': {
                'xaxis': {'showticklabels' :False},
                'yaxis': {'showticklabels' :False},
                'title': 'Topic Explorer'
            }
        }

    return figure


@app.callback(
        Output('word_probs', 'figure'),
        [Input('topic_explorer', 'clickData')]
        )


def update_word_probs(clickData):
    
    #topic_df = get_topics()
    topic = clickData['points'][0]['hoverinfo']
    name = clickData['points'][0]['text']
    
    raw = []
    docs = db.top_words.find({'top_num' : topic})
    for item in docs:
        raw.append(item)
    topic_words = pd.DataFrame(raw)

   
    #topic_words = topic_df.loc[topic_df.top_num == topic, :].sort_values(by = 'saliency')
    figure = word_graph(topic_words, name)
    return figure

@app.callback(
        Output('company_score', 'figure'),
        [Input('topic_explorer', 'clickData')]
    )


def update_cos(clickData):
    
    #company_df = get_cos()
    topic = clickData['points'][0]['hoverinfo']
    name = clickData['points'][0]['text']  
    
    raw = []
    docs = db.company_pct.find({'top_num' : topic})
    for item in docs:
        raw.append(item)
        
    df = pd.DataFrame(raw)
    df.sort_values(by = 'percentage', inplace = True, ascending = False)

    #company_topics = company_df.loc[
    #       company_df.topic == topic, :].sort_values(by = 'percentage', ascending = False)
    
    rows = len(df.index)
    company_topics = df.head(min(15, rows))
    
    figure = company_portions(company_topics, name)
    return figure 

@app.callback(
        Output('company_break', 'figure'),
        [Input('dd', 'value')]
    )      

def pie_graph(value):
    
    raw = []
    docs = db.company_pct.find({'ticker' : value})
    for item in docs:
        raw.append(item)
        
    df = pd.DataFrame(raw)
    #df = get_pcts()
    #df = df.loc[df['ticker'] == value, :]
    
    
    figure = {
            'data': [go.Pie(labels = df['top_num'], 
                           values = df['percentage'],
                           hoverinfo = 'text+percent',
                           text = df['topic']
                           
                    )],
            'layout': {
                'title': '{} Topic Breakdown'.format(value),
                'showlegend': False
            }
        }
    return figure


@app.callback(
        Output('raw_text', 'children'),
        [Input('company_break', 'clickData'),
         Input('dd', 'value')
         ]
    )

def highlight_text(clickData, value):
    
    
    topic = int(clickData['points'][0]['label'])
    page = db.pages.find_one({'ticker' : value})['page']
    
    top_words = []
    docs = db.top_words.find({'top_num': topic})
    for item in docs:
        top_words.append(item['word'])
    #top_words = topics.loc[topics.top_num == topic, 'word'].values
    new_words = page.split()
    """
    children = []
    for word in new_words:
        if word in top_words:
            children.append(html.Span(word, style = {'color': 'red'}))
        else:
            children.append(html.P(word))
    """
    my_string = ''
    for word in new_words:
        if word in top_words:
            my_string += '**{}**'.format(word) + ' '
        else:
            my_string += word + ' '
    
    return dcc.Markdown(my_string)


@app.callback(
        Output('table', 'children'),
        [Input('dd', 'value')]
    )

def generate_table(value):
    raw = []
    docs = db.company_pct.find({'ticker' : value})
    for item in docs:
        raw.append(item)
    df =  pd.DataFrame(raw)[['Sector', 'Industry', 'MarketCap', 'IPOyear']].head(1)
    df['MarketCap'] = df['MarketCap'].map('${:,.2f}'.format)
    
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in df.columns])] +

        # Body
        [html.Tr([
            html.Td(df.iloc[i][col]) for col in df.columns
        ]) for i in range(len(df))]
    )

if __name__ == '__main__':
    app.run_server()