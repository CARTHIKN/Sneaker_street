from django.shortcuts import render
from urllib import request
from django import views

# Create your views here.
def adminlogin(request):
    return render(request, 'adminside/admin_login.html')