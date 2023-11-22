from django.urls import reverse
from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from carts.models import CartItem
from orders.forms import addressbook_form
from wallet.models import Wallet, WalletTransaction
from .models import Coupon, Order, PaymentMethod, Payment, OrderProduct
from userside.models import Product, Variation
from django.views.decorators.cache import cache_control
from userside.models import *
from django.conf import settings
from django.contrib.auth.decorators import login_required
import razorpay
from django.utils import timezone
from django.db.models import Sum
from django.http import JsonResponse
import datetime

# Create your views here.


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def order_summary(request, total=0, quantity=0):
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
        
        coupon_discount = 0
        request.session['coupon'] = 0
        coupon_code = request.POST.get('coupon')
        coupon = None
        
        if coupon_code:
            try:
              coupon = Coupon.objects.get(coupon_code = coupon_code)
              coupon_discount = coupon.discount
              request.session['coupon'] = float(coupon_discount)
              total -= float(coupon_discount)
            except Exception as e:
              
              print(e)

              
        user = UserProfile.objects.get(email=request.user)
        try:
            address = AddressBook.objects.get(user=user, is_default=True)
        except Exception:
            messages.warning(request, 'Please Set Default Shipping Address')
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        wallet = Wallet.objects.get_or_create(user=request.user, is_active=True)


        if request.POST.get('wallet_balance'):
          wallet_selected = int(request.POST.get('wallet_balance'))
          print("haeiiiiii")
          print(wallet_selected)
        else:
          wallet_selected = request.POST.get('wallet_balance')

        if wallet_selected == 1:
          wallet = Wallet.objects.get(user=request.user, is_active=True)
          if wallet.balance <= total:
            total -= wallet.balance
            # order.wallet_discount = wallet.balance
          #   # order.order_total = order_total
          else:
          #   order.wallet_discount = order_total
          #   order.order_total = 0
              total = 0
        else:
           pass
          # order.order_total = order_total
          # order.wallet_discount=0

        subtotal = float(total)+request.session['coupon']
        context = {
            'paymentmethods':PaymentMethod.objects.all(),
            'cart_items':cart_items,
            'total':float(total),
            'subtotal':subtotal,
            'coupon_dis':request.session['coupon'],
            'address':address,
            'wallet':wallet,
            }
        return render(request, 'orders/order-summary.html', context)
            
    
    else:
       return redirect('checkout')
    


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

  # tax = (2*total)/100
  # grand_total = total + tax

  order = None
  payment_method = None 
  if request.method == "POST":
    user = current_user
    if request.POST.get('wallet_balance'):
      wallet_selected = int(request.POST.get('wallet_balance'))
    else:
      wallet_selected = request.POST.get('wallet_balance')
      
    order_number = request.POST['order_number']
    
      # Use get() to provide a default value ('') if 'payment_option' is not in the request
    if not 'payment_option' in request.POST:
        messages.error(request, "Please choose a payment method")
        return redirect('order-summary')
    
    payment_option = request.POST['payment_option']
    payment_method = PaymentMethod.objects.get(method_name=payment_option)
    order_total = total
    tax = tax
    ip = request.META.get('REMOTE_ADDR')
    shipping_address = AddressBook.objects.get(user=current_user, is_default = True)
    
    order = Order.objects.create(user = user,  tax = tax, ip = ip, order_total = order_total, shipping_address = shipping_address )

    


    #generate order number
    yr = int(datetime.date.today().year)
    dt = int(datetime.date.today().strftime('%d'))
    mt = int(datetime.date.today().strftime('%m'))
    d = datetime.date(yr,mt,dt)
    current_date = d.strftime("%Y%m%d")
    order_number = current_date + str(order.id)
    order.order_number = order_number
    order.save()
    print(order)


    try:
      payment_method = PaymentMethod.objects.get(method_name=payment_option)
      order = Order.objects.get(user = request.user, is_ordered = False, order_number = order_number)
      print(order)
      print("order is here")
         #coupon
    except Exception as e:
      
      print(e)

    if order is not None:
            order.save()

    if wallet_selected == 1:
      wallet = Wallet.objects.get(user=request.user, is_active=True)
      if wallet.balance <= order_total:
        order_total -= wallet.balance
        order.wallet_discount = wallet.balance
        order.order_total = order_total
      else:
        order.wallet_discount = order_total
        order.order_total = 0
    else:
      # order.order_total = order_total
      order.wallet_discount=0
    order.save()

    if request.session['coupon']:
       value = request.session['coupon']
       print(value)
       order.coupon_discount = int(request.session['coupon'])
       order.order_total -=  order.coupon_discount
       print(f"yessssssss:{order.order_total}")
    else:
       order.order_total = order_total
    
    try:
      if total == 0:
        raise Exception  
      if payment_option == 'COD':
        payment = False
      elif payment_option == 'RAZORPAY':
        print(order.order_total)
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        payment = client.order.create({'amount':float(order.order_total)*100, "currency":"INR"})
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
      'total':total-order.coupon_discount,
      'success_url':success_url,
      'failed_url':failed_url,
      'payment_method':payment_method,
      'payment':payment,
      'address':address,
      'grandtotal': grand_total,
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
  discount = 0
  if request.session['coupon']:
      discount = int(request.session['coupon'])

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
        amount_paid = order.order_total-discount,
        status = 'SUCCESS'
      )
      payment.save()

      order.status = 'Accepted'
      order.payment = payment
      order.is_ordered = True
      order.save()

      wallet = Wallet.objects.get(user=request.user, is_active=True)
      wallet.balance = wallet.balance - order.wallet_discount
      wallet.save()

      wallet_transaction = WalletTransaction.objects.create(
        wallet = wallet,
        transaction_type = 'DEBIT',
        order = order,
        transaction_detail = str(order.order_number),
        amount = order.wallet_discount
      )
      wallet_transaction.save()

     

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

  elif method == 'RAZORPAY':
    order = Order.objects.get(user = request.user, is_ordered = False, order_number = order_id)
    payment_method_is_active = PaymentMethod.objects.filter(method_name = method, is_active = True)

    if payment_method_is_active.exists():
      payment = Payment(
        user = request.user,
        payment_id = payment_id,
        payment_order_id = payment_order_id,
        payment_method = payment_method_is_active[0],
        amount_paid = order.order_total-discount,
        status = 'SUCCESS',
      )
      payment.save()

      wallet = Wallet.objects.get(user=request.user, is_active = True)
      wallet.balance = wallet.balance - order.wallet_discount
      wallet.save()

      wallet_transaction = WalletTransaction.objects.create(
        wallet = wallet,
        transaction_type = 'DEBIT',
        order = order,
        transaction_detail = str(order.order_number),
        amount = order.wallet_discount
      )
      wallet_transaction.save()

      order.payment = payment
      order.is_ordered = True
      order.status = "Accepted"
      order.save()

      cart_items = CartItem.objects.filter(user = request.user)

      for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order= order
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
      request.session["payment_id"] = payment_id
      return redirect('payment-success-page')
      
    else:
      messages.error(request, "Invalid Payment Method Found")
      return redirect('payment-failed')
    
  elif method == 'WALLET':
    payment_method_is_active = PaymentMethod.objects.filter(method_name = method, is_active = True)
    order = Order.objects.get(user = request.user, is_ordered = False, order_number = order_id)

    payment = Payment(
      user = request.user,
      payment_order_id = order_id,
      payment_method = payment_method_is_active[0],
      amount_paid = order.order_total,
      payment_id = 'PID-WLT' + order_id,
      status = 'SUCCESS',
    )
    payment.save()

    wallet = Wallet.objects.get(user=request.user, is_active=True)
    wallet.balance = wallet.balance - order.wallet_discount
    wallet.save()

    wallet_transaction = WalletTransaction.objects.create(
      wallet = wallet,
      transaction_type = 'DEBIT',
      order = order,
      transaction_detail = str(order.order_number),
      amount = order.wallet_discount
      )
    wallet_transaction.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    cart_items = CartItem.objects.filter(user = request.user)

    for item in cart_items:
      orderproduct = OrderProduct()
      orderproduct.order= order
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
      request.session["payment_id"] = 'PID-WLT' + payment_id
      return redirect('orders:payment-success-page')
    
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


@login_required
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


@login_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def order_cancel_user(request,order_number):
  order = Order.objects.get(order_number=order_number)
  orderproduct = OrderProduct.objects.get(order=order)
  if not order.status == 'Cancelled':
    order.status = 'Cancelled'
    order.save()

    wallet = Wallet.objects.get(user=request.user, is_active=True)
    try:
      wallet.balance += float(order.order_total )
      wallet.save()
    except:
       pass

    wallet_transaction = WalletTransaction.objects.create(wallet=wallet,
                                                          transaction_type='CREDIT',
                                                          transaction_detail=str(order.order_number)+ 'CANCELLED',
                                                          amount = order.wallet_discount)
    wallet_transaction.save()

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



def get_weekly_sales():
    end_date = timezone.now()
    start_date = end_date - timezone.timedelta(days=7)

    return OrderProduct.objects.filter(
        order__created_at__range=(start_date, end_date)
    ).values('product__Product_name').annotate(weekly_sales=Sum('quantity'))



def get_monthly_sales():
    end_date = timezone.now()
    start_date = end_date - timezone.timedelta(days=30)

    return OrderProduct.objects.filter(
        order__created_at__range=(start_date, end_date)
    ).values('product__Product_name').annotate(monthly_sales=Sum('quantity'))



def get_yearly_sales():
    end_date = timezone.now()
    start_date = end_date - timezone.timedelta(days=365)

    return OrderProduct.objects.filter(
        order__created_at__range=(start_date, end_date)
    ).values('product__Product_name').annotate(yearly_sales=Sum('quantity'))



def sales_report(request):
    weekly_sales_data = list(get_weekly_sales().values('product__Product_name','weekly_sales'))  # Convert QuerySet to a list of dictionaries
    monthly_sales_data = list(get_monthly_sales().values('product__Product_name','monthly_sales'))
    yearly_sales_data = list(get_yearly_sales().values('product__Product_name','yearly_sales'))
    sales_data = {
        'weekly_sales': weekly_sales_data,
        'monthly_sales': monthly_sales_data,
        'yearly_sales': yearly_sales_data,
    }

    print(weekly_sales_data)
    return JsonResponse(sales_data, safe=False)