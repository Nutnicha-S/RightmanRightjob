# import the standard Django Forms
# from built-in library
from faulthandler import disable
from django import forms
from requests import request
from traitlets import default

from jobportal.models import MyUser
   
# creating a form 
class InputForm(forms.Form):
    user = forms.CharField().disabled
    email = forms.EmailField(max_length = 200)
    Firstname = forms.CharField(max_length = 200)
    Lastname = forms.CharField(max_length = 200)
    skill = forms.CharField(max_length = 1000)

    class Meta:
        model = MyUser
        field = ["user", "email", "Firstname", "Lastname", "skill"]