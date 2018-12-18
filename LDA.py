# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 10:14:31 2016

@author: peter_goodridge
"""

from sklearn import manifold
from six import iteritems
import numpy as np
from pages_load import load_pages
from gensim import corpora, models
from scipy.stats import entropy
from scipy.spatial.distance import pdist, squareform
import pandas as pd

co_list = pd.read_csv('companylist.csv')

num_topics = 30
def _jensen_shannon(_P, _Q):
   _M = 0.5 * (_P + _Q)
   return 0.5 * (entropy(_P, _M) + entropy(_Q, _M))

pages, tickers = load_pages()


dictionary = corpora.Dictionary(pages)
once_ids = [tokenid for tokenid, docfreq in iteritems(dictionary.dfs) if docfreq == 1] 
commons = [tokenid for tokenid, docfreq in iteritems(dictionary.dfs) if docfreq/len(pages) > .8] 
dictionary.filter_tokens(once_ids)
dictionary.filter_tokens(commons)
dictionary.compactify()

corpus = [dictionary.doc2bow(page) for page in pages]
lda = models.LdaModel(corpus = corpus, num_topics = num_topics, id2word = dictionary,passes = 10, alpha = .0005)

output = lda.print_topics(num_topics = num_topics)
topics = [lda.get_document_topics(element) for element in corpus]

measure = []
for doc in topics:
    for tuple in doc:
        measure.append(tuple[0])
        
counts = []
for i in range(num_topics):
    count = measure.count(i)
    counts.append(count)

all_clus = []
vectors =[]
for i in range(len(topics)):
    cluster_vector = np.zeros(num_topics)
    percentage = 0
    for j in range(len(topics[i])):
        all_clus.append({"ticker": tickers[i], "top_num":topics[i][j][0], "percentage":topics[i][j][1]})
        cluster_vector[topics[i][j][0]] = topics[i][j][1]
    vectors.append(cluster_vector)
    

all_clus = pd.DataFrame(all_clus)
all_clus = all_clus.merge(co_list, left_on = 'ticker', right_on = 'Symbol')
all_clus['share'] = all_clus['percentage'] * all_clus['MarketCap']

company_totals = all_clus.groupby('top_num')['percentage', 'MarketCap', 'share'].sum()
company_totals.reset_index(inplace = True)

sectors = all_clus.groupby(['top_num', 'Sector'])['percentage'].sum().reset_index()
top_sector = sectors.sort_values('percentage', ascending = False).groupby(
        ['top_num']).head(1)[['top_num','Sector']]


##based on pyldavis source code 
tokens = dictionary.token2id.values()
tokes = [value for value in tokens]
topic = lda.state.get_lambda()
topic = topic / topic.sum(axis=1)[:, None]
fnames_argsort = np.asarray(tokes, dtype = np.int_)
topic_term_dists = topic[:,fnames_argsort]


dist_matrix = squareform(pdist(topic_term_dists, metric=_jensen_shannon))
model = manifold.MDS(n_components=2, random_state=0, metric='precomputed')
#manifold like PCA, but is a generalization to find non-linear trends
coords = model.fit_transform(dist_matrix)

all_counts = [tup for item in corpus for tup in item]
corp_counts = np.zeros(len(fnames_argsort))       
for i in range(len(all_counts)):
   corp_counts[all_counts[i][0]] += all_counts[i][1]
corp_probs = corp_counts/np.sum(corp_counts)


tws = []
top_totals = []
word_counts = []
for i in range(num_topics):
    tw = lda.show_topic(i,len(all_counts))
    top_total = 0
    for j in range(30):
        global_prob = corp_probs[dictionary.token2id[tw[j][0]]]
        score = tw[j][1]
        relevence = (score/global_prob)*.5 + score*.5
        top_dict = {"top_num": i, "word": tw[j][0], "score" : score, 
                    "global_prob": global_prob, 
                    'saliency': relevence 
                    }
        top_total += corp_counts[dictionary.token2id[tw[j][0]]] 
        tws.append(top_dict)
        word_counts.append(top_total)
    top_totals.append(top_dict)

top_words = pd.DataFrame(tws)
top_words.sort_values(by = ['top_num',  'saliency'], ascending = [True,False], inplace = True)
overall_tops = top_words.groupby('top_num').head(1)

global_probs = top_words.drop_duplicates('word').sort_values(
        by = 'global_prob', ascending = False).head(30)

global_probs['top_num'] = 0
#top_words = pd.concat([top_words, global_probs]) Just in case

coords_dicts = []
for i in range(num_topics):
    tw = lda.show_topic(i,1)
    coords_dict = {'top_num': i, 
                   "pc1": coords[i][0], 
                   "pc2" : coords[i][1],
                   'topic': overall_tops.iloc[i, 4]
                   }
    coords_dicts.append(coords_dict)

coords_df = pd.DataFrame(coords_dicts)
coords_df = coords_df.merge(company_totals, how = 'left', on = 'top_num')
coords_df.fillna(0, inplace = True)

coords_df = coords_df.merge(top_sector, how = 'left', on = 'top_num')
coords_df.fillna('No Sector', inplace = True)

coords_df['percentage'] = coords_df['percentage'].map(lambda x: max(np.log(x), 1))

coords_df['share'] = coords_df['share'].map(lambda x: max(18, np.log(x)))
#coords_df.to_csv('coords.csv')


#top_words.to_csv('top_words.csv')

all_clus = all_clus.merge(coords_df[['top_num', 'topic']], on = 'top_num')

#all_clus.to_csv('company_pct.csv')

from pymongo import MongoClient

connection = MongoClient('ds135714.mlab.com', 35714)
db = connection['data608-final']
db.authenticate('pgoodridge2007', 'Cunydata1')
db.coords.insert_many(coords_df.to_dict(orient = 'records'))
db.company_pct.insert_many(all_clus.to_dict(orient = 'records'))
db.top_words.insert_many(top_words.to_dict(orient = 'records'))