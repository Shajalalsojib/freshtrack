# 🚫 Seller Rejection & Product Cascade System

## Overview
Complete seller rejection logic that automatically hides/removes all products when admin rejects a seller.

---

## 🎯 Features Implemented

### 1. **Admin Rejection Cascade**
- When admin rejects a seller, all their products are automatically set to `status='rejected'`
- Products become invisible to buyers immediately
- Seller loses access to dashboard

### 2. **Seller Dashboard Access Control**
- Rejected sellers cannot access `/seller/` dashboard
- Redirected to home with error message
- Pending sellers also blocked until approved

### 3. **Product Visibility Filtering**
- **Home Page**: Only shows products from approved sellers
- **Buyer Dashboard**: Only shows products from approved sellers  
- **Product Detail**: Only accessible for products from approved sellers
- Filter: `seller__user__role__is_approved='approved'`

### 4. **Re-approval Logic**
- If admin re-approves a seller, their products are restored to `pending` status
- Admin must review and approve each product again individually
- Ensures quality control after re-approval

---

## 📋 Model Changes

### **UserRole Model** (`models.py`)
```python
class UserRole(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')
    is_approved = models.CharField(max_length=20, choices=APPROVAL_STATUS, default='pending')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)  # NEW FIELD
    
    def is_seller_active(self):
        """Check if this is an active approved seller"""
        return self.role == 'seller' and self.is_approved == 'approved'
```

### **SellerProfile Model** (`models.py`)
```python
class SellerProfile(models.Model):
    # ... existing fields ...
    
    def is_active(self):
        """Check if seller is approved and can sell products"""
        try:
            return self.user.role.is_approved == 'approved'
        except:
            return False
    
    def hide_all_products(self):
        """Hide all products when seller is rejected"""
        self.products.update(status='rejected')
    
    def restore_products(self):
        """Restore products to pending when seller is re-approved"""
        self.products.filter(status='rejected').update(status='pending')
```

---

## 🔧 View Changes

### **1. Admin Reject User** (`views.py`)
```python
@login_required
def reject_user(request, user_id):
    # ... permission checks ...
    
    user = get_object_or_404(User, id=user_id)
    user_role = get_object_or_404(UserRole, user=user)
    user_role.is_approved = 'rejected'
    user_role.rejected_at = timezone.now()
    user_role.save()
    
    # CASCADE: If rejecting a seller, hide all their products
    if user_role.role == 'seller':
        try:
            seller_profile = SellerProfile.objects.get(user=user)
            product_count = seller_profile.products.count()
            seller_profile.hide_all_products()
            messages.error(request, f'{user.username} (Seller) has been rejected. All {product_count} products are now hidden.')
        except SellerProfile.DoesNotExist:
            messages.error(request, f'{user.username} ({user_role.role}) has been rejected')
    else:
        messages.error(request, f'{user.username} ({user_role.role}) has been rejected')
    
    return redirect('admin_dashboard')
```

### **2. Admin Approve User** (`views.py`)
```python
@login_required
def approve_user(request, user_id):
    # ... permission checks ...
    
    user = get_object_or_404(User, id=user_id)
    user_role = get_object_or_404(UserRole, user=user)
    user_role.is_approved = 'approved'
    user_role.approved_at = timezone.now()
    user_role.rejected_at = None
    user_role.save()
    
    # If approving a seller, restore their products to pending for re-review
    if user_role.role == 'seller':
        try:
            seller_profile = SellerProfile.objects.get(user=user)
            seller_profile.restore_products()
            messages.success(request, f'{user.username} (Seller) has been approved. Their products are now pending review.')
        except SellerProfile.DoesNotExist:
            messages.success(request, f'{user.username} ({user_role.role}) has been approved')
    else:
        messages.success(request, f'{user.username} ({user_role.role}) has been approved')
    
    return redirect('admin_dashboard')
```

### **3. Seller Dashboard Access Control** (`views.py`)
```python
@login_required
def seller_dashboard(request):
    try:
        role = request.user.role.role
        if role != 'seller':
            return redirect('home')
        
        # BLOCK rejected sellers from accessing dashboard
        if request.user.role.is_approved == 'rejected':
            messages.error(request, 'Your seller account has been rejected. You no longer have access to the seller dashboard.')
            return redirect('home')
        elif request.user.role.is_approved == 'pending':
            messages.warning(request, 'Your seller account is pending approval. Please wait for admin approval.')
            return redirect('home')
    except:
        return redirect('home')
    
    # ... rest of dashboard logic ...
```

### **4. Home Page - Product Filtering** (`views.py`)
```python
def home(request):
    # ... role checks ...
    
    # ONLY show products from approved sellers
    approved_products = Product.objects.filter(
        status='approved',
        seller__user__role__is_approved='approved'  # NEW FILTER
    ).order_by('-created_at')[:12]
    
    # ... rest of logic ...
```

### **5. Buyer Dashboard - Product Filtering** (`views.py`)
```python
@login_required
def buyer_dashboard(request):
    # ... role checks ...
    
    # ONLY show products from approved sellers
    approved_products = Product.objects.filter(
        status='approved',
        seller__user__role__is_approved='approved'  # NEW FILTER
    ).order_by('-created_at')
    
    # ... rest of logic ...
```

### **6. Product Detail - Access Control** (`views.py`)
```python
def product_detail(request, product_id):
    # ONLY show products from approved sellers
    product = get_object_or_404(
        Product, 
        id=product_id, 
        status='approved',
        seller__user__role__is_approved='approved'  # NEW FILTER
    )
    
    # ... rest of logic ...
```

---

## 🗄️ Database Migration

**Migration File**: `0005_userrole_rejected_at.py`

```bash
# Create migration
python manage.py makemigrations

# Output:
# Migrations for 'freshtrack_app':
#   freshtrack_project\freshtrack_app\migrations\0005_userrole_rejected_at.py
#     - Add field rejected_at to userrole

# Apply migration
python manage.py migrate

# Output:
# Running migrations:
#   Applying freshtrack_app.0005_userrole_rejected_at... OK
```

---

## 🚀 Usage Flow

### **Scenario 1: Admin Rejects Seller**
1. Admin goes to Admin Dashboard (`/admin-dashboard/`)
2. Clicks "Reject" button next to seller
3. **Automatic Actions:**
   - UserRole.is_approved → 'rejected'
   - UserRole.rejected_at → current timestamp
   - All seller's products → status='rejected'
   - Message: "John (Seller) has been rejected. All 5 products are now hidden."
4. **Result:**
   - Seller cannot access `/seller/` dashboard
   - All products invisible on home page, buyer dashboard, product detail
   - Products still exist in database but hidden

### **Scenario 2: Rejected Seller Tries to Access Dashboard**
1. Rejected seller logs in
2. Tries to visit `/seller/`
3. **System Response:**
   - Blocked at view level
   - Redirected to home page
   - Error message: "Your seller account has been rejected. You no longer have access to the seller dashboard."

### **Scenario 3: Admin Re-Approves Seller**
1. Admin clicks "Approve" for previously rejected seller
2. **Automatic Actions:**
   - UserRole.is_approved → 'approved'
   - UserRole.approved_at → current timestamp
   - UserRole.rejected_at → None
   - All rejected products → status='pending'
   - Message: "John (Seller) has been approved. Their products are now pending review."
3. **Result:**
   - Seller can access dashboard again
   - Products back to pending status
   - Admin must approve each product individually

---

## 🎨 Admin Dashboard Messages

### Rejection Messages
```python
# For sellers:
"John (Seller) has been rejected. All 5 products are now hidden."

# For other roles:
"Alice (Buyer) has been rejected"
```

### Approval Messages
```python
# For sellers:
"John (Seller) has been approved. Their products are now pending review."

# For other roles:
"Alice (Buyer) has been approved"
```

### Seller Access Blocked Messages
```python
# Rejected seller:
"Your seller account has been rejected. You no longer have access to the seller dashboard."

# Pending seller:
"Your seller account is pending approval. Please wait for admin approval."
```

---

## ✅ Testing Checklist

### Test Case 1: Reject Seller
- [ ] Admin can reject seller from admin dashboard
- [ ] All seller products automatically set to rejected status
- [ ] Success message shows product count
- [ ] Rejected seller cannot access `/seller/` dashboard
- [ ] Products not visible on home page
- [ ] Products not visible on buyer dashboard
- [ ] Product detail page returns 404 for rejected seller's products

### Test Case 2: Re-Approve Seller
- [ ] Admin can re-approve previously rejected seller
- [ ] All rejected products restored to pending status
- [ ] Seller can access dashboard again
- [ ] Products appear in seller dashboard as "Pending"
- [ ] Products still not visible to buyers until admin approves each one

### Test Case 3: Buyer View Protection
- [ ] Home page query includes approved seller filter
- [ ] Buyer dashboard query includes approved seller filter
- [ ] Product detail view includes approved seller filter
- [ ] Direct URL access to rejected seller's product shows 404

---

## 🔍 Key Implementation Points

### 1. **Cascade Pattern**
```python
# When rejecting seller
seller_profile.hide_all_products()  # Updates all products in one query
Product.objects.filter(seller=seller_profile).update(status='rejected')
```

### 2. **Query Filtering Pattern**
```python
# All buyer-facing views use this filter
Product.objects.filter(
    status='approved',
    seller__user__role__is_approved='approved'
)
```

### 3. **Access Control Pattern**
```python
# Seller dashboard checks
if request.user.role.is_approved == 'rejected':
    messages.error(request, '...')
    return redirect('home')
```

---

## 📊 Database State Examples

### Before Rejection
```
UserRole:
  user: John
  role: seller
  is_approved: 'approved'
  
SellerProfile:
  user: John
  
Products (5):
  - Product A: status='approved'
  - Product B: status='approved'
  - Product C: status='pending'
  - Product D: status='approved'
  - Product E: status='approved'
```

### After Rejection
```
UserRole:
  user: John
  role: seller
  is_approved: 'rejected'
  rejected_at: 2025-11-29 01:02:00
  
SellerProfile:
  user: John
  
Products (5):
  - Product A: status='rejected'  ← CHANGED
  - Product B: status='rejected'  ← CHANGED
  - Product C: status='rejected'  ← CHANGED
  - Product D: status='rejected'  ← CHANGED
  - Product E: status='rejected'  ← CHANGED
```

### After Re-Approval
```
UserRole:
  user: John
  role: seller
  is_approved: 'approved'
  approved_at: 2025-11-29 01:05:00
  rejected_at: None
  
SellerProfile:
  user: John
  
Products (5):
  - Product A: status='pending'  ← RESTORED
  - Product B: status='pending'  ← RESTORED
  - Product C: status='pending'  ← RESTORED
  - Product D: status='pending'  ← RESTORED
  - Product E: status='pending'  ← RESTORED
```

---

## 🎯 Summary

**What Happens When Admin Rejects a Seller:**
1. ✅ Seller's UserRole.is_approved → 'rejected'
2. ✅ All seller's products → status='rejected'
3. ✅ Seller loses dashboard access (blocked at view level)
4. ✅ Products hidden from all buyer views (home, buyer dashboard, product detail)
5. ✅ Admin sees message with product count

**What Happens When Admin Re-Approves:**
1. ✅ Seller's UserRole.is_approved → 'approved'
2. ✅ All seller's products → status='pending'
3. ✅ Seller regains dashboard access
4. ✅ Products still hidden from buyers until individually approved by admin

**Security & Quality Control:**
- Rejected sellers cannot bypass dashboard access
- Direct URL access to products checked with seller status filter
- Re-approved sellers' products require fresh admin review
- No automatic re-approval of products (maintains quality control)

---

## 🚦 Server Status

✅ **Migration Applied:** `0005_userrole_rejected_at`  
✅ **Server Running:** `http://127.0.0.1:8000/`  
✅ **Ready to Test**

---

**Implementation Complete!** 🎉
