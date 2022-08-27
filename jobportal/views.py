from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from .models import MyUser
from django.contrib.auth.forms import UserCreationForm
from .forms import InputForm
from pythainlp import word_tokenize
from pythainlp.corpus.common import thai_stopwords
from pythainlp.util import normalize
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

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
            return redirect('login')
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
            MyUser.objects.filter(user=request.user).update(email=request.POST["email"], Firstname=request.POST["Firstname"], Lastname=request.POST["Lastname"], skills=request.POST["skills"])

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
isco['Name'] = isco['Name'].fillna('')

def Recommend(request):
    # Get keyword from template
    msg=request.GET['search']
    print(type(msg))
    # Clean the word
    norm_msg = normalize(msg)
    print(norm_msg)
    list_msg = word_tokenize(norm_msg)
    stop_msg = list(thai_stopwords())
    new_msg = [i for i in list_msg if i not in stop_msg]
    real_msg = [value for value in new_msg if value != " "]
    print(real_msg)

    res = []

    for i in range(len(real_msg)):
        # Filter keyword in Description
        a = isco['Description'].str.contains(real_msg[i], case=False)
        b = isco['Name'].str.contains(real_msg[i], case=False)
        c = a+b
        filterDes = isco.loc[c]
        print(filterDes)

        if filterDes['Description'].empty:
            res = {'ไม่มีอาชีพที่คุณค้นหา กรุณาใช้คำอื่น'}
            # return res
        else :
            # Output the shape of tfidf_matrix
            isco_matrix = tfidf.fit_transform(filterDes['Description'])
            similarity_matrix = linear_kernel(isco_matrix,isco_matrix)

            # Get the pairwsie similarity scores of all data
            sim_scores = list(enumerate(similarity_matrix[0]))

            # Sort the data based on the similarity scores
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            # Get the scores of the 10 most similar data
            # sim_scores = sim_scores[0:20]
            # Get the data indices
            data = [i[0] for i in sim_scores]
 
            res.extend(list(filterDes['Name'].iloc[data]))

    return res

def getDescriptionByName(request, key):
    keyName = key
    filter = isco.loc[isco['Name'].str.contains(keyName, case=False)]

    print("In get Description By Name")
    print(list(filter["Description"])[0])
    # code here

    return render(request, 'moreinfo.html', {"context":list(filter["Description"])[0],"key":key})

def recommendUser(request):
    dataUser = MyUser.objects.filter(user=request.user)
    # print(dataUser[0].skills)
    skillStr = dataUser[0].skills

    # code here
    keywordList = skillStr.rstrip().split(' ')
    print(keywordList)

    msg = []
    for value in keywordList:
        # Clean the word
        norm_msg = normalize(value)
        print(norm_msg)
        list_msg = word_tokenize(norm_msg)
        stop_msg = list(thai_stopwords())
        new_msg = [i for i in list_msg if i not in stop_msg]
        msg.extend(new_msg)
        print(msg)

    resDict = {}
    res = []
    for keyword in range(len(msg)):
        # Filter keyword in Description
        a = isco['Description'].str.contains(msg[keyword], case=False)
        b = isco['Name'].str.contains(msg[keyword], case=False)
        c = a+b
        filter = isco.loc[c]

        if filter['Description'].empty:
            res = {'ไม่มีอาชีพที่คุณค้นหา กรุณาใช้คำอื่น'}
        #     return render('recommendUser.html',messages.success(request, zipRes))
        else:
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

    sort_orders = sorted(resDict.items(), key=lambda x: x[1])
    labels = []
    data = []

    for index in range(len(sort_orders)):
        labels.append(sort_orders[index][0])
        data.append(sort_orders[index][1])

    labels.reverse()
    data.reverse()
    multiData = 100/len(sort_orders)
    multiplied_list = [round((element * multiData), 2) for element in data]
    zipRes = zip(labels,multiplied_list)

    return render(request, 'recommendUser.html', {
        'zipRes': zipRes
    })

def Occupation(request):
    if (request.GET.get("search")):
        if request.method == 'GET':
            res = Recommend(request)
    else:
        res = {}
    
    return render(request, 'Occupation.html', {'dataList':res})