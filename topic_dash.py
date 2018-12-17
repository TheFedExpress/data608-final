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


connection = MongoClient('ds135714.mlab.com', 35714)
db = connection['data608-final']
db.authenticate('pgoodridge2007', 'Cunydata1')

def company_list():
    cos = get_cos()
    return cos.drop_duplicates('ticker')

def get_cos ():
        return pd.read_csv('https://raw.githubusercontent.com/TheFedExpress/data608-final/master/company_topics.csv')
    
def get_topics():
    return pd.read_csv('https://raw.githubusercontent.com/TheFedExpress/data608-final/master/top_words.csv')
def get_pcts():
    return pd.read_csv('https://raw.githubusercontent.com/TheFedExpress/data608-final/master/company_pct.csv')
topics =  pd.read_csv('https://raw.githubusercontent.com/TheFedExpress/data608-final/master/coords.csv')


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
                 'position': 'absolute'}
graph_3_style = {'height': '65%', 'width': '25%', 'bottom': 0, 'left':0, 'padding-top': '10px', 
                 'position' : 'absolute'}

graph_4_style = {'height': '50%', 'width': '35%', 'top': '60px',
                 'margin-left':'45%',
                 'position' : 'absolute'}

raw_style = {
        'border': 'thin lightgrey solid',
        'overflowY': 'scroll',
  
    'height' : '70%', 'width': '40%', 'bottom' : '0px', 'left' : '0px' , 'padding-left': '10px',
    'position': 'absolute'}

dd_style = {'width' : '50%', 'right': '0px', 'top': '0px', 'position': 'absolute', 'padding-top': '5px'}
sector_title = {'width' : '30%', 'left': '0px', 'top': '75px', 'position': 'absolute', 'padding-top': '5px'}

sector_style = {'width' : '30%', 'left': '0px', 'top': '75px', 'position': 'absolute', 'padding-top': '5px'}


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

app = dash.Dash(__name__)
app.config['suppress_callback_exceptions'] = True

app.layout = html.Div(children = [
    dcc.Tabs(id="tabs_input", style = side_style, value='tab1', children=[
        dcc.Tab(label='Topics', value='tab1', style =  tab_style, selected_style = tab_selected_style),
        dcc.Tab(label='Companies', value='tab2', style = tab_style, selected_style = tab_selected_style),
    ]),
    html.Div(id='tabs_content')
])

@app.callback(Output('tabs_content', 'children'),
              [Input('tabs_input', 'value')])

def render_tabs(tabname):
    if tabname == 'tab1': 
        return html.Div(children=[
                html.H4('Choose Color Scale:', style = sector_title),
                dcc.Dropdown(
                        id = 'sector', 
                        options = [{'label' : 'Market Cap', 'value': 'Market Cap'},
                                   {'label' : 'Sector', 'value': 'Sector'}
                                  ],
                        value = 'Market Cap',
                        style = sector_style
                                    
                ),
                html.Div(style = graph_style, children=[
                    dcc.Graph(
                            id='topic_explorer', style = graph_2_style,
                            clickData={'points': [{'hoverinfo': 32, 
                            'text': 'softwar'}]},
                    ),
                    dcc.Graph(id='word_probs', style = graph_1_style ),
                    dcc.Graph(id = 'company_score', style = graph_3_style, clickData={'points': [{ 'text': 'AAPL'}]})
                ])
                     
            ]) 
    elif tabname == 'tab2':
       return  html.Div(children=[
                   html.H4('Choose a Company:'),
                        dcc.Dropdown(
                        id = 'dd',
                        options = [{'label' : row['Name'], 'value' : row['ticker']} 
                            for index, row in company_list().iterrows()],
                        value =  'AAPL',
                        style = dd_style
                        ),
                       dcc.Graph(id = 'company_break', style = graph_4_style,
                                 clickData={'points': [{ 'label': '32'}]}),
                       html.Div(style = raw_style, children = [ 
                           html.H2('10-K Excerpt (topic words in bold)'),
                           html.P(id = 'raw_text')
                          ])
                   ])

@app.callback(Output('topic_explorer', 'figure'),
              [Input('sector', 'value')])

def topic_exlorer(value):
    import pandas as pd
    topics =  pd.read_csv('https://raw.githubusercontent.com/TheFedExpress/data608-final/master/coords.csv')
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
                            'colorbar' :{'title': 'Market Cap'},
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
        for sector in topics['Sector'].drop_duplicates().values:
            data = go.Scatter(
                    x = topics.loc[topics.Sector == sector, :]['pc1'], 
                    y = topics.loc[topics.Sector == sector, :]['pc2'],
                    mode = 'markers',
                    name = sector,
                    marker={
                            
                            'size': topics.loc[topics.Sector == sector, :]['percentage'],
                            'sizemode' : 'area',
                            'sizeref': 2.*max(topics.loc[topics.Sector == sector, :]['percentage'])/(40.**2),
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
    topic_df = get_topics()
    topic = clickData['points'][0]['hoverinfo']
    name = clickData['points'][0]['text']
    topic_words = topic_df.loc[topic_df.top_num == topic, :].sort_values(by = 'saliency')
    figure = word_graph(topic_words, name)
    return figure

@app.callback(
        Output('company_score', 'figure'),
        [Input('topic_explorer', 'clickData')]
    )


def update_cos(clickData):
    company_df = get_cos()
    topic = clickData['points'][0]['hoverinfo']
    name = clickData['points'][0]['text']
    company_topics = company_df.loc[
            company_df.topic == topic, :].sort_values(by = 'percentage', ascending = False)
    rows = len(company_topics.index)
    company_topics = company_topics.head(min(15, rows))
    
    figure = company_portions(company_topics, name)
    return figure 

@app.callback(
        Output('company_break', 'figure'),
        [Input('dd', 'value')]
    )      

def pie_graph(value):
    df = get_pcts()
    df = df.loc[df['ticker'] == value, :]
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
    
    topics = get_topics()
    topic = int(clickData['points'][0]['label'])
    page = db.pages.find_one({'ticker' : value})['page']
    
    top_words = topics.loc[topics.top_num == topic, 'word'].values
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


if __name__ == '__main__':
    app.run_server()