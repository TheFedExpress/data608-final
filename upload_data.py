# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 00:48:09 2018

@author: pgood
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import time
import json
import os

connection = MongoClient('ds135714.mlab.com', 35714)
db = connection['data608-final']
db.authenticate('pgoodridge2007', 'Cunydata1')
    
"""    
db.pages.insert_many(pages.to_dict(orient = 'records'))

"""

directory = r'C:\Users\pgood\OneDrive\Documents\GitHub\Data 608 Final\Pages'
for root,dirs,files in os.walk(directory):
    for file in files:
        
        file_name = os.path.join(directory, file)
        f=open(file_name, 'r')
        d = json.load(f)
        db.pages_raw.insert_one(d)
