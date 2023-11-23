from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from offers.models import CategoryOffer, ProductOffer
from userside.models import UserProfile, Product, Category, Product_image, Variation
from django.contrib.auth import authenticate,login,logout
from django.utils.text import slugify
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import user_passes_test
from orders.models import Coupon, Order, OrderProduct, variation_category_choice
from django.utils import timezone
from django.http import HttpResponseBadRequest
# Create your views here.

def is_superuser(user):
    return user.is_superuser

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_login(request):
    if request.user.is_authenticated and request.user.is_superuser :
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
                messages.error(request,'Invalid credentials')
                return render(request, 'adminside/admin_login.html')      
        else:
            return render(request, 'adminside/admin_login.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superuser)
def dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'adminside/dashboard.html')
    else:
        return redirect('adminside:admin-login')
    
  
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_logout(request):
   if request.user.is_authenticated:
        logout(request)
   return redirect('adminside:adminlogin')
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superuser)
def show_product(request):
    if request.user.is_authenticated:
        products = Product.objects.all()
        return render(request, 'adminside/show_product.html', {'products':products})
    else:
        return render(request, 'adminside/admin_login.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superuser)
def users_list(request):
    if request.user.is_authenticated:
        users = UserProfile.objects.all()
        return render(request,'adminside/users_list.html', {'users': users})
    else:
        return render(request, 'adminside/admin_login.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superuser)
def admin_users_block_unblock(request, id):
    if request.user.is_authenticated:
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
@user_passes_test(is_superuser)
def categories(request):
    if request.user.is_authenticated:

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
    if request.user.is_authenticated:
        category = get_object_or_404(Category, pk=category_id)
        category.soft_deleted = not category.soft_deleted  # Toggle the soft_deleted field
        category.save()
        
        return redirect('adminside:categories')



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superuser)
def add_product(request):
    if request.user.is_authenticated:
        categories = Category.objects.all()
        products = Product.objects.all()
        
        if request.method == "POST":
            product_name = request.POST['product_name']

            try:
                price = float(request.POST['price'])
                max_price = float(request.POST['max_price'])
                quantity = int(request.POST['quantity'])

                if price < 0 or max_price < 0 or quantity < 0:
                    messages.error(request, 'Price, max price, and quantity must be non-negative.')
                else:
                    if Product.objects.filter(Product_name=product_name).exists():
                        messages.error(request, 'A product with this name already exists.')
                        
                    slug = slugify(product_name)
                    category_id = request.POST['category']
                    category = Category.objects.get(id=category_id)
                    brand = request.POST['brand']
                    description = request.POST['description']
                    price = request.POST['price']
                    main_image = request.FILES.get('main_image')
                    additional_images = request.FILES.getlist('additional_images')
                    max_price = request.POST['max_price']
                    quantity = request.POST['quantity']
                    is_available = request.POST.get('is_available') 
                    if main_image == None:
                        messages.warning(request, "Upload a main img")
                        return redirect('adminside:add-product')
                    if len(additional_images) != 4 or any(image is None for image in additional_images):
                         messages.error(request, 'You must provide exactly 4 additional images, and none of them should be empty.')
                         return redirect('adminside:add-product')
                    if is_available == 'on' or is_available == 'True':
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
                        # product.save()

                        product_image = Product_image()

                        for i, image in enumerate(additional_images[:4]):
                            

                            if i == 0:
                                product_image.image2 = image
                            elif i == 1:
                                product_image.image3 = image
                            elif i == 2:
                                product_image.image4 = image
                            elif i == 3:
                                product_image.image5 = image
                                
                            
                        # product_image.image2 = image2
                        # product_image.image3 = image3
                        # product_image.image4 = image4
                        # product_image.image5 = image5

                        product.save()
                        product_image.product = product
                        product_image.save()
                        return redirect('adminside:show-product') 

            except ValueError:
                messages.error(request, 'Invalid price, max price, or quantity.')      

             

        return render(request, "adminside/addproduct.html", {"categories": categories })
    else:
        return render(request, 'adminside/admin_login.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superuser)
def edit_product(request, product_id):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, pk=product_id)
        categories = Category.objects.all()
        return render(request, 'adminside/addproduct.html', {'product': product, "categories": categories })
    else:
        return render(request, 'adminside/admin_login.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superuser)
def update_product(request, product_id):
    if request.user.is_authenticated:
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
@user_passes_test(is_superuser)
def delete_product(request, product_id):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, pk=product_id)      
        product.soft_deleted = not product.soft_deleted
        product.save()       
        return redirect('adminside:show-product') 
    else:
        return render(request, 'adminside/admin_login.html')
    


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@user_passes_test(is_superuser)
def admin_orders(request):
    
    ordered_products = OrderProduct.objects.all()

    return render(request, 'adminside/orders.html', {'ordered_products':ordered_products})



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@user_passes_test(is_superuser)
def admin_orders_details(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number)
        ordered_products = OrderProduct.objects.filter(order=order)
    except Exception as e:
        print(e)
    

    context = {               
        'order': order,
        'ordered_products': ordered_products,
    }
    return render(request, 'adminside/admin_order_details.html', context)

def delivered_order(request, order_number):
    order = Order.objects.get(order_number=order_number)
    order.status = 'Delivered'
    order.save()
    return redirect('adminside:admin-orders')





def add_variations(request):
   
    product = Product.objects.all()

    if request.method == 'POST':
        product_id = request.POST['product']
        product = Product.objects.get(id=product_id)
        variation_category = request.POST['category']
        variation_value = request.POST['variation_value']
        is_active = request.POST.get('is_active') == 'True' 
        if is_active == 'on':
            is_active = False
        else:
            is_active = True

        Variation.objects.create(product = product, variation_category = variation_category, variation_value = variation_value, is_active = is_active )

        return redirect('adminside:dashboard')

    

    context = {
        'products': product,
        'variation_category_choices': variation_category_choice,
    }

    return render(request, 'adminside/add_variations.html', context)


def add_coupon(request):
    if request.method == "POST":
        coupon_code = request.POST['coupon_code']
        discount = request.POST['discount']
        valid_from = request.POST['valid_from']
        valid_to = request.POST['valid_to']
        active = request.POST['active'] == 'True' 
        if active == 'on':
            active = False
        else:
            active = True
        minimum_amount = request.POST['minimum_amount']
        if int(discount)  <= 0 or  int(minimum_amount) <= 0:
            messages.error(request, 'discount and minimumum amount cannnot be zero or negative values')
            return render(request, 'adminside/add_coupon.html')
        
        valid_from = timezone.make_aware(
            timezone.datetime.strptime(valid_from.replace('T', ' '), 
            '%Y-%m-%d %H:%M'))
        valid_to = timezone.make_aware(timezone.datetime.strptime(valid_to.replace('T', ' '), '%Y-%m-%d %H:%M'))


        if valid_to <= valid_from:
            messages.error(request, 'Valid to date cannot be lesser than or equal to Valid from date')
            return render(request, 'adminside/add_coupon.html')

        coupon = Coupon.objects.create(coupon_code=coupon_code, discount=discount, valid_from=valid_from, valid_to=valid_to, active=active, minimum_amount=minimum_amount)

        coupon.save()
        messages.success(request, 'coupon added successfully')
        return redirect('adminside:dashboard')
    return render(request, 'adminside/add_coupon.html')




def add_product_offer(request):
    products = Product.objects.all()
    product_offers = ProductOffer.objects.all()

    if request.method == 'POST':
        offer_name = request.POST.get('offer_name')
        expire_date = request.POST.get('expire_date')
        product_ids = request.POST.getlist('product')  # Assuming 'product' is a multiple select field
        discount_percentage = request.POST.get('discount_percentage')
        product_offer_image = request.FILES.get('product_offer_image')
        is_active = request.POST.get('is_active') 
        if is_active == 'on':
            is_active = True
        else:
            is_active = False

        # Check if the offer name already exists
        if ProductOffer.objects.filter(offer_name=offer_name).exists():
            messages.error(request, 'Offer name already exists. Please choose a different name.')
            return redirect('adminside:add_product_offer')
        
        
        selected_date = timezone.datetime.strptime(expire_date, '%Y-%m-%d').date()
        today = timezone.now().date()


        if selected_date <= today:
            messages.error(request, 'Expiration date should be greater than today\'s date.')
            return redirect('adminside:add_product_offer')

        # Check if the product list is empty
        if not product_ids:
            messages.error(request, 'Product list cannot be empty. Please select at least one product.')
            return redirect('adminside:add_product_offer')

        # Check if discount is greater than 0
        if int(discount_percentage) <= 0:
            messages.error(request, 'Discount should be greater than zero.')
            return redirect('adminside:add_product_offer')
        

       

        # Create the ProductOffer instance
        product_offer = ProductOffer(
            offer_name=offer_name,
            expire_date=expire_date,
            discount_percentage=discount_percentage,
            product_offer_image=product_offer_image,
            is_active=is_active
        )
        product_offer.save()

        # Add products to the many-to-many field
        product_offer.product.set(product_ids)

        messages.success(request, 'Product offer added successfully.')
        return redirect('adminside:add_product_offer') 

    context = {
        'products': products,
        'product_offers': product_offers,
    }
    return render(request, 'adminside/product_offer.html', context)




def edit_product_offer(request, offer_id):
    product_offer = get_object_or_404(ProductOffer, id=offer_id)
    products = Product.objects.all()
    print('asdjfhkjassdfhkk')
    if request.method == 'POST':
        # Update the fields with the new values
        offer_name = request.POST.get('offer_name')
        expire_date = request.POST.get('expire_date')
        product_ids = request.POST.getlist('product') 
        discount_percentage = request.POST.get('discount_percentage')
        product_offer_image = request.FILES.get('product_offer_image')
        is_active = request.POST.get('is_active') 
        if is_active == 'on':
            is_active = True
        else:
            is_active = False

        # Validate the input
        if ProductOffer.objects.exclude(id=offer_id).filter(offer_name=offer_name).exists():
            messages.error(request, 'Offer name already exists. Please choose a different name.')
            return redirect('adminside:edit_product_offer', offer_id=offer_id)

        selected_date = timezone.datetime.strptime(expire_date, '%Y-%m-%d').date()
        today = timezone.now().date()

        if selected_date <= today:
            messages.error(request, 'Expiration date should be greater than today\'s date.')
            return redirect('adminside:edit_product_offer', offer_id=offer_id)

        if not product_ids:
            messages.error(request, 'Product list cannot be empty. Please select at least one product.')
            return redirect('adminside:edit_product_offer', offer_id=offer_id)

        if int(discount_percentage) <= 0:
            messages.error(request, 'Discount should be greater than zero.')
            return redirect('adminside:edit_product_offer', offer_id=offer_id)

        # If validation passes, update the product_offer
        product_offer.offer_name = offer_name
        product_offer.expire_date = expire_date
        product_offer.discount_percentage = discount_percentage
        product_offer.product_offer_image = product_offer_image
        product_offer.is_active = is_active
        
        # Update other fields as neede
        product_offer.save()

        product_offer.product.set(product_ids)
        
        messages.success(request, 'Product offer updated successfully.')
        return redirect('adminside:add_product_offer')

    context = {
        'products': products,
        'product_offer': product_offer,
    }

    return render(request, 'adminside/edit_product_offer.html', context)



def add_category_offer(request):
    if request.method == 'POST':
        # Get data from the request
        offer_name = request.POST.get('offer_name')
        expire_date = request.POST.get('expire_date')
        category_id = request.POST.get('category')
        discount_percentage = request.POST.get('discount_percentage')
        category_offer_image = request.FILES.get('category_offer_image')
        is_active = request.POST.get('is_active')
        if is_active == 'on':
            is_active = True
        else:
            is_active = False

        # Validate data
        if not offer_name or not expire_date or not category_id or not discount_percentage:
            messages.error(request, "Invalid data. Please fill in all required fields.")
            return redirect('adminside:add_category_offer')
        
        if CategoryOffer.objects.filter(offer_name=offer_name).exists():
            messages.error(request, f"The offer name '{offer_name}' already exists. Please choose a different name.")
            return redirect('adminside:add_category_offer')

        # Additional validation
        try:
            # Check if expire_date is a valid date
            expire_date = timezone.datetime.strptime(expire_date, '%Y-%m-%d').date()
            if expire_date < timezone.now().date():
                messages.error(request, "Invalid date format or expiration date should be in the future.")
                return redirect('adminside:add_category_offer')
        except ValueError:
            pass
           

        # Validate discount_percentage
        try:
            discount_percentage = int(discount_percentage)
            if discount_percentage <= 0 or discount_percentage > 100:
                messages.error(request, "Discount percentage should be an integer between 1 and 100.")
                return redirect('adminside:add_category_offer')
        except ValueError:
            pass
            

        # Validate category_id
        
        category_id = int(category_id)
        category = Category.objects.get(pk=category_id)

        # Handle slug creation
        category_offer_slug = slugify(offer_name)
        counter = CategoryOffer.objects.filter(category_offer_slug__istartswith=category_offer_slug).count()
        if counter > 0:
            category_offer_slug = f'{category_offer_slug}-{counter}'

        # Create CategoryOffer instance
        category_offer = CategoryOffer(
            offer_name=offer_name,
            expire_date=expire_date,
            category=category,
            discount_percentage=discount_percentage,
            category_offer_slug=category_offer_slug,
            category_offer_image=category_offer_image,
            is_active=is_active
        )
        category_offer.save()
        messages.success(request, 'Category offer added successfully.')

        return redirect('adminside:category_offer_list')  

    # Render the form for GET requests
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'adminside/add_category_offer.html', context)



def category_offer_list(request):
    category_offers = CategoryOffer.objects.all()

    context = {
        'category_offers':category_offers,

    }
    return render(request, 'adminside/category_offer_list.html', context)


def edit_category_offer(request, category_offer_id):
    print("yessssss")
    category_offer = get_object_or_404(CategoryOffer, pk=category_offer_id)
    if request.method == "POST":
        
        offer_name = request.POST.get('offer_name')
        expire_date = request.POST.get('expire_date')
        category_id = request.POST.get('category')
        discount_percentage = request.POST.get('discount_percentage')
        category_offer_image = request.FILES.get('category_offer_image')
        is_active = request.POST.get('is_active')
        if is_active == 'on':
            is_active = True
        else:
            is_active = False

        if not offer_name or not expire_date or not category_id or not discount_percentage:
                messages.error(request, "Invalid data. Please fill in all required fields.")
                return redirect('adminside:edit_category_offer', category_offer_id= category_offer_id)
        
        if CategoryOffer.objects.exclude(id=category_offer_id).filter(offer_name=offer_name).exists():
            messages.error(request, f"The offer name '{offer_name}' already exists. Please choose a different name.")
            return redirect('adminside:edit_category_offer',  category_offer_id= category_offer_id)


        try:
            # Check if expire_date is a valid date
            expire_date = timezone.datetime.strptime(expire_date, '%Y-%m-%d').date()
            if expire_date < timezone.now().date():
                messages.error(request, "Invalid date format or expiration date should be in the future.")
                return redirect('adminside:edit_category_offer',  category_offer_id= category_offer_id)
        except ValueError:
            pass

        try:
            discount_percentage = int(discount_percentage)
            if discount_percentage <= 0 or discount_percentage > 100:
                messages.error(request, "Discount percentage should be an integer between 1 and 100.")
                return redirect('adminside:edit_category_offer',  category_offer_id= category_offer_id)
        except ValueError:
            pass
        
        category_id = int(category_id)
        category = Category.objects.get(pk=category_id)
        
        category_offer_slug = slugify(offer_name)
        counter = CategoryOffer.objects.filter(category_offer_slug__istartswith=category_offer_slug).count()
        if counter > 0:
            category_offer_slug = f'{category_offer_slug}-{counter}'


        category_offer.offer_name = offer_name
        category_offer.expire_date = expire_date
        category_offer.discount_percentage = discount_percentage
        category_offer.category_offer_image = category_offer_image
        category_offer.category = category
        category_offer.category_offer_slug = category_offer_slug
        category_offer.is_active = is_active
        
        category_offer.save()
        messages.success(request, 'Category offer Updated successfully.')

        return redirect('adminside:category_offer_list')  



    context = {
        'categories': Category.objects.all(),
        'edit_mode': True,  # Add this flag to distinguish between adding and editing
        'category_offer': category_offer,  # Pass the CategoryOffer instance to the template
    }
    return render(request, 'adminside/add_category_offer.html', context)