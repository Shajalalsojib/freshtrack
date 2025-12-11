from django.contrib import admin
from .models import Product, SellerProfile, Review, Alert, UserRole

admin.site.register(Product)
admin.site.register(SellerProfile)
admin.site.register(Review)
admin.site.register(Alert)
admin.site.register(UserRole)
