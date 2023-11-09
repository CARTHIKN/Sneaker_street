from datetime import datetime, timedelta
from urllib import request
from django.http import HttpResponse
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Category, UserProfile, Product, Product_image
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
from django.utils import timezone
from django.views.decorators.cache import cache_control
from django.core.paginator import Paginator
from django.db.models import Q










# Create your views here.
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def landing_page(request):
    
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request,'index.html', {'products':products, 'categories':categories})


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


    
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
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



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
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

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def product_details(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    in_cart = CartItem.objects.filter(cart__cart_id =_cart_id(request), product=product).exists()

    context = {
        'product':product,
        'in_cart':in_cart
    }

    return render(request, 'productdetails.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def search(request):
    categories = Category.objects.all()
    products = []

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            # Modify the search query to include product name, description, color variations, and size variations
            products = Product.objects.filter(
                Q(Product_name__icontains=keyword) |
                Q(description__icontains=keyword) |
                (Q(variation__variation_category='color', variation__variation_value__icontains=keyword) |
                Q(variation__variation_category='size', variation__variation_value__icontains=keyword))
            ).distinct()
            product_count = products.count()
        else:
            product_count = 0  # Handle the case when no keyword is provided
    else:
        product_count = 0  # Handle the case when 'keyword' is not in request.GET

    products_list = [product.id for product in products]
    request.session['product_id'] = products_list

    return redirect('shop-product')



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def forgotPassword(request):
    if request.method == "POST":
        email = request.POST.get('email', '')  # Ensure email is a string

        if UserProfile.objects.filter(email=email).exists():
            last_sent_time_str = request.session.get('otp_sent_time')

            if last_sent_time_str:
                last_sent_time = datetime.strptime(last_sent_time_str, '%Y-%m-%d %H:%M:%S.%f%z')
                elapsed_time = timezone.now() - last_sent_time

                if elapsed_time.total_seconds() < 120:
                    messages.error(request, 'Please wait before requesting a new OTP.')
                    return redirect('forgotPassword')

            # Generate a random OTP (you can customize the length)
            otp = ''.join(random.choice('0123456789') for i in range(6))

            # Send the OTP to the user's email
            subject = 'Password Reset OTP'
            message = f'Your OTP for password reset is: {otp}'
            from_email = 'carthikn1920@gmail.com'  
            recipient_list = [email]

            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

            # Store the OTP in the session
            request.session['reset_otp'] = otp
            request.session['reset_email'] = email
            request.session['otp_sent_time'] = timezone.now().strftime('%Y-%m-%d %H:%M:%S.%f%z')

            # Redirect to the OTP verification page
            return redirect('password-verify-otp')

        else:
            messages.error(request, 'Account does not exist')

    context = {
    'otp_expired': False,  # Set to True if OTP has expired
    }

    return render(request, 'forgotpassword.html', context)



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def password_verify_otp(request):
    if 'reset_otp' in request.session and 'reset_email' in request.session:
        stored_otp = request.session['reset_otp']
        email = request.session['reset_email']
        otp_sent_time_str = request.session.get('otp_sent_time')

        if not otp_sent_time_str:
            messages.error(request, 'OTP has expired. Please request a new one.')
            return redirect('forgotPassword')

        otp_sent_time = datetime.strptime(otp_sent_time_str, '%Y-%m-%d %H:%M:%S.%f%z')
        elapsed_time = timezone.now() - otp_sent_time

        if elapsed_time.total_seconds() >= 120:
            messages.error(request, 'OTP has expired. Please request a new one.')
            request.session['otp_expired'] = True  # Mark OTP as expired
            return redirect('forgotPassword')

        if request.method == "POST":
            entered_otp = request.POST.get('otp', '')
            if entered_otp == stored_otp:
                # Valid OTP; proceed with password reset
                del request.session['reset_otp']
                del request.session['otp_sent_time']
                request.session['reset_email'] = email
                request.session['otp_verified'] = True  # Mark OTP as verified
                return redirect('reset-Password')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
    context = {
    'otp_expired': False,  # Set to True if OTP has expired
    }
    return render(request, 'otp.html', context)



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
    else:
        messages.error(request, 'Session data missing. Please request OTP again.')
        return redirect('forgotPassword')
    

@cache_control(no_cache=True,must_revalidate=True,no_store=True)  
def shop_product(request, att='id'):


    color_filter = request.GET.get('color')
    size_filter = request.GET.get('size')



    # request.session['color_filter'] = False
    # request.session['size_filter'] = False
    if color_filter:
        request.session['color_filter'] = color_filter

    if size_filter:
        request.session['size_filter'] = size_filter

    color_filter = request.session.get('color_filter')
    size_filter = request.session.get('size_filter')
    

    products=Product.objects.all().filter(is_available=True).order_by('id')


    if 'product_id' in request.session:
        pk_key = request.session['product_id']
        products = Product.objects.filter(id__in=pk_key)
    categories=Category.objects.all()
    print(att)
    # sorting_order = request.GET.get('sort', 'default')  # 'default' is the default sorting order

    if color_filter:
        products = products.filter(
            variation__variation_category='color', 
            variation__variation_value__iexact=color_filter
            )

    if size_filter:
        products = products.filter(
            variation__variation_category='size', 
            variation__variation_value__iexact=size_filter
            )


    products = products.order_by(att)
    paginator=Paginator(products,6)
    page=request.GET.get('page')
    product_count=products.count()
    paged_products=paginator.get_page(page)
        
    context={
        'products':paged_products,
        'product_count':product_count,
        'categories':categories,

    }
    return render(request, 'page-shop.html',context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)  
def shop_product_by_category(request, category_slug):
    try:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True)
    except:
        products = Product.objects.filter(is_available=True)

    request.session['color_filter'] = False
    request.session['size_filter'] = False
    products_list = [product.id for product in products]
    request.session['product_id'] = products_list
    return redirect('shop-product')

# def filters(request):


#     products = Product.objects.all()
#     # categories = Category.objects.all()
#     if 'product_id' in  request.session:
#         pk_key = request.session['product_id']
#         products = Product.objects.filter(id__in=pk_key)

#     sort_by = request.GET.get('sort', 'featured')  # Default to 'featured' if no sorting parameter is provided

#     if sort_by == 'price_low_high':
#         products = Product.objects.order_by('price')  # Order by price (low to high)
#         product_count=products.count()
#     elif sort_by == 'price_high_low':
#         products = Product.objects.order_by('-price')  # Order by price (high to low)
#         product_count=products.count()
#     else:
#         # Default to featured order or other sorting logic you have

#     context = {
#         'products': products,
#          'categories': categories,
#          'product_count': product_count,
#         # Other context data you might have
#     }

#     return render(request, 'page-shop.html', context)