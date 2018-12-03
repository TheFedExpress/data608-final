# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 16:02:43 2016

@author: peter_goodridge
"""

import json 
import os
from all_words import grams, get_stops
from nltk.stem.snowball import SnowballStemmer
import re

def load_pages():
    stemmer = SnowballStemmer('english')
    pages = []
    tickers = []
    combos2, combos3 = grams()
    stop_words = get_stops()

    for root,dirs,files in os.walk('Pages'):
        for file in files:
            page_words = []
            
            file_name = os.path.join('pages', file)
            f=open(file_name, 'r')
            try:
               d = json.load(f)
               ticker = d['company']
            except UnicodeDecodeError:
               print("Problem with a file")
            except TypeError:
               print("problem with a file")
            raw_page = d['page'].lower()
            for combo2 in combos2:
               two_word = combo2.split()
               joiner = "_"
               two_base = joiner.join(two_word)
               raw_page = raw_page.replace(combo2, two_base)
            for combo3 in combos3:
               three_word = combo3.split()
               joiner = "_"
               three_base = joiner.join(three_word)
               raw_page = raw_page.replace(combo3, three_base)
            words = raw_page.lower().split()
            for word in words:
                stemmed_word = re.sub('\W+', '', stemmer.stem(word))
                if word not in stop_words and stemmed_word not in stop_words:
                    page_words.append(stemmed_word)

            f.close()
            if len(page_words) > 10:
                   pages.append(page_words)
                   tickers.append(ticker)
    return pages, tickers

