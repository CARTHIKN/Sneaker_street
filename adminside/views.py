from django.contrib import messages
from django.shortcuts import redirect, render
from userside.models import UserProfile, Product
from django.contrib.auth import authenticate,login,logout
# Create your views here.
def admin_login(request):
    if request.user.is_authenticated:
        return render(request, 'adminside/dashboard.html')
    else:
        if request.method == "POST":
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(request, email=email , password=password)
            if user is not None and user.is_superuser:
                login(request,user)
                return redirect('adminside:dashboard')
            else :
                messages.success(request,'Invalid credentials')
                return redirect(admin_login)      
        else:
            return render(request, 'adminside/admin_login.html')


def dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'adminside/dashboard.html')
    else:
        return redirect(admin_login)
  

def admin_logout(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('admin_login')
    

def show_product(request):
    products = Product.objects.all()
    return render(request, 'adminside/show_product.html', {'products':products})


def users_list(request):
    users = UserProfile.objects.all()
    return render(request,'adminside/users_list.html', {'users': users})


def admin_users_block_unblock(request, id):
    user = UserProfile.objects.get(id = id )
    if user.is_blocked:
        user.is_blocked = False
        user.is_active = True
        user.save()
        messages.success(request, "User is Unblocked")
    else:
        user.is_active = False
        user.is_blocked = True
        user.save()
        messages.warning(request, "User is blocked")
    return redirect("adminside:users-list")
    

def categories(request):
    return render(request, 'adminside/categories.html')



    