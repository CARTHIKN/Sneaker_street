from decimal import Decimal
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from orders.models import Coupon
from userside.models import AddressBook, Product,Variation
from . models import Cart, CartItem
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
# Create your views here.
from django.contrib.auth.decorators import user_passes_test

def is_customer(user):
    return not user.is_superuser and not user.is_staff

def customer_login_required(view_func):
    decorated_view = login_required(view_func, login_url='user_login')
    return user_passes_test(is_customer)(decorated_view)

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart



@cache_control(no_cache=True, must_revalidate=True, no_store=True)  
def add_cart(request, id):
    current_user = request.user
    product = Product.objects.get(id=id)

    if current_user.is_authenticated:
        selected_variations = []

        if request.method == "POST":
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    selected_variations.append(variation)
                except Variation.DoesNotExist:
                    pass

            # Get the cart items for the current user
            cart_items = CartItem.objects.filter(product=product, user=current_user)

            matching_cart_item = None

            for cart_item in cart_items:
                # Check if the selected variations match the variations in the cart
                if list(cart_item.variations.all()) == selected_variations:
                    matching_cart_item = cart_item
                    break

            # If a matching cart item is found, increment its quantity
            if matching_cart_item:
                if matching_cart_item.quantity < product.quantity:
                    matching_cart_item.quantity += 1
                    product.quantity -= 1
                    matching_cart_item.save()
                else:
                    messages.warning(request, "This product is out of stock.")
                return redirect('cart')

            # If no matching cart item is found, create a new one
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user
            )
            
            cart_item.variations.add(*selected_variations)
            cart_item.save()

            return redirect('cart')
        else:
            messages.info(request, "The product is out of stock.")
            return redirect('cart')


        
    #if the user is not authenticated    
    else:       
        product_variation = []
        if request.method == "POST":
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass    

        if product.quantity > 0:
            try:
                cart=Cart.objects.get(cart_id=_cart_id(request))#get the cart using cart_id present in the session
            except Cart.DoesNotExist:
                cart=Cart.objects.create(cart_id=_cart_id(request))
            cart.save()

            is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()

            if is_cart_item_exists:
                cart_item = CartItem.objects.filter(product=product, cart=cart)

                #existing_variations -> database
                #current_variation -> product_variation
                #item_id -> database

                ex_var_list = []
                id = []
                for item in cart_item:
                    existing_variation = item.variations.all()
                    ex_var_list.append(list(existing_variation))
                    id.append(item.id)

                if product_variation in ex_var_list:
                    #increase the cart item quantity
                    index = ex_var_list.index(product_variation)
                    item_id = id[index]
                    item = CartItem.objects.get(product=product, id=item_id)

                    if item.quantity < product.quantity:
                        item.quantity += 1
                        item.save()
                    else:
                        messages.warning(request, "This product is out of stock.")
                else:
                    item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                    if len(product_variation) > 0:
                        item.variations.clear()
                        item.variations.add(*product_variation)
                    item.save()
            else:
                cart_item = CartItem.objects.create(
                    product = product,
                    quantity = 1,
                    cart = cart,
                )
                if len(product_variation) > 0:
                    cart_item.variations.clear()
                    cart_item.variations.add(*product_variation)
                cart_item.save()        
            return redirect('cart')
        else:
            messages.info(request, "The product is out of stock.")
            return redirect('cart')


def remove_cart(request, product_id, cart_item_id):
    
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user = request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart = cart, id=cart_item_id)
            
        if cart_item.quantity >1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
    
    product = get_object_or_404(Product, id = product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user = request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart = cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')






def cart(request, total=0, quantity=0, cart_items=None, tax=0, grand_total=0):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user, is_active = True).order_by('-id')
        else: 
            cart = Cart.objects.get(cart_id =_cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart, is_active = True).order_by('-id')
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        # tax = (2 * total)/100
        # grand_total = total + tax
    except:
        pass

    context = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,
    }


    return render(request, 'cart/cart.html', context)


@customer_login_required
def checkout(request, total=0, quantity=0, cart_items=None, tax=0, grand_total=0):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user, is_active = True)
        else: 
            cart = Cart.objects.get(cart_id =_cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart, is_active = True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        # tax = (2 * total)/100
        # grand_total = total + tax
    except:
        pass

    coupon = None
    avlb_coupons = Coupon.objects.filter(active = True)
    coupon_discount = Decimal(0)

    try:
        addresses = AddressBook.objects.filter(user=request.user,is_active=True)
    except Exception:
        messages.warning(request, 'Please Set Default Shipping Address')
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


    context = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,
        'addresses' : addresses,
        'coupon': coupon,
        'coupon_discount': float(coupon_discount),
        'available_coupons':avlb_coupons,

    }
    return render(request, 'cart/checkout.html',context)