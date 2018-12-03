# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 10:14:31 2016

@author: peter_goodridge
"""

from sklearn import manifold
from sklearn.metrics import euclidean_distances
from six import iteritems
import numpy as np
from pages_load import load_pages
from gensim import corpora, models #similarities
import csv
from scipy.stats import entropy
from scipy.spatial.distance import pdist, squareform
import pandas as pd

def _jensen_shannon(_P, _Q):
   _M = 0.5 * (_P + _Q)
   return 0.5 * (entropy(_P, _M) + entropy(_Q, _M))

pages, tickers = load_pages()
pages = pages

dictionary = corpora.Dictionary(pages)
once_ids = [tokenid for tokenid, docfreq in iteritems(dictionary.dfs) if docfreq == 1] 
commons = [tokenid for tokenid, docfreq in iteritems(dictionary.dfs) if docfreq/len(pages) > .8] 
dictionary.filter_tokens(once_ids)
dictionary.filter_tokens(commons)
dictionary.compactify()

corpus = [dictionary.doc2bow(page) for page in pages]
lda = models.LdaModel(corpus = corpus, num_topics = 100, id2word = dictionary,passes = 10, alpha = .0005)

output = lda.print_topics(num_topics = 100)
topics = [lda.get_document_topics(element) for element in corpus]

measure = []
for doc in topics:
    for tuple in doc:
        measure.append(tuple[0])
        
counts = []
for i in range(100):
    count = measure.count(i)
    counts.append(count)

all_clus = []
vectors =[]
company_totals = []
for i in range(len(topics)):
    cluster_vector = np.zeros(100)
    percentage = 0
    for j in range(len(topics[i])):
        all_clus.append({"ticker": tickers[i], "topic":topics[i][j][0], "percentage":topics[i][j][1]})
        cluster_vector[topics[i][j][0]] = topics[i][j][1]
    vectors.append(cluster_vector)
    
company_totals = np.zeros(100)
for item in all_clus:
    company_totals[item["topic"]] = company_totals[item["topic"]] + item["percentage"]
    
tokens = dictionary.token2id.values()
tokes = [value for value in tokens]
topic = lda.state.get_lambda()
topic = topic / topic.sum(axis=1)[:, None]
fnames_argsort = np.asarray(tokes, dtype = np.int_)
topic_term_dists = topic[:,fnames_argsort]


dist_matrix = squareform(pdist(topic_term_dists, metric=_jensen_shannon))
model = manifold.MDS(n_components=2, random_state=0, metric='precomputed')
coords = model.fit_transform(dist_matrix)

all_counts = [tup for item in corpus for tup in item]
corp_counts = np.zeros(len(fnames_argsort))       
for i in range(len(all_counts)):
   corp_counts[all_counts[i][0]] += all_counts[i][1]
corp_probs = corp_counts/np.sum(corp_counts)


tws = []
top_totals = []
for i in range(100):
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
    top_totals.append(top_dict)
    
my_df = pd.DataFrame(tws)
my_df.sort_values(by = ['top_num',  'saliency'], ascending = False, inplace = True)
overall_tops = my_df.groupby('top_num').head(1)
    
coords_dicts = []
for i in range(100):
    tw = lda.show_topic(i,1)
    coords_dict = {"pc1": coords[i][0], "pc2" : coords[i][1],'Topic': overall_tops.iloc[i, 4], 
                   "ticker": company_totals[i]
                   }
    coords_dicts.append(coords_dict)

keys = ["ticker", "topic", "percentage"]
with open("my_skills.csv", "w", newline = '') as a:
    dictwriter=csv.DictWriter(a,fieldnames = keys)
    dictwriter.writeheader()
    dictwriter.writerows(all_clus)

keys = ["top_num", "word", "score", "global_prob", 'saliency' ]
with open("top_words.csv", "w", newline = '') as a:
    dictwriter=csv.DictWriter(a,fieldnames = keys)
    dictwriter.writeheader()
    dictwriter.writerows(tws)
    
keys = ["pc1", "pc2", "Topic", "ticker"]
with open("coords.csv", "w", newline = '') as file:
    dictwriter =  csv.DictWriter(file, fieldnames = keys)
    dictwriter.writeheader()
    dictwriter.writerows(coords_dicts)
    
