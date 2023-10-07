from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from userside.models import UserProfile, Product, Category, Product_image
from django.contrib.auth import authenticate,login,logout
from django.utils.text import slugify
from django.views.decorators.cache import cache_control
# Create your views here.

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_login(request):
    if 'email' in request.session:
    # if request.user.is_superuser:
        return render(request, 'adminside/dashboard.html')
    else:
        if request.method == "POST":
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(request, email=email , password=password)
            if user is not None and user.is_superuser:
                request.session['email'] = email
                return redirect('adminside:dashboard')
            else :
                messages.success(request,'Invalid credentials')
                return redirect(admin_login)      
        else:
            return render(request, 'adminside/admin_login.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dashboard(request):
    if 'email' in request.session:
        return render(request, 'adminside/dashboard.html')
    else:
        return redirect('adminside:admin-login')
    
  
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_logout(request):
    if 'email' in request.session:
        request.session.flush()
    return redirect('adminside:admin-login')
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def show_product(request):
    if 'email' in request.session:
        products = Product.objects.all()
        return render(request, 'adminside/show_product.html', {'products':products})
    else:
        return render(request, 'adminside/admin_login.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def users_list(request):
    if 'email' in request.session:
        users = UserProfile.objects.all()
        return render(request,'adminside/users_list.html', {'users': users})
    else:
        return render(request, 'adminside/admin_login.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_users_block_unblock(request, id):
    if 'email' in request.session:
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
    else:
        return render(request, 'adminside/admin_login.html')
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def categories(request):
    if 'email' in request.session:

        categories = Category.objects.all()

        if request.method == 'POST':
            category_name = request.POST['category_name']
            slug = slugify(category_name)
            description = request.POST['description']
            is_available = request.POST.get('is_available') == 'true'  
            soft_deleted = request.POST.get('soft_deleted', False)  
            # Check if the category name is empty or already exists
            if not category_name:
                messages.error(request, 'Category name should not be empty.')
            elif Category.objects.filter(Category_name=category_name).exists():
                messages.error(request, 'Category with this name already exists.')
            else:
                # Handle category image upload
                category_image = request.FILES.get('category_image')
                
                
                # Create and save the category
                category = Category(
                    Category_name=category_name,
                    slug=slug,
                    description=description,
                    is_available=is_available,
                    soft_deleted=soft_deleted,
                    Category_image=category_image  # Assign the uploaded image
                )
                category.save()
                messages.success(request, 'Category added successfully!')
                return redirect("adminside:categories")  # Redirect to the category list view

        return render(request, 'adminside/categories.html', {"categories" : categories})
    else:
        return render(request, 'adminside/admin_login.html')



def toggle_soft_delete(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    category.soft_deleted = not category.soft_deleted  # Toggle the soft_deleted field
    category.save()
    
    return redirect('adminside:categories')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_product(request):
    if 'email' in request.session:
        categories = Category.objects.all()
        products = Product.objects.all()
        
        if request.method == "POST":
            product_name = request.POST['product_name']
            if Product.objects.filter(Product_name=product_name).exists():
                messages.error(request, 'A product with this name already exists.')
                
            slug = slugify(product_name)
            category_id = request.POST['category']
            category = Category.objects.get(id=category_id)
            brand = request.POST['brand']
            description = request.POST['description']
            price = request.POST['price']
            main_image = request.FILES.get('main_image')
            max_price = request.POST['max_price']
            quantity = request.POST['quantity']
            is_available = request.POST.get('is_available') == 'True' 
            if is_available == 'on':
                is_available = True
            else:
                is_available = False 
            soft_deleted = request.POST.get('is_available', False) 
            if soft_deleted == 'on':
                soft_deleted = True
            else:
                soft_deleted = False

            product = Product(
                Product_name = product_name,
                slug = slug,
                category = category, 
                brand = brand, 
                description = description,
                price =  price,
                main_image = main_image,
                max_price = max_price,
                quantity = quantity,
                is_available = is_available,
                soft_deleted = soft_deleted
                )
            product.save()

            product_image = Product_image()
            product_image.image2 = request.FILES.get('image2')
            product_image.image3 = request.FILES.get('image3')
            product_image.image4 = request.FILES.get('image4')
            product_image.image5 = request.FILES.get('image5')

            product.save()
            product_image.product = product
            product_image.save()

            return redirect('adminside:show-product')  

        return render(request, "adminside/addproduct.html", {"categories": categories })
    else:
        return render(request, 'adminside/admin_login.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_product(request, product_id):
    if 'email' in request.session:
        product = get_object_or_404(Product, pk=product_id)
        categories = Category.objects.all()
        return render(request, 'adminside/addproduct.html', {'product': product, "categories": categories })
    else:
        return render(request, 'adminside/admin_login.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_product(request, product_id):
    if 'email' in request.session:
        if request.method == 'POST':
            product = get_object_or_404(Product, pk=product_id)
            
            # Update the product data based on form inputs
            product.Product_name = request.POST['product_name']
            product.description = request.POST['description']
            product.slug = slugify(product.Product_name)
            category_id = request.POST['category']
            product.category = Category.objects.get(id=category_id)
            product.brand = request.POST['brand']
            product.description = request.POST['description']
            product.price = request.POST['price']
            product.main_image = request.FILES.get('main_image')
            product.max_price = request.POST['max_price']
            quantity_value = request.POST['quantity']
            product.quantity = quantity_value
            is_available = request.POST.get('is_available')
            if is_available == 'on':
                product.is_available = True
            else:
                product.is_available = False 
            soft_deleted = request.POST.get('soft_deleted')
            if soft_deleted == 'on':
                product.soft_deleted = True
            else:
                product.soft_deleted = False

            main_image = request.FILES.get('main_image')
            if main_image:
                product.main_image = main_image         
        
            product.save()
            
            return redirect('adminside:show-product')
    else:
        return render(request, 'adminside/admin_login.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_product(request, product_id):
    if 'email' in request.session:
        product = get_object_or_404(Product, pk=product_id)      
        product.soft_deleted = not product.soft_deleted
        product.save()       
        return redirect('adminside:show-product') 
    else:
        return render(request, 'adminside/admin_login.html')