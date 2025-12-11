import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freshtrack_project.settings')

sys.path.insert(0, os.path.dirname(__file__))

django.setup()

from django.contrib.auth.models import User
from freshtrack_project.freshtrack_app.models import UserRole, SellerProfile, Product
from django.utils import timezone
from datetime import timedelta

def create_sample_data():
    print("Creating sample data...")
    
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@freshtrack.com',
        password='admin123'
    )
    UserRole.objects.create(user=admin_user, role='admin')
    print("✓ Admin user created (username: admin, password: admin123)")
    
    buyer_user = User.objects.create_user(
        username='buyer1',
        email='buyer1@test.com',
        password='buyer123'
    )
    UserRole.objects.create(user=buyer_user, role='buyer')
    print("✓ Buyer user created (username: buyer1, password: buyer123)")
    
    buyer_user2 = User.objects.create_user(
        username='buyer2',
        email='buyer2@test.com',
        password='buyer123'
    )
    UserRole.objects.create(user=buyer_user2, role='buyer')
    print("✓ Buyer user created (username: buyer2, password: buyer123)")
    
    seller_user = User.objects.create_user(
        username='seller1',
        email='seller1@test.com',
        password='seller123'
    )
    UserRole.objects.create(user=seller_user, role='seller')
    seller = SellerProfile.objects.create(
        user=seller_user,
        company_name='Fresh Farms Co.',
        rating=4.5,
        total_sales=500
    )
    print("✓ Seller user created (username: seller1, password: seller123)")
    
    seller_user2 = User.objects.create_user(
        username='seller2',
        email='seller2@test.com',
        password='seller123'
    )
    UserRole.objects.create(user=seller_user2, role='seller')
    seller2 = SellerProfile.objects.create(
        user=seller_user2,
        company_name='Organic Produce Ltd.',
        rating=4.8,
        total_sales=750
    )
    print("✓ Seller user created (username: seller2, password: seller123)")
    
    now = timezone.now()
    
    products = [
        {
            'seller': seller,
            'name': 'Fresh Milk (1L)',
            'price': 2.50,
            'quantity': 50,
            'manufacturing_date': now - timedelta(days=2),
            'expiry_datetime': now + timedelta(hours=72),
            'status': 'approved'
        },
        {
            'seller': seller,
            'name': 'Organic Yogurt (500g)',
            'price': 3.99,
            'quantity': 30,
            'manufacturing_date': now - timedelta(days=1),
            'expiry_datetime': now + timedelta(hours=48),
            'status': 'approved'
        },
        {
            'seller': seller,
            'name': 'Fresh Bread (Loaf)',
            'price': 1.99,
            'quantity': 40,
            'manufacturing_date': now - timedelta(hours=12),
            'expiry_datetime': now + timedelta(hours=36),
            'status': 'approved'
        },
        {
            'seller': seller,
            'name': 'Eggs (12 pack)',
            'price': 3.50,
            'quantity': 25,
            'manufacturing_date': now - timedelta(days=3),
            'expiry_datetime': now + timedelta(days=15),
            'status': 'approved'
        },
        {
            'seller': seller2,
            'name': 'Fresh Tomatoes (1kg)',
            'price': 2.25,
            'quantity': 60,
            'manufacturing_date': now - timedelta(hours=24),
            'expiry_datetime': now + timedelta(hours=5),
            'status': 'approved'
        },
        {
            'seller': seller2,
            'name': 'Organic Lettuce (bunch)',
            'price': 1.75,
            'quantity': 45,
            'manufacturing_date': now - timedelta(hours=48),
            'expiry_datetime': now + timedelta(hours=2),
            'status': 'approved'
        },
        {
            'seller': seller2,
            'name': 'Bell Peppers (3 pack)',
            'price': 2.99,
            'quantity': 35,
            'manufacturing_date': now - timedelta(days=1),
            'expiry_datetime': now + timedelta(hours=120),
            'status': 'approved'
        },
        {
            'seller': seller,
            'name': 'Cheese (500g)',
            'price': 5.99,
            'quantity': 20,
            'manufacturing_date': now - timedelta(days=5),
            'expiry_datetime': now + timedelta(days=20),
            'status': 'pending'
        },
    ]
    
    for product_data in products:
        Product.objects.create(**product_data)
    
    print(f"✓ Created {len(products)} sample products")
    print("\n========================================")
    print("SAMPLE DATA CREATED SUCCESSFULLY!")
    print("========================================")
    print("\nTest Accounts:")
    print("\nADMIN:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\nBUYER:")
    print("  Username: buyer1")
    print("  Password: buyer123")
    print("  OR")
    print("  Username: buyer2")
    print("  Password: buyer123")
    print("\nSELLER:")
    print("  Username: seller1")
    print("  Password: seller123")
    print("  Company: Fresh Farms Co.")
    print("  OR")
    print("  Username: seller2")
    print("  Password: seller123")
    print("  Company: Organic Produce Ltd.")
    print("\nYou can now:")
    print("1. Visit http://localhost:8000/")
    print("2. Login with any of the above accounts")
    print("3. Browse and test the system")
    print("========================================")

if __name__ == '__main__':
    create_sample_data()
