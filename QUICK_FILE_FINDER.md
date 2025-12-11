# 🎯 FreshTrack - Quick File Finder

## 📁 Files Organized by First Word (Prefix)

### 🔧 SCRIPT_ Files (Utility Scripts)
```
SCRIPT_add_data.py                    → Add sample data
SCRIPT_add_fresh_products.py          → Add fresh products
SCRIPT_add_seller_products.py         → Add seller products
SCRIPT_approve_all_products.py        → Approve all products
SCRIPT_approve_products.py            → Approve pending products
SCRIPT_approve_users.py               → Approve pending users
SCRIPT_check_products.py              → Check product status
SCRIPT_cleanup_products.py            → Clean up products
SCRIPT_create_admin_role.py           → Create admin user
SCRIPT_populate_sample_data.py        → Populate sample data
SCRIPT_test_payment.py                → Test payment gateway
SCRIPT_test_visibility.py             → Test visibility rules
```

### 📚 DOC_ Files (Documentation)
```
DOC_ADMIN_DASHBOARD_REDESIGN.md       → Admin dashboard redesign
DOC_BUYER_PAGINATION_GUIDE.md         → Buyer pagination guide
DOC_CHANGE_GUIDE.md                   → Change implementation guide
DOC_CHANGE_REQUEST.md                 → Change requests
DOC_DESIGN_COMPLETE_SUMMARY.md        → Design summary
DOC_DESIGN_GUIDE.md                   → Design guidelines
DOC_DESIGN_INDEX.md                   → Design index
DOC_DESIGN_MIGRATION_GUIDE.md         → Design migration
DOC_DESIGN_QUICK_IMPLEMENTATION.md    → Quick design implementation
DOC_DESIGN_VISUAL_REFERENCE.md        → Visual design reference
DOC_DISCOUNT_FEATURE_GUIDE.md         → Discount feature guide
DOC_IMPLEMENTATION_REPORT.md          → Implementation report
DOC_INDEX.md                          → Main documentation index
DOC_LOGIN_REGISTER_GUIDE.md           → Login & registration guide
DOC_PAYMENT_FIX_SUMMARY.md            → Payment fixes
DOC_PAYMENT_QUICK_SETUP.md            → Quick payment setup
DOC_PAYMENT_SETUP.md                  → Full payment setup
DOC_PAYMENT_SYSTEM_GUIDE.md           → Payment system guide
DOC_PROJECT_RESEARCH.md               → Project research
DOC_QUICK_PAYMENT_TEST.md             → Quick payment test
DOC_QUICK_SANDBOX_TEST.md             → Sandbox testing
DOC_QUICK_SUMMARY.md                  → Quick summary
DOC_README_PAYMENT.md                 → Payment README
DOC_READY_FOR_CHANGES.md              → Ready for changes
DOC_REJECTION_QUICK_SUMMARY.md        → Rejection summary
DOC_SANDBOX_DEMO_GUIDE.md             → Sandbox demo guide
DOC_SELLER_REJECTION_GUIDE.md         → Seller rejection guide
DOC_SELLER_UPGRADE_GUIDE.md           → Seller upgrade guide
DOC_STRICT_VISIBILITY_IMPLEMENTATION.md → Visibility implementation
```

### 💾 BACKUP_ Files
```
BACKUP_views.py                       → Backup of old views
```

### 🎯 CORE Django Files (No Prefix - Most Important!)
```
manage.py                             → Django management commands
requirements.txt                      → Python dependencies
db.sqlite3                            → Database file
setup.bat / setup.sh                  → Setup scripts

freshtrack_project/
  ├── settings.py                     → Main configuration
  ├── urls.py                         → Main URL routing
  └── wsgi.py                         → Production server

freshtrack_project/freshtrack_app/
  ├── models.py                       → Database models ⭐ IMPORTANT
  ├── views.py                        → All business logic ⭐ IMPORTANT
  ├── urls.py                         → App URL routing ⭐ IMPORTANT
  ├── forms.py                        → Django forms
  ├── admin.py                        → Admin panel config
  ├── api_tracking.py                 → API tracking
  ├── tracking_features.py            → Tracking features
  └── signals.py                      → Django signals
```

---

## 📄 Template Files by Category

### 🏠 Home & Authentication
```
base.html                             → Base layout template
home.html                             → Landing page
login.html                            → Login page
register.html                         → Registration page
```

### 👨‍💼 Admin Templates
```
admin_dashboard.html                  → Main admin dashboard
admin_users.html                      → User management
admin_sellers.html                    → Seller management
admin_products.html                   → Product moderation
admin_sales_analytics.html            → Sales analytics with charts ⭐
admin_dashboard_backup.html           → Backup dashboard
```

### 🛒 Buyer Templates
```
buyer_dashboard.html                  → Buyer dashboard
buyer_dashboard_eco_example.html      → Eco design example
buyer_history.html                    → Purchase history
cart.html                             → Shopping cart
checkout.html                         → Single product checkout
checkout_cart.html                    → Cart checkout
product_detail.html                   → Product details
add_review.html                       → Add product review
```

### 🏪 Seller Templates
```
seller_dashboard.html                 → Seller dashboard
seller_analytics.html                 → Seller analytics
seller_alerts.html                    → Seller alerts
add_product.html                      → Add new product
edit_product.html                     → Edit product
```

### 💳 Payment Templates
```
payment_success.html                  → Payment successful
payment_failed.html                   → Payment failed
payment_canceled.html                 → Payment canceled
payment_ipn.html                      → Payment IPN handler
```

---

## 🎨 CSS Files
```
freshtrack-eco.css                    → Main eco-friendly theme ⭐
styles.css                            → Additional styles
```

---

## 🚀 Quick Search Guide

### Want to find...

**Scripts for adding data?**
→ Look for `SCRIPT_add_*` files

**Documentation about payment?**
→ Look for `DOC_PAYMENT_*` files

**Admin related pages?**
→ Look for `admin_*` template files

**Seller features?**
→ Look for `seller_*` template files

**Buyer features?**
→ Look for `buyer_*` template files

**Database models?**
→ `freshtrack_project/freshtrack_app/models.py`

**Business logic/functions?**
→ `freshtrack_project/freshtrack_app/views.py`

**URL routing?**
→ `freshtrack_project/freshtrack_app/urls.py`

---

## 💡 VS Code Search Tips

1. **Search by prefix**: Type `SCRIPT_` to see all scripts
2. **Search by feature**: Type `payment` to see all payment-related files
3. **Quick Open**: `Ctrl + P` then type filename
4. **Global Search**: `Ctrl + Shift + F` to search in all files
5. **Find in File**: `Ctrl + F` to search in current file

---

## ⭐ Most Frequently Used Files

### Backend (Python)
1. **models.py** - Database structure
2. **views.py** - All business logic & functions
3. **urls.py** - URL routing
4. **settings.py** - Configuration

### Frontend (Templates)
1. **base.html** - Layout
2. **home.html** - Landing page
3. **admin_dashboard.html** - Admin interface
4. **admin_sales_analytics.html** - Analytics with charts
5. **buyer_dashboard.html** - Buyer interface
6. **seller_dashboard.html** - Seller interface

### Utilities
1. **SCRIPT_create_admin_role.py** - Create admin
2. **SCRIPT_populate_sample_data.py** - Add test data
3. **FILE_STRUCTURE.md** - Full structure guide

---

**Created:** December 11, 2025  
**Last Updated:** December 11, 2025  
**Project:** FreshTrack Agricultural Product Management System
