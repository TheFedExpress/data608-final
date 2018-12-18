# -*- coding: utf-8 -*-
"""
Created on Fri Nov 23 13:03:37 2018

@author: pgood
"""

from urllib.request import urlopen
import pandas as pd
from bs4 import BeautifulSoup

company_list = pd.read_csv('companylist.csv')

base = 'https://www.sec.gov'

def get_contents(soup):
    page_type = 'p'
    all_ps = soup.find_all('p')
    all_fonts = soup.find_all('font')
    if len(all_ps) > 0 and len(all_fonts) <= 1000:
        page_type = 'p'
    else:
        page_type = 'pfont'
    if len(all_ps) == 0:
        all_ps = soup.find_all('font')
        page_type = 'font'
    if len(all_ps) == 0:
        all_ps = soup.final_all('div')
        page_type = 'div'
        print(url)
    base_string = ''
    past_contents = False
    past_3 = False
    i = 0
    for ptag in all_ps:
        is_ital = False
        if page_type == 'p':
            bolds = []
            try:
                bolds = ptag.find_all('b')
            except:
                pass
            if len(bolds) >=1:
                for bold in bolds:
                    if bold.text.lower().strip() in ['part i', 'part\xa0i']:
                        print('hit')
                        past_contents = True
                    elif bold.text.lower().strip() in ['part ii', 'part\xa0ii']:
                        print('done')
                        past_3 = True
        elif page_type == 'pfont':
            try:
                if 'font-style:italic' in ptag.font['style'].lower():
                    is_ital = True
                if 'font-weight:bold' in ptag.font['style'].lower():
                    a_parents = ptag.find_parents('a')
                    a_parents = len(ptag.find_parents('a'))
                    a_children = len(ptag.find_all('a'))
                    a_tots = a_parents + a_children
                    if  ptag.text.lower().strip() in ['part i', 'part\xa0i']:
                        print(ptag.text.lower().strip())
                        print(i)
                        past_contents = True
                    elif ptag.text.lower().strip() in ['part ii', 'part\xa0ii']:
                        print(ptag.text.lower().strip())
                        past_3 = True
            except:
                pass
        elif page_type == 'font':
            if 'font-style:italic' in ptag['style'].lower():
                is_ital = True
            if 'font-weight:bold' in ptag['style'].lower():
                a_parents = len(ptag.find_parents('a'))
                a_children = len(ptag.find_all('a'))
                a_tots = a_parents + a_children
                if ptag.text.lower().strip() in ['part i', '\ufeffpart\xa0i'] and a_tots == 0:
                    print(ptag.text.lower().strip())
                    past_contents = True
                elif ptag.text.lower().strip() in ['part ii', 'part\xa0ii'] and a_tots == 0:
                    print(ptag.text.lower().strip())
                    past_3 = True
    
                    
        if past_3 == True:
            break
            
        if past_contents and not past_3:
            is_bold = len(ptag.find_all('b')) > 1
            is_table = len(ptag.find_all('table')) > 1
            is_in_table = ptag.parent.name == 'table'
            is_anchor = len(ptag.find_all('A')) > 1
            if (is_bold == False and is_anchor ==False and is_in_table == False
                and is_table == False and is_ital ==False):
               base_string += ptag.text + ' '
    return base_string

strings = []
for ticker in company_list['Symbol']:
    for i in range(0, 300, 100):
        url = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&type=&dateb=&owner=include&start={}&count=100'.format(ticker, i)
        try:
            page = urlopen(url).read()
            soup1 = BeautifulSoup(page, 'lxml')
            txt = soup1(text = '10-K')
            if len(txt) > 0:
                break
        except:
            print(url)
    try:
        link = txt[0].parent.parent.find_all('a')[0]['href']
        page2 = urlopen(base + link).read()
        soup2 = BeautifulSoup(page2, 'lxml')
        tbl = soup2.find_all('table', class_ = 'tableFile')[0]
        link2 = tbl(text = '10-K')[0].parent.parent.find_all('a')[0]['href']
        
        final_page = urlopen(base + link2).read()
        soup = BeautifulSoup(final_page, 'lxml')
        my_string = get_contents(soup)
        strings.append({'company': ticker, 'page': my_string})
    except:
        print(url)
    
def write_file(data):
    import json
    
    ticker = data['company']
    fname = 'pages/' + ticker + '.txt'
    with open(fname, 'w') as json_file:
        json.dump(data, json_file)

for item in strings:
    if len(item['page']) > 1000:
        write_file(item)