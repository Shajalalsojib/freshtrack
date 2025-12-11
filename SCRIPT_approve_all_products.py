import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freshtrack_project.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from freshtrack_project.freshtrack_app.models import Product

# Approve all pending products
updated = Product.objects.filter(status='pending').update(status='approved')
print(f"✅ Updated {updated} products from 'pending' to 'approved'")

# Verify
approved_count = Product.objects.filter(status='approved').count()
pending_count = Product.objects.filter(status='pending').count()
print(f"Approved products: {approved_count}")
print(f"Pending products: {pending_count}")
