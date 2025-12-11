import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freshtrack_project.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from freshtrack_project.freshtrack_app.models import (
    Product, SellerProfile, UserRole, Review
)

def populate_data():
    print("🚀 Starting data population...")
    
    seller_users = []
    sellers = []
    
    for i in range(1, 6):
        username = f'seller{i}'
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=f'seller{i}@test.com',
                password='seller123'
            )
            UserRole.objects.create(user=user, role='seller')
            seller = SellerProfile.objects.create(
                user=user,
                company_name=f'Fresh Foods {i}',
                rating=4.5 - (i * 0.1),
                total_sales=1000 * i
            )
            seller_users.append(user)
            sellers.append(seller)
            print(f"✓ Created seller: {username}")
    
    for i in range(1, 4):
        username = f'buyer{i}'
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=f'buyer{i}@test.com',
                password='buyer123'
            )
            UserRole.objects.create(user=user, role='buyer')
            print(f"✓ Created buyer: {username}")
    
    now = timezone.now()
    products_data = [
        ('Fresh Milk 1L', 2.99, 45, -2, 72, 'approved'),
        ('Organic Yogurt 500g', 3.49, 30, -1, 48, 'approved'),
        ('Fresh Bread Loaf', 1.99, 60, -0.5, 36, 'approved'),
        ('Eggs 12 pack', 3.99, 25, -3, 360, 'approved'),
        ('Fresh Tomatoes 1kg', 2.49, 50, -1, 5, 'approved'),
        ('Organic Lettuce', 1.75, 40, -2, 3, 'approved'),
        ('Bell Peppers 3pack', 2.99, 35, -1, 120, 'approved'),
        ('Cheese 500g', 5.99, 20, -5, 432, 'approved'),
        ('Butter 250g', 4.49, 15, -3, 240, 'approved'),
        ('Whole Milk 2L', 3.49, 35, -2, 96, 'approved'),
        
        ('Fresh Strawberries', 4.99, 25, -1, 4, 'approved'),
        ('Blueberries 250g', 5.99, 20, -1, 6, 'approved'),
        ('Bananas 6pack', 1.49, 50, -1, 7, 'approved'),
        ('Apples 1kg', 2.99, 40, -2, 240, 'approved'),
        ('Oranges 1kg', 2.49, 35, -2, 216, 'approved'),
        ('Grapes 500g', 3.99, 22, -1, 5, 'approved'),
        ('Watermelon', 6.99, 10, -2, 168, 'approved'),
        ('Mangoes 2pack', 3.99, 18, -2, 5, 'approved'),
        ('Pineapple', 4.49, 12, -1, 240, 'approved'),
        ('Kiwi 6pack', 3.49, 15, -1, 240, 'approved'),
        
        ('Chicken Breast 500g', 7.99, 20, -1, 3, 'approved'),
        ('Ground Beef 500g', 8.99, 18, -1, 2, 'approved'),
        ('Salmon Fillet 300g', 12.99, 12, -1, 2, 'approved'),
        ('Shrimp 300g', 10.99, 15, -1, 3, 'approved'),
        ('Cod Fish 400g', 9.99, 14, -1, 4, 'approved'),
        ('Pork Chops 500g', 6.99, 16, -1, 3, 'approved'),
        ('Lamb Meat 500g', 10.99, 10, -1, 4, 'approved'),
        ('Turkey Breast 400g', 8.49, 13, -1, 3, 'approved'),
        ('Bacon 200g', 5.99, 22, -1, 8, 'approved'),
        ('Sausages 400g', 4.99, 25, -1, 6, 'approved'),
        
        ('Spinach Bunch', 2.49, 30, -1, 3, 'approved'),
        ('Broccoli Crown', 2.99, 28, -1, 5, 'approved'),
        ('Carrots 1kg', 1.99, 40, -2, 432, 'approved'),
        ('Potatoes 2kg', 3.49, 35, -3, 720, 'approved'),
        ('Onions 1kg', 1.49, 50, -2, 720, 'approved'),
        ('Garlic Bulb', 0.99, 60, -1, 240, 'approved'),
        ('Bell Peppers Red', 1.99, 30, -1, 120, 'approved'),
        ('Cucumbers', 1.49, 35, -1, 7, 'approved'),
        ('Zucchini 500g', 2.49, 20, -1, 10, 'approved'),
        ('Mushrooms 200g', 3.99, 18, -1, 4, 'approved'),
        
        ('Yogurt Parfait', 4.49, 15, -1, 5, 'approved'),
        ('Ice Cream 500ml', 5.99, 12, -1, 180, 'approved'),
        ('Cottage Cheese 500g', 3.99, 16, -2, 240, 'approved'),
        ('Mozzarella 250g', 4.99, 20, -3, 288, 'approved'),
        ('Cheddar Cheese 200g', 5.49, 18, -4, 336, 'approved'),
    ]
    
    product_count = 0
    for name, price, qty, days_old, hours_left, status in products_data:
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
            status=status
        )
        product_count += 1
        
        remaining = product.remaining_hours()
        alert = product.alert_level()
        print(f"✓ {product_count}. {name} - {remaining}h remaining - {alert}")
    
    buyer_users = User.objects.filter(role__role='buyer')
    for buyer in buyer_users:
        products = Product.objects.filter(status='approved').order_by('?')[:5]
        for product in products:
            if not Review.objects.filter(product=product, buyer=buyer).exists():
                Review.objects.create(
                    product=product,
                    buyer=buyer,
                    rating=(hash(f"{buyer.id}{product.id}") % 5) + 1,
                    comment=f"Great product from {product.seller.company_name}!"
                )
    
    print(f"\n✅ SUCCESS!")
    print(f"Created {product_count} products")
    print(f"Created {len(sellers)} sellers")
    print(f"Created {buyer_users.count()} buyers")
    print(f"\n🔓 Login Credentials:")
    print("SELLERS: seller1/seller123, seller2/seller123, etc.")
    print("BUYERS: buyer1/buyer123, buyer2/buyer123, buyer3/buyer123")
    print("\n📊 Product Status:")
    approved = Product.objects.filter(status='approved').count()
    print(f"Approved products: {approved}")
    print(f"Fresh (48+ hours): {Product.objects.filter(status='approved').filter(expiry_datetime__gt=now + timedelta(hours=48)).count()}")
    print(f"Warning (24-48 hours): {Product.objects.filter(status='approved').filter(expiry_datetime__lte=now + timedelta(hours=48)).filter(expiry_datetime__gt=now + timedelta(hours=24)).count()}")
    print(f"Expiring Soon (6-24 hours): {Product.objects.filter(status='approved').filter(expiry_datetime__lte=now + timedelta(hours=24)).filter(expiry_datetime__gt=now + timedelta(hours=6)).count()}")
    print(f"Urgent (< 6 hours): {Product.objects.filter(status='approved').filter(expiry_datetime__lte=now + timedelta(hours=6)).filter(expiry_datetime__gt=now).count()}")

if __name__ == '__main__':
    populate_data()
