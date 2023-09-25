from urllib import request
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile
from django.contrib.auth import authenticate,login,logout





# Create your views here.

def landing_page(request):
    
        
    return render(request,'index.html')

def user_login(request):
    if request.user.is_authenticated:
        return redirect(landing_page)
    
    else:
        if request.method == "POST":
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(request, email=email , password=password)
            print(f"Email: {email}")
            print(f"Password: {password}")
            print(f"Authenticated User: {user}")
            if user is not None:
                login(request, user)
                messages.success(request, ("Logged in successfully "))
                return redirect(landing_page)
        else:
            messages.success(request, ("Invalid Credentials"))
            return render(request, 'login.html', {'error':"Invalid Credentials "})  
    
    return render (request, 'login.html')


    

def signup(request):
    if request.method == "POST":
            username = request.POST['username']
            email = request.POST['email']
            mobile = request.POST['phone']
            password1 = request.POST['password1']
            password2 = request.POST['password2']   
            if password1 == password2 and password1 !="":
                if UserProfile.objects.filter(username = username).exists() or UserProfile.objects.filter(email = email).exists():
                    return render(request, 'signup.html',{'error':"User already exist or Invalid Credential"})
                
                else:
                    user = UserProfile.objects.create_user(username=username,email=email,password=password1,phone=mobile)
                    user.save()
                    messages.success(request, ("Your Account has been successfully created"))
                    return redirect(user_login)

    return render(request, 'signup.html')




def signout(request):

    if request.user.is_authenticated:
        logout(request)

    return render(request,'login.html')