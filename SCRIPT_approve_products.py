import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freshtrack_project.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from freshtrack_project.freshtrack_app.models import Product

# Approve all pending products
products = Product.objects.filter(status='pending')
count = 0
for product in products:
    product.status = 'approved'
    product.save()
    count += 1
    print(f"✓ Approved: {product.name} (${product.price})")

print(f"\n✅ Approved {count} products!")

# Show all approved products
approved = Product.objects.filter(status='approved')
print(f"\nTotal Approved Products: {approved.count()}")
for product in approved:
    print(f"  - {product.name} by {product.seller.company_name}")
