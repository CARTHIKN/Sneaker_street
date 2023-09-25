from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin,Group, Permission
from django.db import models

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
        return self.create_user(email, password, **extra_fields)


class UserProfile(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30,unique=True,blank=False)
    email = models.EmailField(unique=True)
    phone= models.CharField(max_length=15, blank=False,default='')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    groups = models.ManyToManyField(Group, verbose_name='groups', blank=True, related_name='user_profiles')
    user_permissions = models.ManyToManyField(Permission, verbose_name='user permissions', blank=True, related_name='user_profiles')


    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email 