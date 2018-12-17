# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

def get_stops():
    stop_words = set({"i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", 
        "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its",
        "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this",
        "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", 
        "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", 
        "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", 
        "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", 
        "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", 
        "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", 
        "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", 
        "now" 'consultant', 'consult', 'include' ,'provide', 'service' ,'company', 'perform',
       'service', 'prepare', 'nj', 'plan', 'work', 'client', 'submittal', 'understand',
        'email', 'month', 'introduce','agree', 'introduce', 'understanding',
        'express', 'recipient', 'qualify', 'access', 'express', 'asset', 'loacte', 'value', 'engage',
          'indirectly', 'month date', 'date', 'period', 'pre qualifying', 'qualifying', 'pre', 'directly',
          'locate pre', 'locate', 'pre directly' 'purpose',
          'assignment', 'directly purpose', 'employee', 'chairman', 'board', 'ceo', 'president', 
          'vice', 'vice_president', 'fiscal', 'in', 'january', 'february', 'march', 'total',
          'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december',' thousands',
          '10q', '10k', 'end', 'item', '8k','year', 'amount' ,'part i', 'part ii', 'part iii',
          'operate', 'operating', 'senior', 'tax', 'report', 'increase', 'increasing', 'reslt', 
          'revenue', 'million', 'millions', 'market', 'note', 'could', '2018', 'product', 'financail',
          'financials', 'cost', 'net', '2017', '2016', '31', 'custom', 'business', 'include',
          'product',	'result',	'us',	'financi',	'custom',	'2017',	'busi',	'includ',	'sale',	'requir',	
          'cost',	'2016',	'new',	'chang',	'31','30','develop',	'signific',	'advers',	'oper',	'effect',	'cash',	'manag',	'time',	
          'price',	'data',	'certain',	'secur',	'futur',	'market',	'materi',	'net',	'account',	'business',	'continu',	'abil',	
          'expens',	'control',	'report',	'base',	'intern',	'common',	'provid',	'rate',	
          'subject',	'unit',	'addit',	'consolid',	'manufactur',	'inform',	'compani',	
          'increas',	'impact',	'asset',	'risk',	'system',	'solut',	'products',	'invest',	'addition',	'2015',	
          'operations',	'general',	'applic',	'offer',	'industri',	'statement',	'expect',	'law',	'end',	
          'agreement',	'due',	'support',	'interest',	'services',	'contract',	'customers',	'exist',	'process',	
          'estim',	'believ',	'fair',	'liabil',	'million',	'properti',	'revenu',	'perform',	'state',	
          'year',	'reduc',	'content',	'network',	'licens',	'would',	'primarili',	'quarter',	'leas',	'regul',
          'use', 'also', 'item' , '31'

          }
          )
    return stop_words

def get_words():
    import json
    import os
    import re
    
    all_words = []
    directory = r'C:\Users\pgood\OneDrive\Documents\GitHub\Data 608 Final\Pages'
    stop_words = get_stops()
    for root,dirs,files in os.walk(directory):
        for file in files:
           if file.endswith(".txt"):
               file_name = os.path.join(directory, file)
               f=open(file_name, 'r')
               try:
                   data = json.load(f)
               except TypeError:
                   print("Problem with a file")
               except UnicodeDecodeError:
                   print("Problem with a file")
               words = data['page'].lower().split()
               for word in words:
                   if word not in stop_words:
                       all_words.append(re.sub('\W+', '', word))
               f.close()
    return all_words


def grams():
    from nltk import BigramCollocationFinder, BigramAssocMeasures, TrigramAssocMeasures, TrigramCollocationFinder
    
    
    words = get_words()
    
    bigram_measures = BigramAssocMeasures()
    finder = BigramCollocationFinder.from_words(words)
    finder.apply_freq_filter(800)
    bigrams = finder.nbest(bigram_measures.pmi, 500)
    
    trigram_measures = TrigramAssocMeasures()
    finder3 = TrigramCollocationFinder.from_words(words)
    finder3.apply_freq_filter(300)
    trigrams = finder3.nbest(trigram_measures.pmi, 300)
    combos2 = [combo2[0]+ " " + combo2[1] for combo2 in bigrams]
    combos3 = [combo3[0]+ " " + combo3[1] + " " + combo3[2] for combo3 in trigrams]
    return combos2, combos3