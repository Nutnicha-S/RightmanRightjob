from django.shortcuts import render
from .models import ISCO, JobAnalysis
from .forms import Recommend
import numpy as np
import os
import nltk
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import words
from nltk.stem.porter import PorterStemmer
import pythainlp
from pythainlp import word_tokenize
from pythainlp.corpus.common import thai_stopwords
from pythainlp.corpus import wordnet
import re,string,random
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import linear_kernel

isco = pd.read_csv("jobportal/dataset/ISCOutf.csv",encoding='utf-8')
tfidf = TfidfVectorizer(stop_words=thai_stopwords())

#Replace NaN with an empty string 
isco['Description'] = isco['Description'].fillna('')

def Recommend(request):

    # Get keyword from template
    msg=request.GET['search']
    # Filter keyword in Description
    filter = isco.loc[isco['Description'].str.contains(msg, case=False)]
    # Output the shape of tfidf_matrix
    isco_matrix = tfidf.fit_transform(filter['Description'])
    similarity_matrix = linear_kernel(isco_matrix,isco_matrix)

    # Get the pairwsie similarity scores of all data
    sim_scores = list(enumerate(similarity_matrix[0]))

    # Sort the data based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the 10 most similar data
    sim_scores = sim_scores[0:10]

    # Get the data indices
    data = [i[0] for i in sim_scores]

    res = filter['Name'].iloc[data]

    # Return the top 10 most similar data
    return render(request, 'Result.html', {'data':res})

def Occupation(request):
    data = ISCO.objects.all()
    return render(request, 'Occupation.html', {'Occupation':data})

#def Recommend(request):
#    if request.method == 'GET':
#        name = request.GET['search']
#        data = get_recommendations(name)
#    return render(request, 'Recommend.html', {'data':data})