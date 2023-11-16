from django.shortcuts import render
from razorpay import Order
from carts.models import CartItem

from wallet.models import Wallet
from django.http import JsonResponse 

# Create your views here.


def wallet(request):
  wallet,created = Wallet.objects.get_or_create(user=request.user, is_active=True)
  context = {
    'wallet': wallet
  }
  return render(request, 'userprofile/wallet.html', context)


def get_wallet_grand_total(request):
    print("hellooo")
    order_number = request.GET.get('order_number')
    check = request.GET.get('check')
    if check:
        
        wallet = Wallet.objects.get(user=request.user,is_active=True)
        cart_items = CartItem.objects.filter(user = request.user)
        total = 0 
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)

        if request.session['coupon']:
            coupon_discount = int(request.session['coupon'])
            total -=  coupon_discount
           

        grand_total = total
        print(grand_total)
        wallet_balance = wallet.balance  
        wallet_dis = 0
        if check=='true':  
            if wallet.balance <= grand_total  :  
                grand_total = grand_total- wallet.balance   
                wallet_dis = wallet.balance
                wallet_balance = 0
            else:
                wallet_dis = grand_total
                wallet_balance = wallet.balance - grand_total
                grand_total = 0


        
                    
            return JsonResponse({"status": "success", "grand_total":grand_total,"wallet_balance":wallet_balance, "wallet_dis":wallet_dis})
        else:
            return JsonResponse({"status": "success", "grand_total":grand_total,"wallet_balance":wallet_balance, "wallet_dis":wallet_dis})
    else:
            print("hello")
            return JsonResponse({"status": "success", "grand_total":12334,"wallet_balance":1205})
