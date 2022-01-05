from googlesearch import search
from multiprocessing import Manager, Pool
    

import pandas as pd
import time
import requests
from bs4 import BeautifulSoup
import re 
import random

import multiprocessing


sites_crawled = []


def get_url(query):
    global sites_crawled
    time.sleep(1)
    parts = query.split()
    query = '"' + " ".join(parts[:len(parts)//2+1]) + '"'
    print("Searching:", query)
    url = ""
    for url in search(query, stop = 1, num=1):
        print("URL:", url)
        if url not in sites_crawled:
            sites_crawled.append(url)
        else:
            url = ""
            print("Skipping ", query)
    return url        



def google_sentences(url):
    content = []
    try:
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.content, "html.parser")
        paragraph_texts = soup.find_all('p')
        content = [re.sub(r'<.+?>', r'', str(p)) for p in paragraph_texts]
        content = [re.sub(
                    r"[\"\#\%\&\(\)\*\+\/\:\<\=\>\@\[\\\]\^\_\`\{\|\}\~]+", " ", document) for document in content]
        content = [re.sub(r"[ \t\n\r\x0b\x0c]+", " ", document).split('.')
                           for document in content]
        content = [item for sublist in content for item in sublist]
        content = list(set(content))
    except:
        pass
    return content


def get_sentences(query, content):

    sentences = []
    org_parts = query.split(' ')
    if len(org_parts) > 1:
        #any one of first half of words?
        #org_main = 
        org_main = " ".join(org_parts[: random.randint(len(org_parts)//2 + 1, len(org_parts)-1)]) # never searches entire name
    else:
        org_main = org_parts[0]
    for line in content:
        if len(sentences) <= 100: # take max 5 sentences per company name, it will reduce on further filtering  
            line_words = line.split(' ')        
            if len(line_words) > len(org_parts):
                if (org_main in line): # to get longer meaningful sentences, not just a line with just the company name
                    sentences.append(line)
        else:
            break
    return sentences


def get_query_tags(query, main_tag, length):
    first_tag = ["B_" + main_tag]
    inner_tags = ["I_" + main_tag] * (length -1)
    tags = first_tag + inner_tags
    return tags
    
def get_B_indices(sent_words, B_word):
    indices = [i for i, x in enumerate(sent_words) if x == B_word]
    return indices


def tag_sentence(sent, query_words):
    sent_words = re.findall(r'\w+', sent)
    
    B_indices = get_B_indices(sent_words, query_words[0])
    X_one = sent_words
    y_one = ['O'] * len(sent_words)
    for B_index in B_indices:
        try:
            #20 Microns company, I was born in 2020, will also come here, and get eliminated after tokenization
            #B_index = words.index(query_words[0])
            
            y_one[B_index] = "B_ORG"
            count = 1
            
            for i in range(B_index + 1, B_index + 1 + len(query_words) - 1): # to avoid index out of bound
              if  i < len(sent_words):
                if sent_words[i].lower() == query_words[count].lower():
                    y_one[i] = "I_ORG"
                else:
                    break
                count = count + 1
              else:
                break
        except:
            pass
    X_one.append('.')
    y_one.append('O')
    X_one.append('\n')
    y_one.append('\n')
    # count holds number of words in company name found in sentence
    # eliminating some possible errors
    '''
    capital_in_sent = sum(1 for c in sent if c.isupper())
    capital_in_query = 0
    for word in query_words:
        capital_in_query = capital_in_query + sum(1 for c in word if c.isupper())
    if B_index == 0:
        if capital_in_sent > 3 * capital_in_query:
            X_one = []
            y_one = []  
    else:
        if capital_in_sent > 3 * (capital_in_query + 1):
            X_one = []
            y_one = [] '''  
    
    
    return X_one, y_one


def make_data(query, res_list):
    url = get_url(query)
    
    X_onequery = []
    y_onequery = []
    # skip if company has same site url as some other cause sentences from that site are already scrapped
    if url != "":
        content = google_sentences(url)
        if content != []:
            sentences = get_sentences(query, content)
            query_words = re.findall(r'\w+', query)
            #tags = get_query_tags(query, "ORG", len(query_words))
            for sent in sentences:
                print(sent)
                X_sent, y_sent = tag_sentence(sent, query_words)
                X_onequery = X_onequery + X_sent
                y_onequery = y_onequery + y_sent
                
        else:
            print("Empty content- ignoring")
    X_y_onequery = [(X_onequery[i], y_onequery[i]) for i in range(0, len(y_onequery))]
    res_list.append(X_y_onequery)
    
    print("DATA OF ONE QUERY:", X_y_onequery)


import csv

def write_csv(final_res):
    with open('org_data_6.csv', 'w', newline = '') as f:
        f.write('\n'.join('%s %s' % x for x in final_res))
    

if __name__ == "__main__":
    df = pd.read_csv("bse_companies.csv", encoding = "ISO-8859-1", usecols = ['Company Name'])
    names = list(df['Company Name'])
    names = names[5001:]
    manager = Manager()
    pool = Pool(4)
    res_list = manager.list()

    print(len(names))
    
    start = time.time()

    for name in names:
            print("---------------------- Scraping for", name , "------------------------")
            pool.apply_async(make_data, (name, res_list,))

    pool.close()
    pool.join()
    end = time.time()
    print("Time taken: ", end - start)
    print("FINAL: \n",res_list)
    final_res = [item for sublist in res_list for item in sublist]
    write_csv(final_res)