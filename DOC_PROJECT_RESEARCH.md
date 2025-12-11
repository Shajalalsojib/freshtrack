📚 FRESHTRACK PROJECT - COMPREHENSIVE RESEARCH REPORT
═══════════════════════════════════════════════════════════════════

📅 Date: December 4, 2025
🔍 Status: Complete Research & Mapping

═══════════════════════════════════════════════════════════════════
1️⃣ PROJECT OVERVIEW
═══════════════════════════════════════════════════════════════════

Name: FreshTrack - Smart Product Expiry Management System
Backend: Django 4.2+
Frontend: HTML + CSS
Database: SQLite (configurable)
Python Version: 3.13

Core Goal:
- Products must never expire unnoticed
- Buyers see remaining HOURS (not days)
- Smart alert engine notifies based on expiry time
- Prevents food waste & helps save money

═══════════════════════════════════════════════════════════════════
2️⃣ USER ROLES & FEATURES
═══════════════════════════════════════════════════════════════════

👥 BUYER
├── Browse approved products (hour-based countdown)
├── See money-saving deals
├── Track purchase history
├── Download invoices (PDF)
├── Leave/edit reviews
├── Check waste prevention stats
└── View hot deals (expiring < 6 hours)

🏪 SELLER
├── Add products (status: pending → needs admin approval)
├── Edit/update products
├── Receive smart alerts (expiry warnings)
├── View analytics (sales, revenue, trends)
├── Apply discounts (auto-recommended based on expiry)
├── Bulk operations (delete, discount)
├── Track products at waste risk
└── View performance metrics

👨‍💼 ADMIN
├── Approve/reject products
├── Manage sellers
├── Approve/reject user registrations
├── View all products with statuses
├── See pending products for review
├── View seller management dashboard
└── System-wide monitoring

═══════════════════════════════════════════════════════════════════
3️⃣ DATABASE MODELS
═══════════════════════════════════════════════════════════════════

User (Django built-in)
├── username, email, password
└── Linked to UserRole

UserRole
├── user (OneToOne)
├── role (buyer/seller/admin)
├── is_approved (pending/approved/rejected)
├── approved_at, rejected_at
└── Methods: is_seller_active()

SellerProfile
├── user (OneToOne)
├── company_name, company_info
├── rating, total_sales, total_revenue
├── is_verified, response_rate, delivery_score
├── created_at
└── Methods: is_active(), hide_all_products(), restore_products()

Product
├── seller (ForeignKey → SellerProfile)
├── name, price, quantity
├── original_price, discount_percent, discount_percentage
├── manufacturing_date, expiry_datetime
├── status (pending/approved/rejected/expired)
├── created_at, updated_at
├── Custom Manager: approved_available(), pending_products(), etc.
└── Methods: 
    ├── is_visible_to_buyers()
    ├── remaining_seconds/hours()
    ├── countdown_display(), alert_level()
    ├── recommended_discount()
    ├── has_discount(), get_final_discount()
    ├── get_discounted_price(), get_savings()
    ├── apply_discount()
    ├── get_average_rating(), get_rating_count()
    └── get_rating_stars()

Review
├── product (ForeignKey)
├── buyer (ForeignKey)
├── purchase (OneToOne, optional)
├── rating (1-5)
├── comment
└── created_at, updated_at

Alert
├── product (ForeignKey)
├── alert_type (seller/buyer)
├── alert_level, message, priority
├── is_read, action_taken
├── created_at
└── Ordering: by priority then date

Purchase
├── buyer (ForeignKey)
├── product (ForeignKey, optional)
├── product_name, seller_name
├── price, quantity, total_price
├── payment_status (initiated/pending/success/failed/canceled)
├── payment_method (card/bkash/nagad/rocket/cellfin/other)
├── transaction_id, gateway_response
├── purchased_at, payment_completed_at
└── Ordering: by purchased_at descending

═══════════════════════════════════════════════════════════════════
4️⃣ TRACKING FEATURES (NEW)
═══════════════════════════════════════════════════════════════════

📁 File: tracking_features.py

Classes:
1. HourBasedTracking
   ├── get_hours_remaining(product)
   ├── get_hours_status(product) → {status, class, label}
   └── get_all_products_with_hours()

2. SmartAlerts
   ├── create_seller_alert()
   ├── create_buyer_alert()
   ├── check_and_create_alerts()
   ├── get_seller_alerts()
   └── mark_alert_as_read()

3. SaveMoney
   ├── get_money_saving_deals()
   ├── recommend_discount_for_product()
   ├── apply_auto_discount()
   └── get_discounted_products_by_category()

4. ReduceWaste
   ├── get_products_at_waste_risk()
   ├── get_waste_prevention_stats()
   └── get_expiry_calendar()

5. DashboardStats
   ├── get_buyer_dashboard_stats()
   └── get_seller_dashboard_stats()

═══════════════════════════════════════════════════════════════════
5️⃣ API TRACKING ENDPOINTS
═══════════════════════════════════════════════════════════════════

📁 File: api_tracking.py

GET /api/product/<id>/hours/
├── Returns: hours, status, label, class
└── Auth: Required

GET /api/money-saving-deals/
├── Returns: top deals with discount info
└── Auth: Required

GET /api/waste-risk-products/
├── Returns: products at waste risk
└── Auth: Required

GET /api/waste-stats/
├── Returns: discount value, at-risk count, purchases, prevented waste
└── Auth: Required

GET /api/seller-alerts/
├── Returns: unread seller alerts
└── Auth: Required (Seller)

POST /api/alert/<id>/read/
├── Marks alert as read
└── Auth: Required (Seller)

POST /api/product/<id>/apply-discount/
├── Applies recommended discount
└── Auth: Required (Seller)

GET /api/hot-deals/
├── Returns: products expiring < 6 hours
└── Auth: Required

═══════════════════════════════════════════════════════════════════
6️⃣ VIEWS (MAIN)
═══════════════════════════════════════════════════════════════════

home()
├── Shows admin dashboard if staff/admin
└── Shows approved products for other users

register() & login_view() & logout_view()

buyer_dashboard()
├── Shows approved available products
├── Search & filtering
├── Pagination (12 per page)
├── Adds: hours_remaining, hours_status
├── Adds: money_saving_deals, waste_stats, buyer_stats
└── Returns: buyer_dashboard.html

buyer_history()
├── Shows user's purchases
├── Paginated
└── Returns: buyer_history.html

product_detail()
├── Shows single product details
├── Reviews section
└── Buy button

add_product() & edit_product() & delete_product()
├── For sellers only
├── Initializes tracking features on save
└── Updates alerts when modified

seller_dashboard()
├── Shows seller's products
├── Stats: total, approved, pending, rejected, expired
├── Expiry timeline, discount suggestions
├── Sales data (7d, 30d), daily charts
├── Adds: hours_remaining, waste_risk_products, alerts, stats
└── Returns: seller_dashboard.html

seller_alerts() & seller_analytics()

admin_dashboard()
├── Shows all products with status
├── Stats cards
├── Pending products review section (NEW)
├── Adds: hours_remaining for all products
└── Returns: admin_dashboard.html

approve_product() & reject_product()

checkout() & initiate_payment() & payment_success()
├── Payment processing with SSLCommerz
├── Creates Purchase records

download_invoice()
├── Generates PDF invoice

add_review() & delete_review()

═══════════════════════════════════════════════════════════════════
7️⃣ TEMPLATES (20 HTML FILES)
═══════════════════════════════════════════════════════════════════

Core Templates:
├── base.html (master template with navigation)
├── home.html (landing page)
├── login.html & register.html

Buyer Templates:
├── buyer_dashboard.html
│   ├── Search & filter
│   ├── Money-saving deals section
│   ├── Waste prevention stats
│   └── Product grid with hour tracking
├── buyer_history.html
│   ├── Purchase history table
│   ├── Invoice download buttons
│   └── Review buttons
└── product_detail.html
    ├── Product info
    ├── Reviews section
    └── Buy button

Seller Templates:
├── seller_dashboard.html
│   ├── Stats cards
│   ├── Smart alerts section
│   ├── Waste risk products
│   ├── Product table with filters
│   └── Charts (sales, revenue)
├── seller_alerts.html
├── seller_analytics.html
├── add_product.html
├── edit_product.html

Admin Templates:
├── admin_dashboard.html
│   ├── Stats cards
│   ├── Pending products review section (NEW)
│   └── All products table

Payment Templates:
├── checkout.html
├── payment_success.html
├── payment_failed.html
├── payment_canceled.html
└── payment_ipn.html

═══════════════════════════════════════════════════════════════════
8️⃣ URL PATTERNS (40+ ROUTES)
═══════════════════════════════════════════════════════════════════

📁 File: urls.py

Main Routes:
├── '' → home
├── 'register/' → register
├── 'login/' → login_view
├── 'logout/' → logout_view

Buyer Routes:
├── 'buyer/' → buyer_dashboard
├── 'buyer/history/' → buyer_history
├── 'product/<id>/' → product_detail
├── 'product/<id>/buy/' → buy_product

Review Routes:
├── 'review/add/<id>/' → add_review
├── 'review/delete/<id>/' → delete_review

Payment Routes:
├── 'checkout/<id>/' → checkout
├── 'payment/initiate/<id>/' → initiate_payment
├── 'payment/success/' → payment_success
├── 'payment/fail/' → payment_fail
├── 'payment/cancel/' → payment_cancel
├── 'payment/ipn/' → payment_ipn
├── 'invoice/download/<id>/' → download_invoice

Seller Routes:
├── 'seller/' → seller_dashboard
├── 'seller/add-product/' → add_product
├── 'seller/edit-product/<id>/' → edit_product
├── 'seller/quick-edit/<id>/' → quick_edit_product
├── 'seller/alerts/' → seller_alerts
├── 'seller/analytics/' → seller_analytics
├── 'seller/apply-discount/<id>/' → apply_discount
├── 'seller/bulk-delete/' → bulk_delete_products
├── 'seller/bulk-discount/' → bulk_apply_discount

Alert Routes:
├── 'alert/<id>/read/' → mark_alert_read
├── 'alert/mark-all-read/' → mark_all_alerts_read
├── 'alert/delete-product/<id>/' → delete_product_from_alert

Admin Routes:
├── 'moderation/' → admin_dashboard
├── 'moderation/approve/<id>/' → approve_product
├── 'moderation/reject/<id>/' → reject_product
├── 'moderation/approve-user/<id>/' → approve_user
├── 'moderation/reject-user/<id>/' → reject_user

API Tracking Routes:
├── 'api/product/<id>/hours/' → api_product_hours
├── 'api/money-saving-deals/' → api_money_saving_deals
├── 'api/waste-risk-products/' → api_waste_risk_products
├── 'api/waste-stats/' → api_waste_stats
├── 'api/seller-alerts/' → api_seller_alerts
├── 'api/alert/<id>/read/' → api_mark_alert_read
├── 'api/product/<id>/apply-discount/' → api_apply_recommended_discount
├── 'api/hot-deals/' → api_hot_deals

═══════════════════════════════════════════════════════════════════
9️⃣ KEY FILES & STRUCTURE
═══════════════════════════════════════════════════════════════════

Main App Files:
├── freshtrack_project/
│   ├── settings.py (Django config)
│   ├── urls.py (main router)
│   └── wsgi.py
├── manage.py (Django CLI)

App Files:
├── freshtrack_app/
│   ├── models.py (7 models)
│   ├── views.py (40+ functions)
│   ├── urls.py (40+ routes)
│   ├── forms.py
│   ├── signals.py
│   ├── admin.py
│   ├── tracking_features.py (NEW)
│   ├── api_tracking.py (NEW)
│   ├── templates/ (20 HTML files)
│   ├── static/css/ (styling)
│   └── migrations/ (database)

Support Files:
├── requirements.txt (dependencies)
├── populate_sample_data.py (test data)
├── test_payment.py
├── test_visibility.py
└── Various guides & documentation

═══════════════════════════════════════════════════════════════════
🔟 IMPLEMENTATION DETAILS
═══════════════════════════════════════════════════════════════════

Payment System:
├── Gateway: SSLCommerz (sandbox mode)
├── Methods: Card, bKash, Nagad, Rocket, CellFin
├── Status tracking: initiated → success/failed/canceled
└── IPN validation

Product Status Flow:
New Product → Pending → [Admin Approval] → Approved → Auto-Expired
                      → [Admin Rejects] → Rejected

User Approval Flow:
Registration → Pending Approval → [Admin] → Approved or Rejected

Seller Rejection:
When Seller Rejected → All their products marked as Rejected → Hidden from buyers

Hour-Based Tracking:
├── < 1 hour: LAST_CHANCE (🔴 Critical)
├── 1-6 hours: URGENT (🔴 Critical)
├── 6-24 hours: SOON (🟠 High)
├── 24-48 hours: WARNING (🟡 Medium)
└── > 48 hours: NORMAL (🟢 Low)

Discount Recommendation:
├── < 1 hour: 50% discount
├── 1-6 hours: 35% discount
├── 6-12 hours: 25% discount
├── 12-24 hours: 15% discount
├── 24-48 hours: 10% discount
└── > 48 hours: No discount

═══════════════════════════════════════════════════════════════════
1️⃣1️⃣ RECENT CHANGES (CURRENT SESSION)
═══════════════════════════════════════════════════════════════════

✅ Created tracking_features.py
   └── HourBasedTracking, SmartAlerts, SaveMoney, ReduceWaste, DashboardStats

✅ Created api_tracking.py
   └── 8 JSON API endpoints for dynamic data

✅ Updated views.py
   └── Integrated tracking features into dashboards
   └── Added hours_remaining to product objects
   └── Enhanced buyer_dashboard, seller_dashboard, admin_dashboard

✅ Updated urls.py
   └── Added API tracking routes

✅ Updated templates:
   ├── buyer_dashboard.html (added money-saving deals, waste stats)
   ├── seller_dashboard.html (added alerts, waste risk section)
   ├── admin_dashboard.html (added pending products review section)
   └── buyer_history.html (enhanced invoice download buttons)

═══════════════════════════════════════════════════════════════════
1️⃣2️⃣ READY FOR CHANGES
═══════════════════════════════════════════════════════════════════

✨ Project is fully documented and ready for modifications!

Tell me which file/section you want to change:
1. Models - Add/modify database fields
2. Views - Change business logic
3. Templates - Update UI/styling
4. Features - Add new functionality
5. API - Create new endpoints
6. Settings - Configure system behavior

Just say: "Change [section] at [location]" and provide requirements!

═══════════════════════════════════════════════════════════════════
