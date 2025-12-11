FreshTrack - Smart Product Expiry Management System

Complete Website Built With:
- Frontend: HTML + CSS
- Backend: Django
- Database: SQLite (configurable to PostgreSQL)

FEATURES:

⭐ System Goal
- Products must never expire unnoticed
- Buyers see only remaining hours before expiry
- Smart alert engine notifies buyers and sellers based on expiry hours

👥 User Roles
- Buyer: Browse approved products, see hourly countdown, leave reviews
- Seller: Add products for approval, edit products, receive expiry alerts
- Admin: Approve/reject products, manage sellers, view hourly expiry insights

🟦 Seller Features
- Add new product with name, price, quantity, manufacturing date, expiry date/time
- Product starts as Pending status
- After admin approval → product becomes Approved
- Receive alerts when product is close to expiry
- Edit or update products

🟥 Admin Features
- Approve or reject products
- Manage sellers
- View best sellers
- See hourly expiry insights
- Manage rejected/pending/approved/expired product lists

🟩 Buyer Features
- View all approved products
- See hour-based expiry countdown (e.g., "48 hours left", "12 hours left")
- Receive alerts for near-expiry deals
- Choose best product using freshness, rating, price, seller quality

🔥 Smart Alert System (Hours Only)
Alert Levels:
- < 48 hours: "Early Warning"
- < 24 hours: "Expiring Soon"
- < 6 hours: "Urgent Alert"
- < 1 hour: "Last Chance"
- <= 0: Product becomes Expired

Alerts sent to:
- Sellers (their product is expiring soon)
- Buyers (hot deals & near-expiry discounts)

INSTALLATION:

1. Create Virtual Environment:
   python -m venv venv
   venv\Scripts\activate

2. Install Dependencies:
   pip install -r requirements.txt

3. Setup Database:
   cd freshtrack
   python manage.py makemigrations
   python manage.py migrate

4. Create Admin User:
   python manage.py createsuperuser

5. Run Server:
   python manage.py runserver 0.0.0.0:8000

6. Access Website:
   http://localhost:8000
   or
   http://127.0.0.1:8000
   or from network:
   http://<your-ip>:8000

PROJECT STRUCTURE:

freshtrack/
├── manage.py
├── requirements.txt
├── freshtrack_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── freshtrack_app/
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── forms.py
│       ├── models.py
│       ├── signals.py
│       ├── urls.py
│       ├── views.py
│       ├── static/
│       │   └── css/
│       │       └── style.css
│       └── templates/
│           ├── base.html
│           ├── home.html
│           ├── login.html
│           ├── register.html
│           ├── buyer_dashboard.html
│           ├── product_detail.html
│           ├── seller_dashboard.html
│           ├── add_product.html
│           ├── edit_product.html
│           ├── seller_alerts.html
│           └── admin_dashboard.html

DATABASE MODELS:

1. User (Django Built-in)
   - username, email, password

2. UserRole
   - user (OneToOne)
   - role (Buyer, Seller, Admin)

3. SellerProfile
   - user (OneToOne)
   - company_name
   - rating
   - total_sales
   - created_at

4. Product
   - seller (ForeignKey)
   - name
   - price
   - quantity
   - manufacturing_date
   - expiry_datetime
   - status (Pending, Approved, Rejected, Expired)
   - created_at, updated_at

5. Review
   - product (ForeignKey)
   - buyer (ForeignKey)
   - rating (1-5)
   - comment
   - created_at

6. Alert
   - product (ForeignKey)
   - alert_type (Seller, Buyer)
   - alert_level
   - message
   - is_read
   - created_at

KEY FUNCTIONS:

Product.remaining_hours():
- Calculates hours remaining before expiry
- Returns 0 if expired

Product.alert_level():
- Returns alert level based on remaining hours
- Values: expired, last_chance, urgent, soon, warning, normal

check_and_create_alerts(product):
- Checks product expiry status
- Creates alerts for sellers at different levels
- Prevents duplicate alerts

WORKFLOWS:

Seller Workflow:
1. Register as Seller
2. Add Product (Name, Price, Qty, Mfg Date, Expiry Date/Time)
3. Product status = Pending
4. Admin reviews and approves/rejects
5. If Approved: Product visible to buyers
6. Seller gets alerts as product approaches expiry

Admin Workflow:
1. View pending products
2. Check product details and hours remaining
3. Approve → Product becomes visible to buyers
4. Reject → Product removed from pending
5. Monitor all approved products and their expiry status
6. View best sellers and sales insights

Buyer Workflow:
1. Register as Buyer
2. Browse approved products
3. See hours remaining for each product
4. View product details and reviews
5. Leave reviews and ratings
6. See alert badges (Fresh, Early Warning, Urgent, Last Chance)

RUNNING TESTS:

To test specific features, use Django's test framework:
python manage.py test freshtrack_app

IMPROVEMENTS & OPTIMIZATION:

1. Email Notifications: Add email alerts for sellers and buyers
2. Email Integration: Configure Celery for async email sending
3. SMS Alerts: Add SMS notifications for urgent alerts
4. Dashboard Charts: Add charts for sales analytics
5. Search & Filter: Implement advanced product search
6. Real-time Alerts: Add WebSocket support for live alerts
7. Mobile App: Create mobile version
8. Payment Integration: Add Stripe/PayPal for transactions
9. Inventory Management: Add stock tracking system
10. Analytics: Add comprehensive analytics dashboard

NO ERRORS - FULLY FUNCTIONAL
