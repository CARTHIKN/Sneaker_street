from datetime import datetime
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from orders.forms import addressbook_form
from userside.models import AddressBook
from userside.views import UserProfile
from .models import Userdetails
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from orders.models import OrderProduct, Order
from django.views.decorators.cache import cache_control
import re
from datetime import date


# Create your views here.
@login_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def user_profile(request):
    selected_menu = request.GET.get('menu_item' , 'profile')
    print(request)
    user_profile_instance = UserProfile.objects.get(email=request.user)
    
    userdetails, created = Userdetails.objects.get_or_create(userprofile=user_profile_instance)

    context = {
        'user': request.user,
        'userdetails': userdetails,
        'selected_menu': selected_menu,
        
    }
    return render(request, 'userprofile/account.html', context)



@login_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def edit_profile(request):
    user_profile_instance = UserProfile.objects.get(email=request.user)
    userdetails, created = Userdetails.objects.get_or_create(userprofile=user_profile_instance)

    if request.method == 'POST':
        fullname = request.POST['full_name'].strip()
        phone = request.POST['phone'].strip()
        date_of_birth = request.POST['DOB'].strip()
        
         # Custom validation logic
        name_pattern = r'^[A-Za-z. ]+$'
        phone_pattern = r'^\d{10}$'

        if len(fullname) <= 3:
            messages.error(request, "Full name must be longer than 3 characters.")
        elif not re.match(name_pattern, fullname):
            messages.error(request, "Invalid full name. Please use only letters, spaces, and dots.")
        elif not re.match(phone_pattern, phone):
            messages.error(request, "Invalid phone number. Please provide a 10-digit number.")
            

        else:
            try:
                date_obj = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
                today = date.today()

                if date_obj >= today:
                    messages.error(request, "Invalid date of birth. Please use a past date.")
                else:
                    userdetails.fullname = fullname
                    userdetails.date_of_birth = date_obj
                    userdetails.save()
                    user_profile_instance.phone = phone
                    user_profile_instance.save()
                    return redirect('userprofile:user-profile')

            except ValueError:
                print("Invalid date format. Please use 'YYYY-MM-DD' format.")

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
    selected_menu = 'orders'
    orderroducts = OrderProduct.objects.filter(user=request.user).order_by('-created_at')
    orders = Order.objects.filter(user=request.user).exclude(status="New").order_by('-created_at')



    return render(request, 'userprofile/user_orders.html', {'orders': orders, 'orderproducts':orderroducts, 'selected_menu': selected_menu,})



@login_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def user_address(request):
    
    selected_menu = 'address'
    addressess  = AddressBook.objects.filter(user=request.user)

    return render(request,'userprofile/user_address.html', {'addressess' : addressess, 'selected_menu': selected_menu,})


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_address(request, address_id):
    address = get_object_or_404(AddressBook, id=address_id, user=request.user)

    if request.method == 'POST':
        # Retrieve updated data from the POST request
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        pincode = request.POST.get('pincode')

        # Update the address fields
        address.name = name
        address.phone = phone
        address.address_line_1 = address_line_1
        address.address_line_2 = address_line_2
        address.city = city
        address.state = state
        address.country = country
        address.pincode = pincode

        # Save the updated address
        address.save()

        return redirect('userprofile:user-address')
    context = {
        'address': address,
    }

    return render(request, 'userprofile/edit_address.html', context)


def user_add_address(request):
    if request.method == "POST":
        form = addressbook_form(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('userprofile:user-address')
        else:
            print(form.non_field_errors())
    return render(request, 'userprofile/user_add_address.html')