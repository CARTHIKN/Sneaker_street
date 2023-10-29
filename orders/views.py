from django.urls import reverse
from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from carts.models import CartItem
from orders.forms import addressbook_form
from .models import Order, PaymentMethod, Payment, OrderProduct
import datetime
from userside.models import Product, Variation
from django.views.decorators.cache import cache_control
from userside.models import *
# Create your views here.


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def order_summary(request, total=0, quantity=0):
    print('oiwjgrasasfdhkajsfdhkasjdf')
    current_user = request.user

    #if the cart count is less than or equal to 0, then redirect back to landing page

    cart_items = CartItem.objects.filter(user = current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('landing')
    
    
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
        
    

    print(f'grand_total')


    
    if request.method == 'POST':
        user = UserProfile.objects.get(email=request.user)
        try:
            address = AddressBook.objects.get(user=user, is_default=True)
        except Exception:
            messages.warning(request, 'Please Set Default Shipping Address')
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


        context = {
            'paymentmethods':PaymentMethod.objects.all(),
            'cart_items':cart_items,
            'total':total,
            'address':address
            
            }
        return render(request, 'orders/order-summary.html', context)
            
    
    else:
        return redirect('landing')
    


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def place_order(request, total=0, quantity=0):
  current_user = request.user
  
  #if the cart count is less than equal to 0, then redirect back to shop
  cart_items = CartItem.objects.filter(user=current_user)
  cart_count = cart_items.count()
  if cart_count <=0:
    return redirect('landing')
  

  grand_total =  0
  tax = 0 
  for cart_item in cart_items:
    total += (cart_item.product.price * cart_item.quantity)
    quantity += cart_item.quantity

  tax = (2*total)/100
  grand_total = total + tax

  order = None
  payment_method = None 
  if request.method == "POST":

    user = current_user
    
    payment_option = request.POST['payment_option']
    payment_method = PaymentMethod.objects.get(method_name=payment_option)
    order_total = grand_total
    tax = tax
    ip = request.META.get('REMOTE_ADDR')
    shipping_address = AddressBook.objects.get(user=current_user, is_default = True)
    
    order = Order.objects.create(user = user, order_total = order_total, tax = tax, ip = ip, shipping_address = shipping_address )


    #generate order number
    yr = int(datetime.date.today().strftime('%Y'))
    dt = int(datetime.date.today().strftime('%d'))
    mt = int(datetime.date.today().strftime('%m'))
    d = datetime.date(yr,mt,dt)
    current_date = d.strftime("%Y%m%d")
    order_number = current_date + str(order.id)
    order.order_number = order_number
    order.shipping_address = shipping_address
    order.save()

    if not payment_option:
      messages.error(request, "please choose a payment method")
      return redirect('order_summary')

    try:
      payment_method = PaymentMethod.objects.get(method_name=payment_option)
      order = Order.objects.get(user = request.user, is_ordered = False, order_number = order_number)
         
    except Exception as e:
      
      print(e)

    if order is not None:
            order.save()
    

    try:
      if total == 0:
        raise Exception  
      if payment_option == 'COD':
        payment = False
      else:
        payment = False
    except:
      payment = False

    address = AddressBook.objects.get(user=current_user, is_default=True)
    success_url = request.build_absolute_uri(reverse('payment-success'))
    failed_url = request.build_absolute_uri(reverse('payment-failed'))   
    context = {
      'order':order,
      'cart_items':cart_items,
      'total':total,
      'success_url':success_url,
      'failed_url':failed_url,
      'payment_method':payment_method,
      'payment':payment,
      'address':address,
    }  
    print(payment)  
    print(payment_method) 
    print(order)  
    return render(request, 'orders/payments.html',context)
            
  order = Order.objects.get(id=id)
  context = {
    'order':order,
    'cart_items':cart_items,
    'total':total,
  }       
  return render(request, 'orders/payments.html',context)
  



def payment_success(request):
  method = request.GET.get('method')
  payment_id = request.GET.get('payment_id')
  payment_order_id = request.GET.get('payment_order_id')
  order_id = request.GET.get('order_id')

  if method == 'COD':
    try:
      order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_id)
    except Exception as e:
      print(e)
      return redirect('landing')
     
    payment_method_is_active =  PaymentMethod.objects.filter(method_name=method, is_active=True)
    
    if payment_method_is_active.exists():
      payment = Payment(
        user = request.user,
        payment_id = 'PID_COD'+ order_id,
        payment_order_id = order_id,
        payment_method = payment_method_is_active[0],
        amount_paid = order.order_total,
        status = 'SUCCESS'
      )
      payment.save()

      order.status = 'Accepted'
      order.payment = payment
      order.is_ordered = True
      order.save()

    #   wallet = Wallet.objects.get(user=request.user, is_active=True)
    #   wallet.balance = wallet.balance - order.wallet_discount
    #   wallet.save()

    #   wallet_transaction = WalletTransaction.objects.create(
    #     wallet = wallet,
    #     transaction_type = 'DEBIT',
    #     order = order,
    #     transaction_detail = str(order.order_number),
    #     amount = order.wallet_discount
    #   )
    #   wallet_transaction.save()

     

      cart_items = CartItem.objects.filter(user=request.user)

      for item in cart_items:
        print(item.variations.all()) 
        orderproduct = OrderProduct()
        orderproduct.order = order
        orderproduct.user = request.user
        orderproduct.product = item.product
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        orderproduct.variation.set(item.variations.all())

        product = Product.objects.get(id=item.product_id)
        product.quantity -= item.quantity
        product.save()

        

        
        

      CartItem.objects.filter(user=request.user).delete()

      request.session["order_number"] = order_id
      request.session["payment_id"] = 'PID-COD'+order_id
      return redirect('payment-success-page')
      
    else:
      messages.error(request, "Invalid Payment Method Found")
      return redirect('payment-failed')

#   elif method == 'RAZORPAY':
#     order = Order.objects.get(user = request.user, is_ordered = False, order_number = order_id)
#     payment_method_is_active = PaymentMethod.objects.filter(method_name = method, is_active = True)

    # if payment_method_is_active.exists():
    #   payment = Payment(
    #     user = request.user,
    #     payment_id = payment_id,
    #     payment_order_id = payment_order_id,
    #     payment_method = payment_method_is_active[0],
    #     amount_paid = order.order_total,
    #     status = 'SUCCESS',
    #   )
    #   payment.save()

    #   wallet = Wallet.objects.get(user=request.user, is_active = True)
    #   wallet.balance = wallet.balance - order.wallet_discount
    #   wallet.save()

    #   wallet_transaction = WalletTransaction.objects.create(
    #     wallet = wallet,
    #     transaction_type = 'DEBIT',
    #     order = order,
    #     transaction_detail = str(order.order_number),
    #     amount = order.wallet_discount
    #   )
    #   wallet_transaction.save()

    #   order.payment = payment
    #   order.is_ordered = True
    #   order.save()

    #   cart_items = CartItem.objects.filter(user = request.user)

    #   for item in cart_items:
    #     orderproduct = OrderProduct()
    #     orderproduct.order= order
    #     orderproduct.user = request.user
    #     orderproduct.product = item.product
    #     orderproduct.quantity = item.quantity
    #     orderproduct.product_price = item.product.price

    #     orderproduct.ordered = True
    #     orderproduct.save()
    #     orderproduct.variation.set(item.variations.all())

    #     product = Product.objects.get(id=item.product_id)
    #     product.quantity -= item.quantity
    #     product.save()

    #   CartItem.objects.filter(user=request.user).delete()

    #   request.session["order_number"] = order_id
    #   request.session["payment_id"] = payment_id
    #   return redirect('orders:payment-success-page')
      
    # else:
    #   messages.error(request, "Invalid Payment Method Found")
    #   return redirect('payment-failed')
    
#   elif method == 'WALLET':
#     payment_method_is_active = PaymentMethod.objects.filter(method_name = method, is_active = True)
#     order = Order.objects.get(user = request.user, is_ordered = False, order_number = order_id)

#     payment = Payment(
#       user = request.user,
#       payment_order_id = order_id,
#       payment_method = payment_method_is_active[0],
#       amount_paid = order.order_total,
#       payment_id = 'PID-WLT' + order_id,
#       status = 'SUCCESS',
#     )
#     payment.save()

#     wallet = Wallet.objects.get(user=request.user, is_active=True)
#     wallet.balance = wallet.balance - order.wallet_discount
#     wallet.save()

#     wallet_transaction = WalletTransaction.objects.create(
#       wallet = wallet,
#       transaction_type = 'DEBIT',
#       order = order,
#       transaction_detail = str(order.order_number),
#       amount = order.wallet_discount
#       )
#     wallet_transaction.save()

#     order.payment = payment
#     order.is_ordered = True
#     order.save()

#     cart_items = CartItem.objects.filter(user = request.user)

#     for item in cart_items:
#       orderproduct = OrderProduct()
#       orderproduct.order= order
#       orderproduct.user = request.user
#       orderproduct.product = item.product
#       orderproduct.quantity = item.quantity
#       orderproduct.product_price = item.product.price

#       orderproduct.ordered = True
#       orderproduct.save()
#       orderproduct.variation.set(item.variations.all())

#       product = Product.objects.get(id=item.product_id)
#       product.quantity -= item.quantity
#       product.save()

#       CartItem.objects.filter(user=request.user).delete()

#       request.session["order_number"] = order_id
#       request.session["payment_id"] = 'PID-WLT' + payment_id
#       return redirect('orders:payment-success-page')
    
  else:
    return redirect('user-profile')   
@cache_control(no_cache=True,must_revalidate=True,no_store=True)      
def payment_failed(request):
  return HttpResponse('failed')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def payment_success_page(request):

  order_id = request.session["order_number"]
  print(order_id)

  order = Order.objects.get(user = request.user,order_number = order_id)
 

  return render(request, 'orders/payment-success-page.html')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def user_order_details(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number)
    except Exception as e:
        print(e)
    ordered_products = OrderProduct.objects.filter(order=order)

    context = {               
        'order': order,
        'ordered_products': ordered_products,
    }
    return render(request, 'userprofile/order-details.html', context)


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def order_cancel_user(request,order_number):
  order = Order.objects.get(order_number=order_number)
  orderproduct = OrderProduct.objects.get(order=order)
  if not order.status == 'Cancelled':
    order.status = 'Cancelled'
    order.save()

    # wallet = Wallet.objects.get(user=request.user, is_active=True)
    # wallet.balance += float(order.order_total + order.wallet_discount)
    # wallet.save()

    # wallet_transaction = WalletTransaction.objects.create(wallet=wallet,
    #                                                       transaction_type='CREDIT',
    #                                                       transaction_detail=str(order.order_number)+ 'CANCELLED',
    #                                                       amount = order.wallet_discount)
    # wallet_transaction.save()

    for orderproduct in order.orderproduct_set.all():
      product = orderproduct.product
      product.quantity += orderproduct.quantity
      product.save()


    return redirect('user-order-details', order_number=order.order_number)
  else:
    return redirect('user-order-details', order_number=order.order_number)
  

def add_address(request):
    if request.method == "POST":
        form = addressbook_form(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
        else:
            print(form.non_field_errors())
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))




def default_address(request, id):
    address = AddressBook.objects.get(id=id)
    address.is_default = True
    address.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

def delete_address(request, id):
    address = AddressBook.objects.get(id=id)
    address.delete()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))