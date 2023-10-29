from typing import Self
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin,Group, Permission
from django.db import models
from django.utils.text import slugify

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('username', email.split('@')[0])

        return self.create_user(email, password, **extra_fields)


class UserProfile(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30,unique=True,blank=False)
    email = models.EmailField(unique=True)
    phone= models.CharField(max_length=15, blank=False,default='')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
   


    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email 
    
class AddressBook(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=30)
    phone = models.CharField(max_length=20)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    pincode = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_default = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.is_default:
            # Set is_default=False for other addresses of the same user
            AddressBook.objects.filter(user=self.user).exclude(
                pk=self.pk).update(is_default=False)
        super(AddressBook, self).save(*args, **kwargs)

    def get_user_full_address(self):
        address_parts = [self.address_line_1]
        if self.address_line_2:
            address_parts.append(self.address_line_2)
        address_parts.append(self.pincode)
        address_parts.extend([self.city, self.state, self.country])
        return ', '.join(address_parts)
    
    
  
    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def __str__(self):
        return self.name
    



class Category(models.Model):
    Category_name = models.CharField(max_length=25, unique=True)
    slug = models.SlugField(max_length=25, unique = False)
    description = models.TextField(max_length=100, blank=True)
    is_available = models.BooleanField(default=True)
    soft_deleted = models.BooleanField(default=False)
    Category_image = models.ImageField(upload_to='photos/category', blank=False)


    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.Category_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.Category_name)
        super().save(*args, **kwargs)






class Product(models.Model):
    Product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=100, unique = True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    main_image = models.ImageField(upload_to='photos/product')
    brand = models.CharField(max_length=200, blank=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    max_price = models.DecimalField(max_digits=10, decimal_places=2) 
    quantity = models.IntegerField() 
    is_available = models.BooleanField(default=True)
    soft_deleted = models.BooleanField(default=False)
   
    
    def __str__(self):
        return self.Product_name 
    

class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category = 'color', is_active = True)
    
    def sizes(self):
        return super(VariationManager, self).filter(variation_category = 'size', is_active = True)


variation_category_choice = (
    ('color', 'color'),
    ('size', 'size'), 

)



class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value

    
class Product_image(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE,default=1)
    image2 = models.ImageField(upload_to='photos/product', null = True,verbose_name='Product Image 2')
    image3 = models.ImageField(upload_to='photos/product', null = True,verbose_name='Product Image 3')
    image4 = models.ImageField(upload_to='photos/product', null = True,verbose_name='Product Image 4')
    image5 = models.ImageField(upload_to='photos/product', null = True,verbose_name='Product Image 5')

    def __str__(self):
        return self.image2.name 

