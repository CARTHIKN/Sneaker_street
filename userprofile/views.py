from datetime import datetime
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from userside.views import UserProfile
from .models import Userdetails

# Create your views here.
@login_required
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