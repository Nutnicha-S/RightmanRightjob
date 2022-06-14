from django import forms

class Recommend(forms.Form):
    search = forms.CharField(label='search', max_length=100)