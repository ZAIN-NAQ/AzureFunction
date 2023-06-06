# -*- coding: utf-8 -*-
"""
Created on Sat Jul 23 15:56:11 2022

@author: zainh
"""

import numpy as np
import pandas as pd
import nltk
nltk.download("stopwords")
import os
import string
import re
from nltk.stem import *
import nltk

import math

from nltk.corpus import stopwords

def tokenize_and_remove_punctuations(s):
    translator = str.maketrans('','',string.punctuation)
    string_transformed = s.translate(translator)
    string_transformed = ''.join([i for i in string_transformed if not i.isdigit()])
    return nltk.word_tokenize(string_transformed)

# =============================================================================
# def get_stopwords():
#     #from nltk.corpus import stopwords
#     stopwordsfromnltk = stopwords.words('english')
#     stop_words = stopwordsfromnltk
#     return stop_words
# =============================================================================

def stem_words(tokens):
    stemmer = PorterStemmer()
    stemmed_words = [stemmer.stem(token) for token in tokens]
    return stemmed_words

def remove_stop_words(tokens):
    stop_words = stopwords.words('english')
    filtered_words = [token for token in tokens if token not in stop_words and len(token) > 2]
    return filtered_words

def tfcalculator(tokens):
    tf_score = {}
    for token in tokens:
        tf_score[token] = tokens.count(token)
    return tf_score

def get_vocabulary(data):
    tokens = []
    for token_list in data.values():
        tokens = tokens + token_list
    fdist = nltk.FreqDist(tokens)
    return list(fdist.keys())

def preprocess_data(contents):
    dataDict = {}
    count=0
    for content in contents:
        #print(content[1])
        tokens = tokenize_and_remove_punctuations(content)
        #print(tokens)
        filtered_tokens = remove_stop_words(tokens)
        stemmed_tokens = stem_words(filtered_tokens)
        #print(stemmed_tokens)
        filtered_tokens1 = remove_stop_words(stemmed_tokens)
        #print(filtered_tokens1)
        #print(content[0])
        dataDict[count] = filtered_tokens1
        count +=1
    return dataDict

def idfCalculator(data):
    idf_score = {}
    N = len(data)
    all_words = get_vocabulary(data)
    for word in all_words:
        word_count = 0
        for token_list in data.values():
            if word in token_list:
                word_count += 1
        idf_score[word] = math.log10(N/word_count)
    return idf_score

def tfidfCalculatorData(data, idf_score):
    scores = {}
    for key,value in data.items():
        scores[key] = tfcalculator(value)
    for doc,tf_scores in scores.items():
        for token, score in tf_scores.items():
            tf = score
            idf = idf_score[token]
            tf_scores[token] = tf * idf
    return scores

def query_preproces(path):
    queriesDict = {}
    queries = path.split('\n')
    i = 1
    for query in queries:
        tokens = tokenize_and_remove_punctuations(query)
        filtered_tokens = remove_stop_words(tokens)
        stemmed_tokens = stem_words(filtered_tokens)
        filtered_tokens1 = remove_stop_words(stemmed_tokens)
        queriesDict[i] = filtered_tokens1
        i+=1
    print('-----------')
    return queriesDict

def tfidfCalculatorQuery(queries, idf_score):
    scores = {}
    print(queries)
    for key, value in queries.items():
        scores[key] = tfcalculator(value)
    for key, tf_scores in scores.items():
        for token, score in tf_scores.items():
            idf = 0
            tf = score
            if token in idf_score.keys():
                idf = idf_score[token]
            tf_scores[token] = tf * idf
    return scores

def InvertedIndex(data):
    wordsinDoc = get_vocabulary(data)
    index = {}
    for word in wordsinDoc:
        for doc, tokens in data.items():
            if word in tokens :
                if word in index.keys():
                    index[word].append(doc)
                else:
                    index[word] = [doc]
    return index