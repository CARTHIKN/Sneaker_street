from urllib import request
from django.http import HttpResponse
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile, Product, Product_image
from django.contrib.auth import authenticate,login,logout
from django.core.mail import send_mail
import pyotp
from django.views.decorators.cache import cache_control
from carts.views import  _cart_id
from carts.models import  CartItem, Cart
from django.core.mail import send_mail
import random
from django.views.decorators.cache import never_cache
import requests










# Create your views here.

def landing_page(request):
    
    products = Product.objects.all()
    return render(request,'index.html', {'products':products})

@never_cache
def user_login(request):
        
        if request.user.is_authenticated and not request.user.is_superuser:
            return redirect('landing')
            
        if request.method == "POST":
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(request, email=email , password=password)
            if user is not None:
                try:
                    cart = Cart.objects.get(cart_id =_cart_id(request))
                    is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                    if is_cart_item_exists:
                        cart_item = CartItem.objects.filter(cart=cart)

                        # getting the product variations by cart id
                        product_variation = []
                        for item in cart_item:
                            variation = item.variations.all()
                            product_variation.append(list(variation))

                        # Get the cart items from the user to access his product variations
                        cart_item = CartItem.objects.filter(user=user)
                        ex_var_list = []
                        id = []
                        for item in cart_item:
                            existing_variation = item.variations.all()
                            ex_var_list.append(list(existing_variation))
                            id.append(item.id)


                        # product_variation = [1, 2, 3, 4, 6]
                        # ex_var_list = [4, 6, 3, 5]


                        for pr in product_variation:
                            if pr in ex_var_list:
                                index = ex_var_list.index(pr)
                                item_id = id[index]
                                item = CartItem.objects.get(id=item_id)
                                item.quantity += 1
                                item.user = user
                                item.save()

                            else:
                                cart_item = CartItem.objects.filter(cart=cart)
                                for item in cart_item:
                                    item.user = user
                                    item.save()


                except:
                    pass
                login(request, user)
                messages.success(request, ("Logged in successfully "))
                url = request.META.get('HTTP_REFERER')
                try:
                    query = requests.utils.urlparse(url).query
                    params = dict(x.split('=') for x in query.split('&'))
                    if 'next' in params:
                        nextPage = params['next']
                        return redirect(nextPage)
                except:
                    return redirect(landing_page)

                
        else:
            messages.success(request, ("Invalid Credentials"))
            return render(request, 'login.html', {'error':"Invalid Credentials "},)  
    
        return render (request, 'login.html')


    
@never_cache
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
                    from_email = 'carthikn1920@gamil.com'  # Change this to your email address
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



@never_cache
def signout(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('landing')

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
    in_cart = CartItem.objects.filter(cart__cart_id =_cart_id(request), product=product).exists()

    context = {
        'product':product,
        'in_cart':in_cart
    }

    return render(request, 'productdetails.html', context)


def search(request):
    return HttpResponse("search page")

def forgotPassword(request):
        if request.method == "POST":
            email = request.POST['email']
            if UserProfile.objects.filter(email=email).exists():
                # Generate a random OTP (you can customize the length)
                otp = ''.join(random.choice('0123456789') for i in range(6))

                # Send the OTP to the user's email
                subject = 'Password Reset OTP'
                message = f'Your OTP for password reset is: {otp}'
                from_email = 'carthikn1920@gmail.com'  # Change this to your email address
                recipient_list = [email]

                send_mail(subject, message, from_email, recipient_list, fail_silently=False)

                # Store the OTP in the session
                request.session['reset_otp'] = otp
                request.session['reset_email'] = email

                # Redirect to the OTP verification page
                return redirect('password-verify-otp')

            else:
                messages.error(request, 'Account does not exist')
    
        return render(request, 'forgotpassword.html')



def password_verify_otp(request):
    if 'reset_otp' in request.session and 'reset_email' in request.session:


        if request.method == "POST":
            entered_otp = request.POST.get('otp', '')
            stored_otp = request.session['reset_otp']
            email = request.session['reset_email']

            if entered_otp == stored_otp:
               
                del request.session['reset_otp']
                request.session['reset_email'] = email
                
                return redirect(reset_password)
            else:
                messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'otp.html')


def reset_password(request):
    if 'reset_email' in request.session:  # Check if email is in the session
        email = request.session['reset_email']  
        if request.method == "POST":
        
            password1 = request.POST['new_password']
            password2 = request.POST['new_password2']

            if password1 != "" and password1 == password2:
                user = UserProfile.objects.get(email=email)
                user.set_password(password1)
                user.save()
                del request.session['reset_email']

                messages.success(request, "Password reset successfully.")
                return redirect(user_login)
            
        return render(request, 'reset.html')
    

