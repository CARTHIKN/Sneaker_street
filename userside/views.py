from urllib import request
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile, Product, Product_image
from django.contrib.auth import authenticate,login,logout
from django.core.mail import send_mail
import pyotp
from django.views.decorators.cache import cache_control





# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def landing_page(request):
    
    products = Product.objects.all()
    return render(request,'index.html', {'products':products})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_login(request):
        
        if 'email' in request.session:
            return redirect('landing')
            
        if request.method == "POST":
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(request, email=email , password=password)
            if user is not None:
                request.session['email'] = email
                login(request, user)
                messages.success(request, ("Logged in successfully "))
                return redirect(landing_page)
        else:
            messages.success(request, ("Invalid Credentials"))
            return render(request, 'login.html', {'error':"Invalid Credentials "},)  
    
        return render (request, 'login.html')


    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
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
                    totp = pyotp.TOTP(pyotp.random_base32())
                    otp_code = totp.now()

        # Send OTP to the user's email
                    subject = 'OTP Verification'
                    message = f'Your OTP for signup is: {otp_code}'
                    from_email = 'carthikn2002@gamil.com'  # Change this to your email address
                    recipient_list = [email]

                    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

                    # Store OTP code in session
                    request.session['otp_code'] = otp_code

                    # Store user data in session
                    request.session['user_data'] = {
                        'username': username,
                        'email': email,
                        'phone': mobile,
                        'password1': password1,
                        'password2': password2,
                    }

                    messages.success(request, "An OTP has been sent to your email. Enter it to complete registration.")
                    return redirect(verify_otp)

    return render(request, 'signup.html')



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def signout(request):

    if 'email' in request.session:
        request.session.flush()

    return render(request,'login.html')

def verify_otp(request):
    if 'otp_code' not in request.session or 'user_data' not in request.session:
        return redirect(signup)  # Redirect to signup if session data is missing

    if request.method == "POST":
        entered_otp = request.POST.get('otp', '')
        stored_otp = request.session['otp_code']

        if entered_otp == stored_otp:
            # OTP is correct, create the user in the database
            user_data = request.session['user_data']
            user = UserProfile.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password1'],
                phone=user_data['phone']
            )
            user.save()
            messages.success(request, "Your account has been successfully created.")
            del request.session['otp_code']
            del request.session['user_data']
            return redirect(user_login)

        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'otp.html')


def product_details(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'productdetails.html', {'product': product})