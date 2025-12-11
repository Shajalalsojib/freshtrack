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

# Get sellers
sellers = SellerProfile.objects.all()[:3]

if not sellers:
    print("❌ No sellers found! Please register sellers first.")
    sys.exit(1)

products_data = [
    ('Fresh Milk 1L', 2.99, 45, -2, 72),
    ('Organic Yogurt 500g', 3.49, 30, -1, 48),
    ('Fresh Bread Loaf', 1.99, 60, -0.5, 36),
    ('Cheese 500g', 5.99, 20, -5, 432),
    ('Butter 250g', 4.49, 15, -3, 240),
    ('Fresh Strawberries', 4.99, 25, -1, 4),
    ('Blueberries 250g', 5.99, 20, -1, 6),
    ('Bananas 6pack', 1.49, 50, -1, 7),
    ('Apples 1kg', 2.99, 40, -2, 240),
    ('Chicken Breast 500g', 7.99, 20, -1, 3),
    ('Salmon Fillet 300g', 12.99, 12, -1, 2),
    ('Spinach Bunch', 2.49, 30, -1, 3),
    ('Broccoli Crown', 2.99, 28, -1, 5),
    ('Carrots 1kg', 1.99, 40, -2, 432),
    ('Potatoes 2kg', 3.49, 35, -3, 720),
]

product_count = 0
for name, price, qty, days_old, hours_left in products_data:
    seller = sellers[product_count % len(sellers)]
    mfg_date = now + timedelta(days=days_old)
    expiry_date = mfg_date + timedelta(hours=hours_left)
    
    product = Product.objects.create(
        seller=seller,
        name=name,
        price=price,
        quantity=qty,
        manufacturing_date=mfg_date,
        expiry_datetime=expiry_date,
        status='approved'
    )
    product_count += 1
    remaining = product.remaining_hours()
    alert = product.alert_level()
    print(f"✓ {product_count}. {name} - {remaining}h remaining - {alert}")

print(f"\n✅ Added {product_count} products!")
