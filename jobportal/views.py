from cmath import log
import email
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from traitlets import Instance
from .models import ISCO, JobAnalysis, MyUser
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .forms import InputForm
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
from jobportal import views

def home(request):
    # count = User.objects.count()
    dataUser = MyUser.objects.filter(user=request.user)
    print(dataUser)
    return render(request, 'home.html', {
        'dataUser': dataUser
    })

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {
        'form': form
    })

def editprofile(request):
    context ={}
    context['form']= InputForm()
    dataUser = MyUser.objects.filter(user=request.user)

    if request.method == 'POST':
        form = InputForm(request.POST, request.FILES)

        if form.is_valid():
            MyUser.objects.filter(user=request.user).update(Firstname=request.POST["Firstname"], Lastname=request.POST["Lastname"], skills=request.POST["skills"])

            return HttpResponseRedirect('/profile')
    else:
        context['form']= InputForm(initial={"Firstname": dataUser[0].Firstname, "Lastname": dataUser[0].Lastname, "email":dataUser[0].email, "skills": dataUser[0].skills})

    return render(request, 'editprofile.html', {"context":context})

def profile(request):
    context ={}
    context['form']= InputForm()

    dataUser = MyUser.objects.filter(user=request.user)
    # print("Data : ", dataUser)

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = InputForm(request.POST, request.FILES)
        # check whether it's valid:

        # print("req : " +  form)

        if form.is_valid():
            form = MyUser(
                user = request.user,
                email = request.POST["email"],
                Firstname = request.POST["Firstname"],
                Lastname = request.POST["Lastname"],
                skills = request.POST["skills"]
            )
            form.save()

            return HttpResponseRedirect('/profile')

    elif (len(dataUser) == 0):
        context['form']= InputForm()

    return render(request, 'profile.html', {"context":context,"dataUser":dataUser})

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
    res = list(filter['Name'].iloc[data])

    # Return the top 10 most similar data
    return res

def recommendUser(request):

    dataUser = MyUser.objects.filter(user=request.user)
    # print(dataUser[0].skills)
    skillStr = dataUser[0].skills

    # code here
    keywordList = skillStr.rstrip().split(' ')
    print(keywordList)

    resDict = {}
    res = []
    for keyword in keywordList:
        if keyword == " ":
            continue
        else:
            # Filter keyword in Description
            filter = isco.loc[isco['Description'].str.contains(keyword, case=False)]
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
            res.extend(list(filter['Name'].iloc[data]))

    for data in res:
        if data in resDict:
            resDict[data] += 1
        else:
            resDict[data] = 1

    print(resDict)

    # end

    return render(request, 'recommendUser.html', {'resDict':resDict})

def Occupation(request):
    if (request.GET.get("search")):
        if request.method == 'GET':
            res = Recommend(request)
    else:
        res = {}
    
    return render(request, 'Occupation.html', {'dataList':res})