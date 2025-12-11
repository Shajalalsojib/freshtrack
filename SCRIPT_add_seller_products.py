import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freshtrack_project.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from freshtrack_project.freshtrack_app.models import Product, SellerProfile

now = timezone.now()

# Get the first seller
seller = SellerProfile.objects.first()

if not seller:
    print("❌ No sellers found!")
    sys.exit(1)

# Add 2 products for the seller - PENDING APPROVAL
products_data = [
    ('Bread', 20.00, 1, -1, 72),
    ('Bread', 30.00, 1, -1, 72),
]

product_count = 0
for name, price, qty, days_old, hours_left in products_data:
    mfg_date = now + timedelta(days=days_old)
    expiry_date = mfg_date + timedelta(hours=hours_left)
    
    product = Product.objects.create(
        seller=seller,
        name=name,
        price=price,
        quantity=qty,
        manufacturing_date=mfg_date,
        expiry_datetime=expiry_date,
        status='pending'  # Pending approval
    )
    product_count += 1
    print(f"✓ {product_count}. {name} - ${price} - Status: Pending")

print(f"\n✅ Added {product_count} products (Pending Approval)!")
print(f"Seller: {seller.company_name}")
