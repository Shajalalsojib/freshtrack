# Strict Product Visibility Rules - Implementation Guide

## Overview
This document explains the strict visibility rules implemented in FreshTrack to ensure only approved, non-expired products from approved sellers are visible to buyers and on the main dashboard.

---

## 🎯 Visibility Rules Summary

### Products Visible to Buyers & Main Dashboard
A product is visible ONLY when ALL these conditions are met:
1. ✅ Product `status = 'approved'` (approved by admin)
2. ✅ Product is NOT expired (`expiry_datetime > now`)
3. ✅ Seller is approved (`seller.user.role.is_approved = 'approved'`)

### Products Hidden from Buyers
Products are HIDDEN if ANY of these conditions apply:
- ❌ Status is `'pending'` (awaiting admin approval)
- ❌ Status is `'rejected'` (rejected by admin)
- ❌ Status is `'expired'` OR `expiry_datetime <= now`
- ❌ Seller is not approved (`pending` or `rejected`)

---

## 📋 Code Implementation

### 1. Custom Model Manager (models.py)

Added `ProductManager` class with convenient filtering methods:

```python
class ProductManager(models.Manager):
    """Custom manager for Product model with visibility filtering"""
    
    def approved_available(self):
        """
        Returns only products that are:
        1. Approved by admin (status='approved')
        2. Not expired (expiry_datetime > now)
        3. From approved sellers (seller is approved)
        
        Use this for buyer-facing views and public product listings.
        """
        return self.filter(
            status='approved',
            expiry_datetime__gt=timezone.now(),
            seller__user__role__is_approved='approved'
        ).select_related('seller', 'seller__user', 'seller__user__role')
    
    def pending_products(self):
        """Returns products awaiting admin approval"""
        return self.filter(status='pending').select_related('seller', 'seller__user')
    
    def approved_products(self):
        """Returns all approved products (including expired)"""
        return self.filter(status='approved').select_related('seller', 'seller__user')
    
    def rejected_products(self):
        """Returns rejected products"""
        return self.filter(status='rejected').select_related('seller', 'seller__user')
    
    def expired_products(self):
        """Returns expired products"""
        return self.filter(
            Q(status='expired') | Q(expiry_datetime__lte=timezone.now())
        ).select_related('seller', 'seller__user')
```

**Applied to Product model:**
```python
class Product(models.Model):
    # ... fields ...
    
    # Custom manager
    objects = ProductManager()
```

### 2. Product Model Method (models.py)

Added `is_visible_to_buyers()` instance method:

```python
def is_visible_to_buyers(self):
    """
    Determines if this product should be visible to buyers.
    Returns True only if:
    1. Product is approved
    2. Product is not expired
    3. Seller is approved
    """
    try:
        return (
            self.status == 'approved' and
            timezone.now() < self.expiry_datetime and
            self.seller.user.role.is_approved == 'approved'
        )
    except:
        return False
```

**Usage in templates:**
```django
{% if product.is_visible_to_buyers %}
    <!-- Show product -->
{% endif %}
```

### 3. Home View (views.py)

**BEFORE:**
```python
# Old approach - less strict
approved_products = Product.objects.filter(
    status='approved',
    seller__user__role__is_approved='approved'
).order_by('-created_at')[:12]

for product in approved_products:
    if product.remaining_hours() <= 0:
        product.status = 'expired'
        product.save()
```

**AFTER:**
```python
# New approach - strict visibility with custom manager
approved_products = Product.objects.approved_available().order_by('-created_at')[:12]
```

**Benefits:**
- ✅ Automatically filters non-expired products
- ✅ Uses optimized select_related for performance
- ✅ Single source of truth for visibility logic
- ✅ No need for manual expiry checking loop

### 4. Buyer Dashboard View (views.py)

**BEFORE:**
```python
approved_products = Product.objects.filter(
    status='approved',
    seller__user__role__is_approved='approved',
    expiry_datetime__gt=timezone.now()
)
```

**AFTER:**
```python
# STRICT VISIBILITY: Only show approved + non-expired products from approved sellers
approved_products = Product.objects.approved_available()
```

### 5. Product Detail View (views.py)

**BEFORE:**
```python
product = get_object_or_404(
    Product, 
    id=product_id, 
    status='approved',
    seller__user__role__is_approved='approved'
)
```

**AFTER:**
```python
# STRICT VISIBILITY: Only show approved + non-expired products from approved sellers
product = get_object_or_404(
    Product.objects.approved_available(),
    id=product_id
)
```

---

## 🔄 Product Lifecycle & Visibility Flow

### 1. Seller Adds Product
```
Status: pending
Visible to: Seller only (in their dashboard)
Visible on main/home: ❌ NO
Visible to buyers: ❌ NO
```

### 2. Admin Approves Product
```
Status: approved
Visible to: Everyone (if not expired)
Visible on main/home: ✅ YES (if not expired)
Visible to buyers: ✅ YES (if not expired)
Action: Product instantly appears everywhere
```

### 3. Admin Rejects Product
```
Status: rejected
Visible to: Seller only (marked as rejected)
Visible on main/home: ❌ NO
Visible to buyers: ❌ NO
```

### 4. Product Expires
```
Status: expired (or expiry_datetime <= now)
Visible to: Seller only (in expired list)
Visible on main/home: ❌ NO
Visible to buyers: ❌ NO
Action: Auto-removed from all buyer-facing pages
```

### 5. Seller Rejected by Admin
```
All seller's products: Hidden/Rejected
Visible on main/home: ❌ NO
Visible to buyers: ❌ NO
Action: All products disappear immediately
```

---

## 🧪 Testing Checklist

### Test Case 1: Pending Product
- [ ] Add new product as seller
- [ ] Check main/home dashboard → Should NOT appear
- [ ] Check buyer dashboard → Should NOT appear
- [ ] Check seller dashboard → Should appear as "Pending"

### Test Case 2: Admin Approval
- [ ] Admin approves pending product
- [ ] Refresh main/home dashboard → Should appear immediately
- [ ] Check buyer dashboard → Should appear immediately
- [ ] Buyers can now purchase it

### Test Case 3: Expired Product
- [ ] Wait for product to expire OR manually set expiry to past
- [ ] Check main/home dashboard → Should disappear
- [ ] Check buyer dashboard → Should disappear
- [ ] Check seller dashboard → Should show as "Expired"

### Test Case 4: Rejected Product
- [ ] Admin rejects a product
- [ ] Check main/home dashboard → Should NOT appear
- [ ] Check buyer dashboard → Should NOT appear
- [ ] Check seller dashboard → Should show as "Rejected"

### Test Case 5: Unapproved Seller
- [ ] Set seller's `is_approved = 'pending'`
- [ ] Check main/home dashboard → ALL seller's products should disappear
- [ ] Check buyer dashboard → ALL seller's products should disappear

### Test Case 6: Product Detail Page
- [ ] Try accessing product detail URL for pending product → 404 error
- [ ] Try accessing product detail URL for expired product → 404 error
- [ ] Try accessing product detail URL for approved product → Works

---

## 📊 Database Query Optimization

All visibility queries use `select_related()` for optimal performance:

```python
Product.objects.approved_available()
# Executes: SELECT ... FROM product 
#           INNER JOIN seller ON ...
#           INNER JOIN user ON ...
#           INNER JOIN role ON ...
# Result: Single database query instead of N+1 queries
```

**Performance Benefits:**
- ✅ Reduces database queries from N+1 to 1
- ✅ Faster page load times
- ✅ Better scalability with many products

---

## 🔐 Security Considerations

1. **No Direct Product Access:** Product detail pages verify visibility rules
2. **Admin-Only Views:** Admin dashboard shows all products with filtering
3. **Seller Isolation:** Sellers can only see their own products
4. **Buyer Protection:** Buyers never see pending/rejected/expired products

---

## 🎨 Template Usage

### Using Custom Manager in Views
```python
# Good - Use approved_available()
products = Product.objects.approved_available()

# Bad - Manual filtering (error-prone)
products = Product.objects.filter(status='approved', expiry_datetime__gt=timezone.now())
```

### Using Instance Method in Templates
```django
{% for product in products %}
    {% if product.is_visible_to_buyers %}
        <div class="product-card">
            {{ product.name }}
        </div>
    {% endif %}
{% endfor %}
```

---

## 📱 Views Affected

| View | Visibility Rule Applied |
|------|-------------------------|
| `home()` | ✅ Approved + Non-expired + Approved sellers only |
| `buyer_dashboard()` | ✅ Approved + Non-expired + Approved sellers only |
| `product_detail()` | ✅ Approved + Non-expired + Approved sellers only |
| `admin_dashboard()` | ℹ️ Shows ALL products (for moderation) |
| `seller_dashboard()` | ℹ️ Shows seller's own products (all statuses) |

---

## 🚀 Quick Reference

### Add New Buyer-Facing View
```python
def new_buyer_view(request):
    # Always use approved_available() for buyer-facing views
    products = Product.objects.approved_available()
    # ... rest of logic ...
```

### Check Product Visibility
```python
# In view
if product.is_visible_to_buyers():
    # Show to buyer
else:
    # Hide or show 404
```

### Admin Moderation View
```python
def admin_view(request):
    # Show ALL products for moderation
    all_products = Product.objects.all()
    pending = Product.objects.pending_products()
    approved = Product.objects.approved_products()
    rejected = Product.objects.rejected_products()
    expired = Product.objects.expired_products()
```

---

## ✅ Implementation Complete

All visibility rules are now enforced across:
- ✅ Main/Home Dashboard
- ✅ Buyer Dashboard
- ✅ Product Detail Pages
- ✅ Product Listings
- ✅ Search Results

**No pending, rejected, or expired products will appear to buyers or on the main dashboard!**
