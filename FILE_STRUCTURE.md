# 📁 FreshTrack Project - File Structure Guide
## ✨ All files renamed with clear prefixes for easy identification!

## 📋 File Naming Convention:
- **SCRIPT_** = Utility scripts (data management, testing)
- **DOC_** = Documentation files
- **BACKUP_** = Backup files
- **CONFIG_** = Configuration files
- **CORE_** = Core Django files

---

## 🎯 Main Configuration Files

### Core Settings
- **`manage.py`** - Django project runner (server start/migrate commands)
- **`freshtrack_project/settings.py`** - Main settings (database, apps, middleware)
- **`freshtrack_project/urls.py`** - Main URL routing
- **`freshtrack_project/wsgi.py`** - Production server configuration

---

## 🔧 App Files (freshtrack_project/freshtrack_app/)

### Core Backend Files
- **`models.py`** - Database models (Product, User, Purchase, Cart, etc.)
- **`views.py`** - All view functions (login, register, dashboard, payment)
- **`urls.py`** - App-specific URL patterns
- **`forms.py`** - Django forms for user input
- **`admin.py`** - Django admin panel configuration

### Special Features
- **`api_tracking.py`** - API tracking functionality
- **`tracking_features.py`** - Product tracking features
- **`signals.py`** - Django signals for automated actions

### Template Tags
- **`templatetags/product_filters.py`** - Custom template filters

---

## 📄 HTML Templates (freshtrack_project/freshtrack_app/templates/)

### 🏠 Home & Auth
- **`home.html`** - Main landing page
- **`base.html`** - Base template (navbar, footer)
- **`login.html`** - Login page
- **`register.html`** - Registration page

### 👨‍💼 Admin Dashboard
- **`admin_dashboard.html`** - Main admin dashboard
- **`admin_users.html`** - All users management
- **`admin_sellers.html`** - Seller management
- **`admin_products.html`** - Product moderation
- **`admin_sales_analytics.html`** - Sales analytics with charts ⭐

### 🛒 Buyer Pages
- **`buyer_dashboard.html`** - Buyer dashboard
- **`buyer_history.html`** - Purchase history
- **`cart.html`** - Shopping cart
- **`checkout.html`** - Single product checkout
- **`checkout_cart.html`** - Cart checkout
- **`product_detail.html`** - Product details page
- **`add_review.html`** - Add product review

### 🏪 Seller Pages
- **`seller_dashboard.html`** - Seller dashboard
- **`seller_analytics.html`** - Seller sales analytics
- **`seller_alerts.html`** - Seller alerts/notifications
- **`add_product.html`** - Add new product
- **`edit_product.html`** - Edit existing product

### 💳 Payment Pages
- **`payment_success.html`** - Payment successful page
- **`payment_failed.html`** - Payment failed page
- **`payment_canceled.html`** - Payment canceled page
- **`payment_ipn.html`** - IPN handler

---

## 🎨 CSS Files (freshtrack_project/freshtrack_app/static/css/)

- **`freshtrack-eco.css`** - Main eco-friendly theme
- **`styles.css`** - Additional styles

---

## 🔨 Utility Scripts (Root Directory)

### Data Management Scripts
- **`SCRIPT_add_data.py`** - Add sample data to database
- **`SCRIPT_add_fresh_products.py`** - Add fresh products
- **`SCRIPT_add_seller_products.py`** - Add seller products
- **`SCRIPT_populate_sample_data.py`** - Populate database with sample data

### Admin Tool Scripts
- **`SCRIPT_create_admin_role.py`** - Create admin user account
- **`SCRIPT_approve_users.py`** - Approve pending users
- **`SCRIPT_approve_products.py`** - Approve pending products
- **`SCRIPT_approve_all_products.py`** - Approve all products at once

### Testing & Cleanup Scripts
- **`SCRIPT_check_products.py`** - Check product status
- **`SCRIPT_cleanup_products.py`** - Clean up products database
- **`SCRIPT_test_payment.py`** - Test payment gateway functionality
- **`SCRIPT_test_visibility.py`** - Test product visibility rules

### Backup Files
- **`BACKUP_views.py`** - Backup of old views file

---

## 🗄️ Database
- **`db.sqlite3`** - SQLite database file

---

## 📦 Dependencies
- **`requirements.txt`** - Python package dependencies

---

## 📚 Documentation Files (Root Directory)

### Admin & Dashboard Docs
- **`DOC_ADMIN_DASHBOARD_REDESIGN.md`** - Admin dashboard redesign guide
- **`DOC_BUYER_PAGINATION_GUIDE.md`** - Buyer pagination implementation

### Design Documentation
- **`DOC_DESIGN_COMPLETE_SUMMARY.md`** - Complete design summary
- **`DOC_DESIGN_GUIDE.md`** - Design guidelines
- **`DOC_DESIGN_INDEX.md`** - Design documentation index
- **`DOC_DESIGN_MIGRATION_GUIDE.md`** - Design migration guide
- **`DOC_DESIGN_QUICK_IMPLEMENTATION.md`** - Quick design implementation
- **`DOC_DESIGN_VISUAL_REFERENCE.md`** - Visual design reference

### Feature Guides
- **`DOC_DISCOUNT_FEATURE_GUIDE.md`** - Discount feature implementation
- **`DOC_LOGIN_REGISTER_GUIDE.md`** - Login & registration guide
- **`DOC_SELLER_REJECTION_GUIDE.md`** - Seller rejection process
- **`DOC_SELLER_UPGRADE_GUIDE.md`** - Seller upgrade process
- **`DOC_STRICT_VISIBILITY_IMPLEMENTATION.md`** - Product visibility rules

### Payment Documentation
- **`DOC_PAYMENT_FIX_SUMMARY.md`** - Payment fixes summary
- **`DOC_PAYMENT_QUICK_SETUP.md`** - Quick payment setup
- **`DOC_PAYMENT_SETUP.md`** - Full payment setup guide
- **`DOC_PAYMENT_SYSTEM_GUIDE.md`** - Payment system guide
- **`DOC_README_PAYMENT.md`** - Payment README
- **`DOC_QUICK_PAYMENT_TEST.md`** - Quick payment testing
- **`DOC_QUICK_SANDBOX_TEST.md`** - Sandbox testing guide
- **`DOC_SANDBOX_DEMO_GUIDE.md`** - Sandbox demo guide

### Project Documentation
- **`DOC_CHANGE_GUIDE.md`** - Change implementation guide
- **`DOC_CHANGE_REQUEST.md`** - Change requests log
- **`DOC_IMPLEMENTATION_REPORT.md`** - Implementation report
- **`DOC_INDEX.md`** - Main documentation index
- **`DOC_PROJECT_RESEARCH.md`** - Project research notes
- **`DOC_QUICK_SUMMARY.md`** - Quick project summary
- **`DOC_READY_FOR_CHANGES.md`** - Ready for changes checklist
- **`DOC_REJECTION_QUICK_SUMMARY.md`** - Rejection feature summary
- **`FILE_STRUCTURE.md`** - This file! Complete project structure guide

---

## 🚀 Quick Access Guide

### Want to modify...

#### **Login/Register functionality?**
→ `freshtrack_project/freshtrack_app/views.py` (line 67-120)
→ `templates/login.html` & `templates/register.html`

#### **Product display on home page?**
→ `freshtrack_project/freshtrack_app/views.py` (home function)
→ `templates/home.html`

#### **Admin Dashboard?**
→ `freshtrack_project/freshtrack_app/views.py` (admin_dashboard function)
→ `templates/admin_dashboard.html`

#### **Sales Analytics with Charts?** ⭐
→ `templates/admin_sales_analytics.html` (has Chart.js)

#### **Payment Processing?**
→ `freshtrack_project/freshtrack_app/views.py` (payment functions)
→ `templates/payment_*.html`

#### **Database Models?**
→ `freshtrack_project/freshtrack_app/models.py`

#### **URL Routes?**
→ `freshtrack_project/urls.py` (main)
→ `freshtrack_project/freshtrack_app/urls.py` (app-specific)

#### **CSS Styling?**
→ `freshtrack_project/freshtrack_app/static/css/freshtrack-eco.css`

---

## 📌 Most Important Files

### Backend (Python)
1. **`models.py`** - Database structure
2. **`views.py`** - All business logic
3. **`urls.py`** - URL routing
4. **`settings.py`** - Project configuration

### Frontend (HTML)
1. **`base.html`** - Layout template
2. **`home.html`** - Landing page
3. **`admin_dashboard.html`** - Admin interface
4. **`admin_sales_analytics.html`** - Analytics dashboard ⭐

### CSS
1. **`freshtrack-eco.css`** - Main stylesheet

---

## 🔍 How to Find Specific Code

### Finding Functions in views.py
```python
# Line ranges (approximate):
- register: line 67
- login_view: line 95
- home: line 40-65
- admin_dashboard: line 600+
- payment views: line 1500+
- seller views: line 800+
- buyer views: line 400+
```

### Finding URL Patterns
```python
# freshtrack_project/freshtrack_app/urls.py
- All routes are clearly named (name='...')
- Search for: path('your-url/', ...)
```

---

## 💡 Tips

1. **VS Code Search**: Press `Ctrl + Shift + F` to search across all files
2. **Find Function**: Press `Ctrl + P` then type filename
3. **Go to Definition**: `Ctrl + Click` on function name
4. **Find in File**: `Ctrl + F`

---

**Created:** December 11, 2025  
**Project:** FreshTrack - Agricultural Product Management System
