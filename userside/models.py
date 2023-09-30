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
    


class Category(models.Model):
    Category_name = models.CharField(max_length=25, unique=True)
    slug = models.SlugField(max_length=25, unique = False)
    description = models.TextField(max_length=100, blank=True)
    is_available = models.BooleanField(default=True)
    soft_deleted = models.BooleanField(default=False)
    Category_image = models.ImageField(upload_to='photos/category', blank=True)


    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.Category_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.Category_name)
        super().save(*args, **kwargs)



class Product_image(models.Model):
    image = models.ImageField(upload_to='photos/product', null = True, verbose_name='Product Image 1')
    image2 = models.ImageField(upload_to='photos/product', null = True, verbose_name='Product Image 2')
    image3 = models.ImageField(upload_to='photos/product', null = True,verbose_name='Product Image 3')
    image4 = models.ImageField(upload_to='photos/product', null = True,verbose_name='Product Image 4')
    image5 = models.ImageField(upload_to='photos/product', null = True,verbose_name='Product Image 5')

    def __str__(self):
        return self.image.name 




class Product(models.Model):
    Product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=100, unique = True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_image = models.ForeignKey(Product_image, on_delete=models.CASCADE)
    brand = models.CharField(max_length=200, blank=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    max_price = models.DecimalField(max_digits=10, decimal_places=2)
    quatity = models.IntegerField()
    is_available = models.BooleanField(default=True)
    soft_deleted = models.BooleanField(default=False)


    def __str__(self):
        return self.Product_name 

