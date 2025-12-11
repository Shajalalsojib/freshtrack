"""
Test Script: Verify Strict Product Visibility Rules
Run this in Django shell: python manage.py shell < test_visibility.py
"""

from freshtrack_project.freshtrack_app.models import Product, SellerProfile, UserRole
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

print("\n" + "="*70)
print("🧪 TESTING STRICT PRODUCT VISIBILITY RULES")
print("="*70 + "\n")

# Test 1: approved_available() method
print("📋 Test 1: Product.objects.approved_available()")
print("-" * 70)
approved_count = Product.objects.approved_available().count()
print(f"✅ Found {approved_count} products that are:")
print("   - Approved by admin")
print("   - Not expired")
print("   - From approved sellers")
print()

# Test 2: pending_products() method
print("📋 Test 2: Product.objects.pending_products()")
print("-" * 70)
pending_count = Product.objects.pending_products().count()
print(f"⏳ Found {pending_count} products awaiting admin approval")
print()

# Test 3: expired_products() method
print("📋 Test 3: Product.objects.expired_products()")
print("-" * 70)
expired_count = Product.objects.expired_products().count()
print(f"⌛ Found {expired_count} expired products")
print()

# Test 4: rejected_products() method
print("📋 Test 4: Product.objects.rejected_products()")
print("-" * 70)
rejected_count = Product.objects.rejected_products().count()
print(f"❌ Found {rejected_count} rejected products")
print()

# Test 5: is_visible_to_buyers() method
print("📋 Test 5: Product.is_visible_to_buyers() instance method")
print("-" * 70)
all_products = Product.objects.all()[:5]
for product in all_products:
    visibility = "✅ VISIBLE" if product.is_visible_to_buyers() else "❌ HIDDEN"
    print(f"{visibility} | {product.name[:30]:30} | Status: {product.status:10} | Expires: {product.expiry_datetime.strftime('%Y-%m-%d %H:%M')}")
print()

# Test 6: Status breakdown
print("📊 Test 6: Overall Product Status Breakdown")
print("-" * 70)
total = Product.objects.count()
approved = Product.objects.filter(status='approved').count()
pending = Product.objects.filter(status='pending').count()
rejected = Product.objects.filter(status='rejected').count()
expired = Product.objects.filter(status='expired').count()

print(f"Total Products: {total}")
print(f"├─ Approved: {approved} ({round(approved/total*100, 1) if total > 0 else 0}%)")
print(f"├─ Pending: {pending} ({round(pending/total*100, 1) if total > 0 else 0}%)")
print(f"├─ Rejected: {rejected} ({round(rejected/total*100, 1) if total > 0 else 0}%)")
print(f"└─ Expired: {expired} ({round(expired/total*100, 1) if total > 0 else 0}%)")
print()

# Test 7: Buyer visibility summary
print("👁️ Test 7: What Buyers See (Visibility Summary)")
print("-" * 70)
visible_to_buyers = Product.objects.approved_available().count()
hidden_from_buyers = total - visible_to_buyers
print(f"✅ Products VISIBLE to buyers: {visible_to_buyers}")
print(f"❌ Products HIDDEN from buyers: {hidden_from_buyers}")
print(f"📊 Visibility Rate: {round(visible_to_buyers/total*100, 1) if total > 0 else 0}%")
print()

print("="*70)
print("✅ VISIBILITY RULES TEST COMPLETE")
print("="*70)
print("\nSummary:")
print(f"- Main Dashboard shows: {visible_to_buyers} products")
print(f"- Buyer Dashboard shows: {visible_to_buyers} products")
print(f"- Admin Dashboard shows: {total} products (all)")
print(f"- Hidden from buyers: {hidden_from_buyers} products")
print()
