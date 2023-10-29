from django.utils import timezone
from django.db import models
from userside.models import *

# Create your models here.

class PaymentMethod(models.Model):
   method_name = models.CharField(max_length=50)
   is_active = models.BooleanField(default=True)
   created_at = models.DateTimeField(auto_now_add=True)

   def __str__(self):
      return self.method_name


class Payment(models.Model):
  PAYMENT_STATUS_CHOICES =(
        ("PENDING", "Pending"),
        ("FAILED", "Failed"),
        ("SUCCESS", "Success"),
      )
  user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
  payment_id = models.CharField(max_length=100)
  payment_order_id = models.CharField(max_length=100,null=True,blank=True)
  payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
  amount_paid = models.CharField(max_length=100)#total amount paid
  status = models.CharField(max_length=100)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.payment_id
    

class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
        ('Returned', 'Returned'),
    )

    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=20)
    shipping_address = models.ForeignKey(
        AddressBook, on_delete=models.SET_NULL, null=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS, default='New')
    ip = models.CharField(max_length=20, blank=True)
    is_ordered = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'Order {self.order_number}'


class OrderProduct(models.Model):
    order =  models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation = models.ManyToManyField(Variation)
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=50)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at =  models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now = True)




    def  __str__(self):
        return self.product.Product_name
    

