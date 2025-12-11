#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freshtrack_project.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from freshtrack_project.freshtrack_app.models import Product, SellerProfile

print("=== Product Database Check ===\n")
print(f"Total products: {Product.objects.count()}")
print(f"Approved: {Product.objects.filter(status='approved').count()}")
print(f"Pending: {Product.objects.filter(status='pending').count()}")
print(f"Rejected: {Product.objects.filter(status='rejected').count()}")
print(f"Expired: {Product.objects.filter(status='expired').count()}")

print("\n=== All Products ===")
for product in Product.objects.all():
    print(f"ID: {product.id} | Name: {product.name} | Status: {product.status} | Seller: {product.seller.user.username}")

print("\n=== Sellers ===")
for seller in SellerProfile.objects.all():
    product_count = seller.products.count()
    print(f"Seller: {seller.user.username} | Products: {product_count}")
