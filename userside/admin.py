from django.contrib import admin

from .models import UserProfile,Category,Product,Product_image,Variation, AddressBook

class VariationAdmin(admin.ModelAdmin):
    list_display =('product', 'variation_category', 'variation_value', 'is_active')
    list_editable =('is_active',)

admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Product_image)
admin.site.register(Variation,VariationAdmin)
admin.site.register(AddressBook)

