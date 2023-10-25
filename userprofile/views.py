from datetime import datetime
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from userside.views import UserProfile
from .models import Userdetails
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from orders.models import OrderProduct, Order
from django.views.decorators.cache import cache_control


# Create your views here.
@login_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def user_profile(request):
    print(request)
    user_profile_instance = UserProfile.objects.get(email=request.user)
    
    userdetails, created = Userdetails.objects.get_or_create(userprofile=user_profile_instance)

    context = {
        'user': request.user,
        'userdetails': userdetails
    }
    return render(request, 'userprofile/account.html', context)

@login_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def edit_profile(request):
    user_profile_instance = UserProfile.objects.get(email=request.user)
    userdetails, created = Userdetails.objects.get_or_create(userprofile=user_profile_instance)

    if request.method == 'POST':
        fullname = request.POST['full_name']
        phone = request.POST['phone']
        date_of_birth = request.POST['DOB']
        

        # Update the existing user details object
        userdetails.fullname = fullname
        if date_of_birth:
            try:
                date_obj = datetime.strptime(date_of_birth, '%Y-%m-%d')
                userdetails.date_of_birth = date_obj.date()
            except ValueError:
                print("Invalid date format. Please use 'YYYY-MM-DD' format.")
        
      
        userdetails.save()

        # Update the user profile's phone number
        user_profile_instance.phone = phone
        user_profile_instance.save()

        # Redirect to a success page or profile page
        return redirect('userprofile:user-profile')

    context = {
        'user': request.user,
        'userdetails': userdetails,
    }
    return render(request, 'userprofile/edit_profile.html', context)    


@login_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def change_password(request):
    if request.method == "POST":
        current_password = request.POST['password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['new_password2']

        user = request.user  

        if user.check_password(current_password):
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)  # Update the session to keep the user logged in
                messages.success(request, "Password changed successfully.")
                return redirect('userprofile:user-profile')
            else:
                messages.error(request, "New password and confirmation do not match.")
        else:
            messages.error(request, "Current password is incorrect.")

    return render(request, 'userprofile/change_password.html')

@login_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def user_orders(request):
    # Query the orders for the logged-in user
    orderroducts = OrderProduct.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)


    return render(request, 'userprofile/user_orders.html', {'orders': orders, 'orderproducts':orderroducts})