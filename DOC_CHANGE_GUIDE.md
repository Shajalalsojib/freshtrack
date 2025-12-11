🎯 FRESHTRACK - QUICK REFERENCE & CHANGE GUIDE
═══════════════════════════════════════════════════════════════════

📋 MAIN FILES LOCATION & PURPOSE
═══════════════════════════════════════════════════════════════════

📁 PROJECT ROOT
├── manage.py                          ← Django CLI
├── requirements.txt                   ← Dependencies
├── populate_sample_data.py            ← Add test data
├── db.sqlite3                         ← Database

📁 FRESHTRACK_PROJECT (Django Project)
├── settings.py                        ← Config (DEBUG, DATABASES, INSTALLED_APPS)
├── urls.py                            ← Main router (includes freshtrack_app)
└── wsgi.py                            ← Production WSGI

📁 FRESHTRACK_APP (Main App)
├── models.py                          ← Database models (7 models)
├── views.py                           ← Business logic (40+ functions)
├── urls.py                            ← App routes (40+ paths)
├── forms.py                           ← Django forms
├── signals.py                         ← Django signals
├── admin.py                           ← Admin panel config
├── tracking_features.py               ← NEW: Tracking features
├── api_tracking.py                    ← NEW: API endpoints
├── tests.py                           ← Unit tests

📁 TEMPLATES (20 HTML files)
├── base.html                          ← Master template
├── home.html, login.html, register.html
├── buyer_dashboard.html               ← Main buyer page
├── buyer_history.html                 ← Purchase history
├── product_detail.html
├── seller_dashboard.html              ← Main seller page
├── seller_alerts.html
├── seller_analytics.html
├── admin_dashboard.html               ← Admin panel
├── add_product.html, edit_product.html
├── checkout.html, payment_*.html      ← Payment pages
└── add_review.html

═══════════════════════════════════════════════════════════════════
🔧 HOW TO MAKE CHANGES
═══════════════════════════════════════════════════════════════════

SCENARIO 1: ADD A NEW DATABASE FIELD
─────────────────────────────────────
Steps:
1. Open: freshtrack_app/models.py
2. Find the model (Product, SellerProfile, etc.)
3. Add the field with type (CharField, IntegerField, etc.)
4. Run migrations:
   → python manage.py makemigrations
   → python manage.py migrate
5. Update templates if needed to display it

Example:
def add_new_field_to_product():
    # In models.py > Product class
    new_field = models.CharField(max_length=100, blank=True)

─────────────────────────────────────

SCENARIO 2: CREATE A NEW VIEW/PAGE
─────────────────────────────────────
Steps:
1. Add function in: freshtrack_app/views.py
2. Add URL pattern in: freshtrack_app/urls.py
3. Create template in: freshtrack_app/templates/your_template.html
4. Import any needed modules at top of views.py

Structure:
def my_new_view(request):
    # Your logic here
    context = {'key': 'value'}
    return render(request, 'my_template.html', context)

Then in urls.py:
path('my-route/', views.my_new_view, name='my_route'),

─────────────────────────────────────

SCENARIO 3: MODIFY A TEMPLATE/UI
─────────────────────────────────────
Steps:
1. Open the template file
2. Find the section to change
3. Modify HTML/CSS
4. Server auto-reloads (no restart needed)
5. Refresh browser to see changes

No restart needed! Django watches for template changes.

─────────────────────────────────────

SCENARIO 4: ADD BUSINESS LOGIC
─────────────────────────────────────
Steps:
1. Add method in: freshtrack_app/tracking_features.py
   (or create new feature file)
2. Import in views.py: from .tracking_features import YourClass
3. Use in views:
   result = YourClass.your_method(params)
   context['result'] = result

─────────────────────────────────────

SCENARIO 5: ADD API ENDPOINT
─────────────────────────────────────
Steps:
1. Add function in: freshtrack_app/api_tracking.py
2. Add URL in: freshtrack_app/urls.py
   path('api/your-endpoint/', api_tracking.api_function, name='api_endpoint')
3. Return JSON:
   return JsonResponse({'key': 'value'})

─────────────────────────────────────

SCENARIO 6: CHANGE STYLING
─────────────────────────────────────
Steps:
1. Edit CSS in templates (inline <style> tags)
   OR in: freshtrack_app/static/css/style.css
2. No restart needed!
3. Refresh browser (Ctrl+F5 for hard refresh)

═══════════════════════════════════════════════════════════════════
📊 MODEL RELATIONSHIPS
═══════════════════════════════════════════════════════════════════

User (Django)
    ↓
UserRole (1:1) ← Defines if buyer/seller/admin
    ↓
SellerProfile (1:1, only if seller)
    ↓
Product (1:many)
    ├─→ Review (1:many)
    ├─→ Alert (1:many)
    └─→ Purchase (1:many)

Review ← linked to Purchase (1:1, optional)

═══════════════════════════════════════════════════════════════════
📍 IMPORTANT FUNCTIONS TO KNOW
═══════════════════════════════════════════════════════════════════

Product Methods:
├── remaining_hours() → int
├── is_visible_to_buyers() → bool
├── alert_level() → str (normal/warning/soon/urgent/last_chance/expired)
├── get_final_discount() → int (%)
├── get_discounted_price() → Decimal
├── get_savings() → Decimal
└── apply_discount(percentage) → bool

Tracking Features:
├── HourBasedTracking.get_hours_remaining(product) → float
├── SmartAlerts.check_and_create_alerts(product)
├── SaveMoney.recommend_discount_for_product(product) → int (%)
├── ReduceWaste.get_waste_prevention_stats() → dict
└── DashboardStats.get_buyer_dashboard_stats(user) → dict

═══════════════════════════════════════════════════════════════════
🔄 COMMON PATTERNS
═══════════════════════════════════════════════════════════════════

Get all products:
    products = Product.objects.all()

Get approved available products:
    products = Product.objects.approved_available()

Filter by status:
    pending = Product.objects.filter(status='pending')

Add to context in view:
    context = {
        'products': products,
        'count': products.count(),
        'stats': some_calculation()
    }

Render template:
    return render(request, 'template.html', context)

Redirect after action:
    return redirect('view_name', arg=value)

Check user role:
    if request.user.role.role == 'seller':
        # seller code

═══════════════════════════════════════════════════════════════════
⚡ QUICK COMMANDS
═══════════════════════════════════════════════════════════════════

Start server:
    python manage.py runserver

Make migrations:
    python manage.py makemigrations

Apply migrations:
    python manage.py migrate

Create superuser:
    python manage.py createsuperuser

Add sample data:
    python populate_sample_data.py

Run tests:
    python manage.py test

Django shell:
    python manage.py shell

═══════════════════════════════════════════════════════════════════
🎨 TEMPLATE STRUCTURE
═══════════════════════════════════════════════════════════════════

All templates extend base.html:
    {% extends 'base.html' %}

Add content block:
    {% block content %}
        Your HTML here
    {% endblock %}

Loop through data:
    {% for item in items %}
        {{ item.field }}
    {% endfor %}

Conditionals:
    {% if condition %}
        Show this
    {% else %}
        Show that
    {% endif %}

URL reverse:
    <a href="{% url 'view_name' arg_id %}">Link</a>

CSRF token (for forms):
    {% csrf_token %}

═══════════════════════════════════════════════════════════════════
🚀 DEPLOYMENT CHECKLIST
═══════════════════════════════════════════════════════════════════

Before going live:
☐ Set DEBUG = False in settings.py
☐ Update ALLOWED_HOSTS with domain
☐ Set SECRET_KEY to secure random string
☐ Run: python manage.py collectstatic
☐ Use PostgreSQL instead of SQLite
☐ Set up environment variables
☐ Configure CORS headers if needed
☐ Enable HTTPS
☐ Set up SSL certificate
☐ Configure static file serving (nginx/Apache)
☐ Set up database backups

═══════════════════════════════════════════════════════════════════

✨ Ready to make changes! Tell me what you want to modify.

Example requests:
- "Change buyer_dashboard to show only expiring products"
- "Add new field 'rating' to SellerProfile"
- "Create new page for seller performance metrics"
- "Modify invoice PDF format"
- "Add email notifications for alerts"
- "Change color scheme for admin panel"

═══════════════════════════════════════════════════════════════════
