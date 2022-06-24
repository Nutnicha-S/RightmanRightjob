from cmath import log
import email
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
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

class UserEditView(generic.CreateView):
    form_class = UserChangeForm
    template_name = 'profile.html'
    success_url = reverse_lazy('home')

    def get_object(self):
        return self.request.user

def home(request):
    count = User.objects.count()
    return render(request, 'home.html', {
        'count': count
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

def profile(request):
    context ={}
    context['form']= InputForm()
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
                skill = request.POST["skill"]
            )
            form.save()

            return HttpResponseRedirect('/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = InputForm()
        dataUser = MyUser.objects.filter(user=request.user)
        print(dataUser)
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

def Occupation(request):
    print(request.GET.get("search"))

    if (request.GET.get("search")):
        if request.method == 'GET':
            res = Recommend(request)
    else:
        res = {}
    
    return render(request, 'Occupation.html', {'dataList':res})