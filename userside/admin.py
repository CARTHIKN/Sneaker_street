from django.contrib import admin

from .models import UserProfile,Category,Product,Product_image

admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Product_image)
