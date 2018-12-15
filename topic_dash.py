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

topics =  pd.read_csv('https://raw.githubusercontent.com/TheFedExpress/data608-final/master/coords.csv')
def get_pages():
    return pd.read_csv('https://raw.githubusercontent.com/TheFedExpress/data608-final/master/ticker_pages.csv')

test_phrase = [html.P('this is a test'),
    html.Span('I really hope', style = {'color': 'red'}), html.P( 'it works')]

def company_list():
    cos = get_cos()
    return cos.drop_duplicates('ticker')

def get_cos ():
        return pd.read_csv('https://raw.githubusercontent.com/TheFedExpress/data608-final/master/company_topics.csv')
    
def get_topics():
    return pd.read_csv('https://raw.githubusercontent.com/TheFedExpress/data608-final/master/top_words.csv')
def get_pcts():
    return pd.read_csv('https://raw.githubusercontent.com/TheFedExpress/data608-final/master/company_pct.csv')

def word_graph(word_probs, topic):
    figure={
            'data': [go.Bar(x = word_probs['word'], y = word_probs['saliency']),],
             
            'layout': {
                'title': 'Topic "{}"'.format(topic) + 'Word Probabilities'
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
                        text = co_tops['ticker']
                    )],
             
            'layout': {
                'title': 'Topic "{}"'.format(topic) + 'Companies'
            }
        }
    return figure

side_style = {
    'height': '20%',
    'width': '20%',
    'position': 'fixed',
    'z-index': 1,
    'top': 0,
    'left': 0,
    'background-color': '#eee',
    'overflow-x': 'hidden',
    'padding-top': '20px',
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

graph_4_style = {'height': '50%', 'width': '35%', 'top': 0, 'padding-top': '10px', 
                 'position' : 'absolute', 'margin': '30%'}

raw_style = { 
    'height' : '50%', 'width': '40%', 'bottom' : 0, 'left' : 0 , 'padding-left': '10px',
    'position': 'absolute'}

dd_style = {'width' : '20%', 'right': 0, 'top': 0, 'position': 'absolute'}

app = dash.Dash(__name__)
app.config['suppress_callback_exceptions'] = True

app.layout = html.Div(children = [
    dcc.Tabs(id="tabs-example", style = side_style, value='tab1', children=[
        dcc.Tab(label='Tab One', value='tab1'),
        dcc.Tab(label='Tab Two', value='tab2'),
    ]),
    html.Div(id='tabs-content-example')
])

@app.callback(Output('tabs-content-example', 'children'),
              [Input('tabs-example', 'value')])

def render_tabs(tabname):
    if tabname == 'tab1': 
        return html.Div(children=[
            
                html.Div(style = graph_style, children=[
                    dcc.Graph(
                            id='topic_explorer', style = graph_2_style,clickData={'points': [{'hoverinfo': 0, 
                                                                                              'text': 'topic'}]},
                            
                        figure={
                                'data': [go.Scatter(
                                        x = topics['pc1'], 
                                        y = topics['pc2'],
                                        mode = 'markers',
                                        marker={'color': 'blue', 'size': topics['ticker']},
                                        text = topics['Topic'],
                                        hoverinfo = topics['top_num'],
                                        
                                    )],
                                         
                                'layout': {
                                    'title': 'Topic Explorer'
                                }
                            }
        
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
                        options = [{'label' : row['ticker'], 'value' : row['ticker']} 
                            for index, row in company_list().iterrows()],
                        value =  'AAPL',
                        style = dd_style
                        ),
                       dcc.Graph(id = 'company_break', style = graph_4_style),
                       html.Div(test_phrase, id = 'raw_text', style = raw_style)
                   ])
                
    
def topic_exlorer():
    import pandas as pd
    topics =  pd.read_csv('https://raw.githubusercontent.com/TheFedExpress/data608-final/master/coords.csv')
    figure={
            'data': [go.Scatter(
                    x = topics['pc1'], 
                    y = topics['pc2'],
                    mode = 'markers',
                    marker={'color': 'blue', 'size': topics['ticker'], 'symbol': 104},
                    text = topics['Topic']
                )]
, 
            'layout': {
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
            'data': [go.Pie(labels = df['topic'], 
                           values = df['percentage'],
                           hoverinfo = 'label+percent',
                           text = df['topic']
                           
                    )]
        }
    return figure


@app.callback(
        Output('raw_text', 'children'),
        [Input('company_break', 'clickData'),
         Input('dd', 'value')
         ]
    )

def highlight_text(clickData, value):
    print(clickData)
    
    pages = get_pages ()
    topics = get_topics()
    
    topic = int(clickData['points'][0]['label'])
    page = pages.loc[pages.ticker == value, 'page'].values
    
    top_words = topics.loc[topics.top_num == topic, 'word'].values
    
    new_words = page[0].split()        
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