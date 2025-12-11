#!/usr/bin/env python
"""
Payment System Test Script
Run this to verify payment configuration
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freshtrack_project.settings')
django.setup()

from django.conf import settings
from freshtrack_app.models import Purchase, Product, User
import requests

def test_configuration():
    """Test SSLCommerz configuration"""
    print("\n" + "="*60)
    print("🔍 PAYMENT SYSTEM CONFIGURATION CHECK")
    print("="*60 + "\n")
    
    # Check settings
    print("📋 Configuration:")
    print(f"   Store ID: {settings.SSLCOMMERZ_STORE_ID}")
    print(f"   Password: {'*' * len(settings.SSLCOMMERZ_STORE_PASSWORD)}")
    print(f"   Sandbox Mode: {settings.SSLCOMMERZ_IS_SANDBOX}")
    print(f"   API URL: {settings.SSLCOMMERZ_API_URL}")
    print(f"   Validation URL: {settings.SSLCOMMERZ_VALIDATION_URL}")
    
    # Validate credentials
    print("\n✅ Credentials Check:")
    if settings.SSLCOMMERZ_STORE_ID == 'your_store_id_here':
        print("   ⚠️  WARNING: Using placeholder Store ID")
        print("   📝 Update settings.py or .env with real credentials")
    elif settings.SSLCOMMERZ_STORE_ID == 'testbox':
        print("   ✓ Using default sandbox credentials (testbox)")
    else:
        print(f"   ✓ Using custom Store ID: {settings.SSLCOMMERZ_STORE_ID}")
    
    # Test API connectivity
    print("\n🌐 Testing SSLCommerz API Connectivity:")
    try:
        test_data = {
            'store_id': settings.SSLCOMMERZ_STORE_ID,
            'store_passwd': settings.SSLCOMMERZ_STORE_PASSWORD,
            'total_amount': '100',
            'currency': 'BDT',
            'tran_id': 'TEST_' + str(uuid.uuid4().hex[:8]),
            'success_url': 'http://example.com/success',
            'fail_url': 'http://example.com/fail',
            'cancel_url': 'http://example.com/cancel',
            'cus_name': 'Test User',
            'cus_email': 'test@test.com',
            'cus_phone': '01700000000',
            'cus_add1': 'Dhaka',
            'cus_city': 'Dhaka',
            'cus_country': 'Bangladesh',
            'product_name': 'Test Product',
            'product_category': 'Test',
            'product_profile': 'general',
            'shipping_method': 'NO',
        }
        
        response = requests.post(
            settings.SSLCOMMERZ_API_URL,
            data=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'SUCCESS':
                print("   ✓ API connection successful!")
                print(f"   ✓ Gateway URL received: {result.get('GatewayPageURL')[:50]}...")
            else:
                print(f"   ⚠️  API returned status: {result.get('status')}")
                print(f"   Reason: {result.get('failedreason', 'Unknown')}")
        else:
            print(f"   ✗ API returned status code: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("   ✗ Connection timeout - check internet connection")
    except requests.exceptions.RequestException as e:
        print(f"   ✗ Connection error: {str(e)}")
    except Exception as e:
        print(f"   ✗ Unexpected error: {str(e)}")

def check_database():
    """Check database status"""
    print("\n" + "="*60)
    print("💾 DATABASE CHECK")
    print("="*60 + "\n")
    
    # Check users
    buyer_count = User.objects.filter(role__role='buyer').count()
    seller_count = User.objects.filter(role__role='seller').count()
    
    print(f"👥 Users:")
    print(f"   Buyers: {buyer_count}")
    print(f"   Sellers: {seller_count}")
    
    # Check products
    total_products = Product.objects.count()
    approved_products = Product.objects.filter(status='approved').count()
    
    print(f"\n📦 Products:")
    print(f"   Total: {total_products}")
    print(f"   Approved: {approved_products}")
    print(f"   Available for purchase: {approved_products}")
    
    # Check purchases
    total_purchases = Purchase.objects.count()
    successful = Purchase.objects.filter(payment_status='success').count()
    pending = Purchase.objects.filter(payment_status='initiated').count()
    failed = Purchase.objects.filter(payment_status='failed').count()
    
    print(f"\n💰 Purchases:")
    print(f"   Total: {total_purchases}")
    print(f"   Successful: {successful}")
    print(f"   Pending: {pending}")
    print(f"   Failed: {failed}")
    
    # Recent purchases
    if total_purchases > 0:
        recent = Purchase.objects.order_by('-purchased_at')[:3]
        print(f"\n📋 Recent Purchases:")
        for p in recent:
            status_emoji = {
                'success': '✓',
                'failed': '✗',
                'initiated': '⏳',
                'canceled': '⛔'
            }.get(p.payment_status, '?')
            print(f"   {status_emoji} {p.product_name} - {p.payment_status} - ৳{p.total_price}")

def print_test_instructions():
    """Print testing instructions"""
    print("\n" + "="*60)
    print("🧪 READY TO TEST")
    print("="*60 + "\n")
    
    print("Quick Test Steps:")
    print("1. Start server: python manage.py runserver")
    print("2. Go to: http://127.0.0.1:8000/")
    print("3. Login as buyer")
    print("4. Click 'Buy Now' on any product")
    print("5. Select payment method")
    print("6. Click 'Proceed to Payment'")
    print("\nTest Card:")
    print("   Number: 4111 1111 1111 1111")
    print("   Expiry: 12/25")
    print("   CVV: 123")
    print("\nExpected Result:")
    print("   ✓ Redirect to SSLCommerz payment page")
    print("   ✓ Complete payment")
    print("   ✓ See success message")
    print("   ✓ Stock reduced")
    print("   ✓ Purchase in buyer history")
    
    print("\n📚 Documentation:")
    print("   - PAYMENT_SETUP.md - Complete setup guide")
    print("   - QUICK_PAYMENT_TEST.md - Quick testing guide")
    print("   - PAYMENT_FIX_SUMMARY.md - What was fixed")
    
    print("\n" + "="*60)

def main():
    print("\n🚀 FreshTrack Payment System Test\n")
    
    try:
        test_configuration()
        check_database()
        print_test_instructions()
        
        print("\n✅ Configuration check complete!")
        print("🎯 You're ready to test payments!\n")
        
    except Exception as e:
        print(f"\n❌ Error during check: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    import uuid
    sys.exit(main())
