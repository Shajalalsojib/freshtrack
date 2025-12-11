from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Product, SellerProfile, UserRole, Review, Alert

class UserRegistrationTest(TestCase):
    def test_register_as_buyer(self):
        User.objects.create_user(username='buyer1', email='buyer@test.com', password='testpass123')
        user = User.objects.get(username='buyer1')
        self.assertEqual(user.email, 'buyer@test.com')

    def test_register_as_seller(self):
        user = User.objects.create_user(username='seller1', email='seller@test.com', password='testpass123')
        UserRole.objects.create(user=user, role='seller')
        SellerProfile.objects.create(user=user, company_name='Test Company')
        seller = SellerProfile.objects.get(user=user)
        self.assertEqual(seller.company_name, 'Test Company')

class ProductTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='seller1', password='testpass123')
        UserRole.objects.create(user=self.user, role='seller')
        self.seller = SellerProfile.objects.create(user=self.user, company_name='Test Company')
        
        now = timezone.now()
        self.product = Product.objects.create(
            seller=self.seller,
            name='Fresh Milk',
            price=2.50,
            quantity=100,
            manufacturing_date=now - timedelta(days=1),
            expiry_datetime=now + timedelta(hours=24),
            status='approved'
        )

    def test_remaining_hours_calculation(self):
        hours = self.product.remaining_hours()
        self.assertGreater(hours, 0)
        self.assertLessEqual(hours, 24)

    def test_alert_level_warning(self):
        level = self.product.alert_level()
        self.assertEqual(level, 'soon')

    def test_product_expiry(self):
        expired_product = Product.objects.create(
            seller=self.seller,
            name='Expired Milk',
            price=1.00,
            quantity=50,
            manufacturing_date=timezone.now() - timedelta(days=5),
            expiry_datetime=timezone.now() - timedelta(hours=1),
            status='approved'
        )
        self.assertEqual(expired_product.remaining_hours(), 0)
        self.assertEqual(expired_product.alert_level(), 'expired')

class ReviewTest(TestCase):
    def setUp(self):
        self.seller_user = User.objects.create_user(username='seller1', password='testpass123')
        UserRole.objects.create(user=self.seller_user, role='seller')
        self.seller = SellerProfile.objects.create(user=self.seller_user, company_name='Test Company')
        
        now = timezone.now()
        self.product = Product.objects.create(
            seller=self.seller,
            name='Fresh Milk',
            price=2.50,
            quantity=100,
            manufacturing_date=now - timedelta(days=1),
            expiry_datetime=now + timedelta(hours=24),
            status='approved'
        )
        
        self.buyer = User.objects.create_user(username='buyer1', password='testpass123')

    def test_add_review(self):
        review = Review.objects.create(
            product=self.product,
            buyer=self.buyer,
            rating=5,
            comment='Great product!'
        )
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Great product!')

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        UserRole.objects.create(user=self.user, role='buyer')

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

    def test_register_page(self):
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)
