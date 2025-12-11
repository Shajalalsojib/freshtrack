from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Product, SellerProfile, Review, Alert, UserRole, Purchase
from .forms import ProductForm, ReviewForm, UserRegistrationForm
from .tracking_features import HourBasedTracking, SmartAlerts, SaveMoney, ReduceWaste, DashboardStats
from django.db.models import Avg, Count, Q
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import timedelta
from django.conf import settings
from django.http import HttpResponse
import requests
import json
import uuid
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO

def home(request):
    if request.user.is_authenticated:
        try:
            role = request.user.role.role
        except:
            role = 'buyer'
    else:
        role = None

    # For Admin: Show all products for moderation
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role.role == 'admin')):
        all_products = Product.objects.select_related('seller', 'seller__user').order_by('-created_at')
        pending_count = all_products.filter(status='pending').count()
        approved_count = all_products.filter(status='approved').count()
        rejected_count = all_products.filter(status='rejected').count()
        expired_count = all_products.filter(status='expired').count()
        
        context = {
            'all_products': all_products,
            'pending_count': pending_count,
            'approved_count': approved_count,
            'rejected_count': rejected_count,
            'expired_count': expired_count,
            'role': role,
            'is_admin': True,
        }
    else:
        # For Buyers/Sellers/Guests: Show ONLY approved + non-expired + from approved sellers
        # Using custom manager method for strict visibility control
        approved_products = Product.objects.approved_available().order_by('-created_at')[:12]

        context = {
            'products': approved_products,
            'role': role,
            'is_admin': False,
        }
    
    return render(request, 'home.html', context)

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        role = request.POST.get('role', 'buyer')

        if password != password_confirm:
            messages.error(request, 'Passwords do not match')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        UserRole.objects.create(user=user, role=role, is_approved='pending')

        if role == 'seller':
            SellerProfile.objects.create(user=user, company_name=username)

        messages.success(request, f'Registration successful! Please wait for admin approval to access your {role} account.')
        return redirect('login')

    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                user_role = user.role
                if user_role.is_approved == 'pending':
                    messages.error(request, 'Your account is pending admin approval. Please try again later.')
                    return redirect('login')
                elif user_role.is_approved == 'rejected':
                    messages.error(request, 'Your account has been rejected by admin.')
                    return redirect('login')
                
                login(request, user)
                return redirect('home')
            except:
                login(request, user)
                return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')

    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def buyer_dashboard(request):
    try:
        role = request.user.role.role
        if role != 'buyer':
            return redirect('home')
    except:
        return redirect('home')

    # STRICT VISIBILITY: Only show approved + non-expired products from approved sellers
    # Using custom manager method approved_available()
    approved_products = Product.objects.approved_available()
    
    # Search functionality
    search_query = request.GET.get('q', '').strip()
    if search_query:
        approved_products = approved_products.filter(
            Q(name__icontains=search_query) | 
            Q(seller__company_name__icontains=search_query)
        )

    # Alert level filtering
    alert_level = request.GET.get('alert', '')
    if alert_level:
        if alert_level == 'urgent':
            approved_products = approved_products.filter(
                expiry_datetime__lte=timezone.now() + timezone.timedelta(hours=6)
            )
        elif alert_level == 'soon':
            approved_products = approved_products.filter(
                Q(expiry_datetime__lte=timezone.now() + timezone.timedelta(hours=24)) &
                Q(expiry_datetime__gt=timezone.now() + timezone.timedelta(hours=6))
            )
    
    # Order by expiry urgency (soonest first)
    approved_products = approved_products.order_by('expiry_datetime')
    
    # Pagination (12 products per page)
    paginator = Paginator(approved_products, 12)
    page_number = request.GET.get('page', 1)
    
    try:
        products_page = paginator.page(page_number)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    
    # Add hour tracking and status to each product
    for product in products_page:
        product.hours_remaining = HourBasedTracking.get_hours_remaining(product)
        product.hours_status = HourBasedTracking.get_hours_status(product)
    
    # Get money-saving deals
    money_saving_deals = SaveMoney.get_money_saving_deals(Product.objects.approved_available())[:5]
    
    # Get waste reduction stats
    waste_stats = ReduceWaste.get_waste_prevention_stats()
    
    # Get buyer dashboard stats
    buyer_stats = DashboardStats.get_buyer_dashboard_stats(request.user)
    
    # Get cart count
    from .models import Cart
    cart_count = Cart.objects.filter(buyer=request.user).count()

    context = {
        'products': products_page,
        'role': 'buyer',
        'search_query': search_query,
        'alert_level': alert_level,
        'total_products': paginator.count,
        'money_saving_deals': money_saving_deals,
        'waste_stats': waste_stats,
        'buyer_stats': buyer_stats,
        'cart_count': cart_count,
    }
    return render(request, 'buyer_dashboard.html', context)

@login_required
def product_detail(request, product_id):
    # STRICT VISIBILITY: Only show approved + non-expired products from approved sellers
    product = get_object_or_404(
        Product.objects.approved_available(),
        id=product_id
    )
    reviews = product.reviews.all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.buyer = request.user
            review.save()
            messages.success(request, 'Review posted successfully')
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()

    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'form': form,
    }
    return render(request, 'product_detail.html', context)

@login_required
def seller_dashboard(request):
    try:
        role = request.user.role.role
        if role != 'seller':
            return redirect('home')
        
        # Block rejected sellers from accessing dashboard
        if request.user.role.is_approved == 'rejected':
            messages.error(request, 'Your seller account has been rejected. You no longer have access to the seller dashboard.')
            return redirect('home')
        elif request.user.role.is_approved == 'pending':
            messages.warning(request, 'Your seller account is pending approval. Please wait for admin approval.')
            return redirect('home')
    except:
        return redirect('home')

    seller_profile = get_object_or_404(SellerProfile, user=request.user)
    
    # Get all products
    products = seller_profile.products.all()
    
    # Auto-update expired products
    for product in products:
        if product.remaining_seconds() <= 0 and product.status != 'expired':
            product.status = 'expired'
            product.save()
    
    # Apply filters
    status_filter = request.GET.get('status', '')
    expiry_filter = request.GET.get('expiry', '')
    search_query = request.GET.get('search', '')
    
    if status_filter:
        products = products.filter(status=status_filter)
    
    if expiry_filter == '24h':
        cutoff_time = timezone.now() + timedelta(hours=24)
        products = products.filter(expiry_datetime__lte=cutoff_time, expiry_datetime__gt=timezone.now())
    elif expiry_filter == '48h':
        cutoff_time = timezone.now() + timedelta(hours=48)
        products = products.filter(expiry_datetime__lte=cutoff_time, expiry_datetime__gt=timezone.now())
    elif expiry_filter == 'low_stock':
        products = products.filter(quantity__lte=5)
    
    if search_query:
        products = products.filter(name__icontains=search_query)
    
    products = products.order_by('-created_at')
    
    # Calculate dashboard statistics
    total_products = seller_profile.products.count()
    approved_count = seller_profile.products.filter(status='approved').count()
    pending_count = seller_profile.products.filter(status='pending').count()
    rejected_count = seller_profile.products.filter(status='rejected').count()
    expired_count = seller_profile.products.filter(status='expired').count()
    
    # Expiring in 24 hours
    expiring_24h_cutoff = timezone.now() + timedelta(hours=24)
    expiring_24h = seller_profile.products.filter(
        expiry_datetime__lte=expiring_24h_cutoff,
        expiry_datetime__gt=timezone.now(),
        status='approved'
    ).count()
    
    # Get expiry timeline (next 7 days)
    expiry_timeline = []
    for day in range(7):
        day_start = timezone.now() + timedelta(days=day)
        day_end = day_start + timedelta(days=1)
        count = seller_profile.products.filter(
            expiry_datetime__gte=day_start,
            expiry_datetime__lt=day_end,
            status='approved'
        ).count()
        expiry_timeline.append({
            'day': day_start.strftime('%a %d'),
            'count': count
        })
    
    # Get products needing discount
    products_need_discount = seller_profile.products.filter(
        status='approved',
        discount_percentage=0
    ).exclude(expiry_datetime__lte=timezone.now())
    
    discount_suggestions = []
    for product in products_need_discount:
        recommended = product.recommended_discount()
        if recommended > 0:
            discount_suggestions.append({
                'product': product,
                'discount': recommended
            })
    
    # Sales data (last 7 and 30 days)
    purchases_7d = Purchase.objects.filter(
        seller_name=seller_profile.company_name,
        purchased_at__gte=timezone.now() - timedelta(days=7)
    )
    sales_7d = purchases_7d.count()
    revenue_7d = sum(p.total_price for p in purchases_7d)
    
    purchases_30d = Purchase.objects.filter(
        seller_name=seller_profile.company_name,
        purchased_at__gte=timezone.now() - timedelta(days=30)
    )
    sales_30d = purchases_30d.count()
    revenue_30d = sum(p.total_price for p in purchases_30d)
    
    # Daily sales data for chart (last 7 days)
    daily_sales_data = []
    daily_revenue_data = []
    daily_labels = []
    
    for day in range(6, -1, -1):  # 6 days ago to today
        day_start = (timezone.now() - timedelta(days=day)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        day_purchases = Purchase.objects.filter(
            seller_name=seller_profile.company_name,
            purchased_at__gte=day_start,
            purchased_at__lt=day_end
        )
        
        daily_sales = day_purchases.count()
        daily_revenue = sum(p.total_price for p in day_purchases)
        
        daily_sales_data.append(daily_sales)
        daily_revenue_data.append(float(daily_revenue))
        daily_labels.append(day_start.strftime('%b %d'))
    
    # Add hour tracking to products
    for product in products:
        product.hours_remaining = HourBasedTracking.get_hours_remaining(product)
        product.hours_status = HourBasedTracking.get_hours_status(product)
    
    # Get products at waste risk
    waste_risk_products = ReduceWaste.get_products_at_waste_risk(hours_threshold=6)
    waste_risk_products = [p for p in waste_risk_products if p['product'].seller == seller_profile][:5]
    
    # Get seller alerts
    seller_alerts = SmartAlerts.get_seller_alerts(request.user, unread_only=True)
    
    # Get seller dashboard stats
    seller_stats = DashboardStats.get_seller_dashboard_stats(request.user)

    context = {
        'seller': seller_profile,
        'products': products,
        'total_products': total_products,
        'approved_count': approved_count,
        'pending_count': pending_count,
        'rejected_count': rejected_count,
        'expired_count': expired_count,
        'expiring_24h': expiring_24h,
        'expiry_timeline': expiry_timeline,
        'discount_suggestions': discount_suggestions[:10],  # Top 10
        'sales_7d': sales_7d,
        'revenue_7d': revenue_7d,
        'sales_30d': sales_30d,
        'revenue_30d': revenue_30d,
        'daily_labels': daily_labels,
        'daily_sales_data': daily_sales_data,
        'daily_revenue_data': daily_revenue_data,
        'status_filter': status_filter,
        'expiry_filter': expiry_filter,
        'search_query': search_query,
        'role': 'seller',
        'waste_risk_products': waste_risk_products,
        'seller_alerts': seller_alerts,
        'seller_stats': seller_stats,
    }
    return render(request, 'seller_dashboard.html', context)

@login_required
def add_product(request):
    # STRICT: Only sellers can add products
    try:
        role = request.user.role.role
        if role != 'seller':
            messages.error(request, 'Only sellers can add products!')
            return redirect('home')
    except:
        messages.error(request, 'You must be a seller to add products!')
        return redirect('home')

    # Check if seller is approved
    if request.user.role.is_approved != 'approved':
        messages.error(request, 'Your seller account is not approved yet!')
        return redirect('home')

    seller_profile = get_object_or_404(SellerProfile, user=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = seller_profile
            # STRICT: New products must be pending and await admin approval
            product.status = 'pending'
            product.save()
            
            # Initialize tracking features for the new product
            SmartAlerts.check_and_create_alerts(product)
            
            messages.success(request, 'Product added successfully! Waiting for admin approval before it becomes visible to buyers.')
            return redirect('seller_dashboard')
    else:
        form = ProductForm()

    context = {
        'form': form,
        'role': 'seller',
    }
    return render(request, 'add_product.html', context)

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    try:
        role = request.user.role.role
        if role != 'seller':
            return redirect('home')
    except:
        return redirect('home')

    if product.seller.user != request.user:
        return redirect('seller_dashboard')

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            updated_product = form.save()
            
            # Update alerts when product is modified
            SmartAlerts.check_and_create_alerts(updated_product)
            
            messages.success(request, 'Product updated successfully')
            return redirect('seller_dashboard')
    else:
        form = ProductForm(instance=product)

    context = {
        'form': form,
        'product': product,
        'role': 'seller',
    }
    return render(request, 'edit_product.html', context)

@login_required
def admin_dashboard(request):
    try:
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                role = request.user.role.role
                if role != 'admin':
                    return redirect('home')
            except:
                return redirect('home')
    except:
        return redirect('home')

    # Get all seller-added products with seller information
    all_products = Product.objects.select_related('seller', 'seller__user').order_by('-created_at')
    
    # Add hour tracking to products
    for product in all_products:
        product.hours_remaining = HourBasedTracking.get_hours_remaining(product)
        product.hours_status = HourBasedTracking.get_hours_status(product)
    
    # Statistics
    pending_count = all_products.filter(status='pending').count()
    approved_count = all_products.filter(status='approved').count()
    rejected_count = all_products.filter(status='rejected').count()
    expired_count = all_products.filter(status='expired').count()
    
    # Get all users with roles
    all_users = UserRole.objects.select_related('user').order_by('-user__date_joined')
    pending_users = all_users.filter(is_approved='pending')
    approved_users = all_users.filter(is_approved='approved')
    rejected_users = all_users.filter(is_approved='rejected')
    
    # Get all sellers with their product counts and role info
    sellers = SellerProfile.objects.select_related('user').all()
    for seller in sellers:
        seller.product_count = seller.products.count()
        seller.approved_products = seller.products.filter(status='approved').count()
        seller.pending_products = seller.products.filter(status='pending').count()
        seller.rejected_products = seller.products.filter(status='rejected').count()
        # Ensure seller has a role
        try:
            seller.user_role = seller.user.role
        except:
            # Create role if it doesn't exist
            seller.user_role = UserRole.objects.create(user=seller.user, role='seller', is_approved='pending')
    
    # Get pending edit requests
    from .models import ProductEditRequest
    pending_edit_requests = ProductEditRequest.objects.filter(status='pending').select_related('product', 'seller', 'seller__user').order_by('-requested_at')
    
    # Get most selling products (by quantity sold)
    from django.db.models import Sum, Count
    most_selling_products = Purchase.objects.filter(payment_status='success').values('product_name').annotate(
        total_quantity=Sum('quantity'),
        total_sales=Count('id')
    ).order_by('-total_quantity')[:10]
    
    # Get highest revenue products
    highest_revenue_products = Purchase.objects.filter(payment_status='success').values('product_name').annotate(
        total_revenue=Sum('total_price'),
        total_sales=Count('id')
    ).order_by('-total_revenue')[:10]

    context = {
        'all_products': all_products,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'expired_count': expired_count,
        'all_users': all_users,
        'pending_users': pending_users,
        'approved_users': approved_users,
        'rejected_users': rejected_users,
        'sellers': sellers,
        'pending_edit_requests': pending_edit_requests,
        'most_selling_products': most_selling_products,
        'highest_revenue_products': highest_revenue_products,
        'role': 'admin',
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
def admin_sales_analytics(request):
    """Sales Analytics Detail Page"""
    try:
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                role = request.user.role.role
                if role != 'admin':
                    return redirect('home')
            except:
                return redirect('home')
    except:
        return redirect('home')
    
    from django.db.models import Sum, Count
    
    # Get most selling products (all results)
    most_selling_products = Purchase.objects.filter(payment_status='success').values('product_name').annotate(
        total_quantity=Sum('quantity'),
        total_sales=Count('id')
    ).order_by('-total_quantity')
    
    # Get highest revenue products (all results)
    highest_revenue_products = Purchase.objects.filter(payment_status='success').values('product_name').annotate(
        total_revenue=Sum('total_price'),
        total_sales=Count('id')
    ).order_by('-total_revenue')
    
    context = {
        'most_selling_products': most_selling_products,
        'highest_revenue_products': highest_revenue_products,
        'role': 'admin',
    }
    return render(request, 'admin_sales_analytics.html', context)

@login_required
def admin_products(request):
    """All Products Detail Page"""
    try:
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                role = request.user.role.role
                if role != 'admin':
                    return redirect('home')
            except:
                return redirect('home')
    except:
        return redirect('home')
    
    all_products = Product.objects.all().order_by('-created_at')
    pending_products = Product.objects.filter(status='pending')
    approved_products = Product.objects.filter(status='approved')
    rejected_products = Product.objects.filter(status='rejected')
    
    context = {
        'all_products': all_products,
        'pending_products': pending_products,
        'approved_products': approved_products,
        'rejected_products': rejected_products,
        'role': 'admin',
    }
    return render(request, 'admin_products.html', context)

@login_required
def admin_sellers(request):
    """Sellers Management Detail Page"""
    try:
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                role = request.user.role.role
                if role != 'admin':
                    return redirect('home')
            except:
                return redirect('home')
    except:
        return redirect('home')
    
    sellers = SellerProfile.objects.all().select_related('user').prefetch_related('products')
    
    # Ensure all sellers have UserRole and attach role data
    for seller in sellers:
        try:
            seller.role = UserRole.objects.get(user=seller.user)
        except UserRole.DoesNotExist:
            seller.role = UserRole.objects.create(
                user=seller.user,
                role='seller',
                is_approved=False
            )
    
    context = {
        'sellers': sellers,
        'role': 'admin',
    }
    return render(request, 'admin_sellers.html', context)

@login_required
def admin_users(request):
    """All Users Detail Page"""
    try:
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                role = request.user.role.role
                if role != 'admin':
                    return redirect('home')
            except:
                return redirect('home')
    except:
        return redirect('home')
    
    all_users = User.objects.all().order_by('-date_joined')
    
    # Attach role to each user
    for user in all_users:
        try:
            user.role = UserRole.objects.get(user=user)
        except UserRole.DoesNotExist:
            user.role = None
    
    context = {
        'all_users': all_users,
        'role': 'admin',
    }
    return render(request, 'admin_users.html', context)

@login_required
def approve_product(request, product_id):
    try:
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                role = request.user.role.role
                if role != 'admin':
                    return redirect('home')
            except:
                return redirect('home')
    except:
        return redirect('home')

    product = get_object_or_404(Product, id=product_id)
    product.status = 'approved'
    product.save()
    messages.success(request, f'✅ Product "{product.name}" has been approved successfully!')
    return redirect('admin_dashboard')

@login_required
def reject_product(request, product_id):
    try:
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                role = request.user.role.role
                if role != 'admin':
                    return redirect('home')
            except:
                return redirect('home')
    except:
        return redirect('home')

    product = get_object_or_404(Product, id=product_id)
    product.status = 'rejected'
    product.save()
    messages.warning(request, f'❌ Product "{product.name}" has been rejected.')
    return redirect('admin_dashboard')

@login_required
def pending_product(request, product_id):
    try:
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                role = request.user.role.role
                if role != 'admin':
                    return redirect('home')
            except:
                return redirect('home')
    except:
        return redirect('home')

    product = get_object_or_404(Product, id=product_id)
    previous_status = product.status
    product.status = 'pending'
    product.save()
    messages.info(request, f'⏳ Product "{product.name}" moved back to pending review (was: {previous_status}).')
    return redirect('admin_dashboard')

@login_required
def seller_alerts(request):
    try:
        role = request.user.role.role
        if role != 'seller':
            return redirect('home')
    except:
        return redirect('home')

    seller_profile = get_object_or_404(SellerProfile, user=request.user)
    seller_products = seller_profile.products.all()

    for product in seller_products:
        check_and_create_alerts(product)

    # Priority sorting: unread first, then by priority, then by date
    alerts = Alert.objects.filter(
        product__seller=seller_profile,
        alert_type='seller'
    ).order_by('is_read', 'priority', '-created_at')
    
    unread_count = alerts.filter(is_read=False).count()

    context = {
        'alerts': alerts,
        'unread_count': unread_count,
        'role': 'seller',
    }
    return render(request, 'seller_alerts.html', context)

@login_required
def mark_alert_read(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id)
    alert.is_read = True
    alert.save()
    return redirect('seller_alerts')

def check_and_create_alerts(product):
    if product.status == 'approved':
        seconds = product.remaining_seconds()
        
        if seconds <= 0:
            product.status = 'expired'
            product.save()
            return

        existing_alert = Alert.objects.filter(
            product=product,
            alert_type='seller',
            alert_level=product.alert_level()
        ).exists()

        if not existing_alert:
            alert_level = product.alert_level()
            
            alert_messages = {
                'expired': 'Your product has expired',
                'last_chance': f'CRITICAL: Only {seconds} seconds left!',
                'urgent': f'URGENT: Less than 6 hours left ({seconds} seconds)',
                'soon': f'Expiring soon: Less than 24 hours ({seconds} seconds)',
                'warning': f'Early warning: Less than 48 hours ({seconds} seconds)',
                'normal': 'All is normal'
            }
            
            priority_map = {
                'expired': 1,
                'last_chance': 1,
                'urgent': 2,
                'soon': 3,
                'warning': 4,
                'normal': 4
            }

            Alert.objects.create(
                product=product,
                alert_type='seller',
                alert_level=alert_level,
                message=alert_messages.get(alert_level, 'Status update'),
                priority=priority_map.get(alert_level, 4)
            )

@login_required
def approve_user(request, user_id):
    try:
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                role = request.user.role.role
                if role != 'admin':
                    return redirect('home')
            except:
                return redirect('home')
    except:
        return redirect('home')

    user_role = get_object_or_404(UserRole, id=user_id)
    user = user_role.user
    user_role.is_approved = 'approved'
    user_role.approved_at = timezone.now()
    user_role.rejected_at = None
    user_role.save()
    
    # If approving a seller, restore their products to pending for re-review
    if user_role.role == 'seller':
        try:
            seller_profile = SellerProfile.objects.get(user=user)
            seller_profile.restore_products()
            messages.success(request, f'✅ {user.username} (Seller) has been approved. Their products are now pending review.')
        except SellerProfile.DoesNotExist:
            messages.success(request, f'✅ {user.username} ({user_role.role}) has been approved')
    else:
        messages.success(request, f'✅ {user.username} ({user_role.role}) has been approved')
    
    return redirect('admin_dashboard')

@login_required
def reject_user(request, user_id):
    try:
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                role = request.user.role.role
                if role != 'admin':
                    return redirect('home')
            except:
                return redirect('home')
    except:
        return redirect('home')

    user_role = get_object_or_404(UserRole, id=user_id)
    user = user_role.user
    user_role.is_approved = 'rejected'
    user_role.rejected_at = timezone.now()
    user_role.save()
    
    # If rejecting a seller, automatically hide all their products
    if user_role.role == 'seller':
        try:
            seller_profile = SellerProfile.objects.get(user=user)
            product_count = seller_profile.products.count()
            seller_profile.hide_all_products()
            messages.error(request, f'❌ {user.username} (Seller) has been REJECTED. All {product_count} products are now hidden.')
        except SellerProfile.DoesNotExist:
            messages.error(request, f'❌ {user.username} ({user_role.role}) has been REJECTED')
    else:
        messages.error(request, f'❌ {user.username} ({user_role.role}) has been REJECTED')
    
    return redirect('admin_dashboard')

@login_required
def hold_user(request, user_id):
    try:
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                role = request.user.role.role
                if role != 'admin':
                    return redirect('home')
            except:
                return redirect('home')
    except:
        return redirect('home')

    user_role = get_object_or_404(UserRole, id=user_id)
    user = user_role.user
    previous_status = user_role.is_approved
    user_role.is_approved = 'pending'
    user_role.approved_at = None
    user_role.rejected_at = None
    user_role.save()
    
    # If holding a seller, set their products to pending
    if user_role.role == 'seller':
        try:
            seller_profile = SellerProfile.objects.get(user=user)
            products = seller_profile.products.all()
            product_count = products.count()
            for product in products:
                product.status = 'pending'
                product.save()
            messages.warning(request, f'⏸️ {user.username} (Seller) has been PUT ON HOLD. All {product_count} products moved to pending review. (Previous status: {previous_status})')
        except SellerProfile.DoesNotExist:
            messages.warning(request, f'⏸️ {user.username} ({user_role.role}) has been PUT ON HOLD (Previous status: {previous_status})')
    else:
        messages.warning(request, f'⏸️ {user.username} ({user_role.role}) has been PUT ON HOLD (Previous status: {previous_status})')
    
    return redirect('admin_dashboard')

@login_required
def approve_edit_request(request, request_id):
    """Admin approves product edit request"""
    try:
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                role = request.user.role.role
                if role != 'admin':
                    return redirect('home')
            except:
                return redirect('home')
    except:
        return redirect('home')
    
    from .models import ProductEditRequest
    edit_request = get_object_or_404(ProductEditRequest, id=request_id)
    
    # Apply the changes
    edit_request.apply_changes()
    
    # Mark as approved
    edit_request.status = 'approved'
    edit_request.reviewed_at = timezone.now()
    edit_request.reviewed_by = request.user
    edit_request.save()
    
    messages.success(request, f'✅ Edit request for "{edit_request.product.name}" approved and applied!')
    return redirect('admin_dashboard')

@login_required
def reject_edit_request(request, request_id):
    """Admin rejects product edit request"""
    try:
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                role = request.user.role.role
                if role != 'admin':
                    return redirect('home')
            except:
                return redirect('home')
    except:
        return redirect('home')
    
    from .models import ProductEditRequest
    edit_request = get_object_or_404(ProductEditRequest, id=request_id)
    
    # Mark as rejected
    edit_request.status = 'rejected'
    edit_request.reviewed_at = timezone.now()
    edit_request.reviewed_by = request.user
    edit_request.save()
    
    messages.warning(request, f'❌ Edit request for "{edit_request.product.name}" rejected!')
    return redirect('admin_dashboard')

@login_required
def buy_product(request, product_id):
    try:
        role = request.user.role.role
        if role != 'buyer':
            messages.error(request, 'Only buyers can purchase products')
            return redirect('home')
    except:
        messages.error(request, 'Please set your role as a buyer')
        return redirect('home')

    # STRICT: Only allow purchase of approved + non-expired products from approved sellers
    product = get_object_or_404(
        Product.objects.approved_available(),
        id=product_id
    )
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0 or quantity > product.quantity:
            messages.error(request, f'Invalid quantity. Available: {product.quantity}')
            return redirect('product_detail', product.id)
        
        # Create purchase record
        total_price = product.price * quantity
        Purchase.objects.create(
            buyer=request.user,
            product_name=product.name,
            seller_name=product.seller.company_name,
            price=product.price,
            quantity=quantity,
            total_price=total_price
        )
        
        # Reduce product quantity or delete if 0
        product.quantity -= quantity
        if product.quantity <= 0:
            product.delete()
            messages.success(request, f'Successfully purchased {quantity} unit(s) of {product.name}! Product removed from seller.')
        else:
            product.save()
            messages.success(request, f'Successfully purchased {quantity} unit(s) of {product.name}!')
        
        return redirect('buyer_dashboard')
    
    context = {
        'product': product,
        'role': 'buyer',
    }
    return render(request, 'product_detail.html', context)

@login_required
def buyer_history(request):
    try:
        role = request.user.role.role
        if role != 'buyer':
            return redirect('home')
    except:
        return redirect('home')
    
    purchases = Purchase.objects.filter(buyer=request.user).order_by('-purchased_at')
    
    context = {
        'purchases': purchases,
        'role': 'buyer',
    }
    return render(request, 'buyer_history.html', context)

@login_required
def apply_discount(request, product_id):
    """Apply discount to a product"""
    try:
        role = request.user.role.role
        if role != 'seller':
            return redirect('home')
    except:
        return redirect('home')
    
    product = get_object_or_404(Product, id=product_id)
    seller_profile = get_object_or_404(SellerProfile, user=request.user)
    
    if product.seller != seller_profile:
        messages.error(request, 'You can only discount your own products')
        return redirect('seller_dashboard')
    
    if request.method == 'POST':
        discount = int(request.POST.get('discount', 0))
        if discount < 0 or discount > 100:
            messages.error(request, 'Discount must be between 0 and 100')
        else:
            product.apply_discount(discount)
            messages.success(request, f'{discount}% discount applied to {product.name}')
    
    return redirect('seller_dashboard')

@login_required
def bulk_delete_products(request):
    """Bulk delete products"""
    try:
        role = request.user.role.role
        if role != 'seller':
            return redirect('home')
    except:
        return redirect('home')
    
    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids[]')
        seller_profile = get_object_or_404(SellerProfile, user=request.user)
        
        deleted_count = Product.objects.filter(
            id__in=product_ids,
            seller=seller_profile
        ).delete()[0]
        
        messages.success(request, f'{deleted_count} product(s) deleted successfully')
    
    return redirect('seller_dashboard')

@login_required
def bulk_apply_discount(request):
    """Apply discount to multiple products"""
    try:
        role = request.user.role.role
        if role != 'seller':
            return redirect('home')
    except:
        return redirect('home')
    
    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids[]')
        discount = int(request.POST.get('discount', 0))
        seller_profile = get_object_or_404(SellerProfile, user=request.user)
        
        if discount < 0 or discount > 100:
            messages.error(request, 'Discount must be between 0 and 100')
        else:
            products = Product.objects.filter(
                id__in=product_ids,
                seller=seller_profile
            )
            
            for product in products:
                product.apply_discount(discount)
            
            messages.success(request, f'{discount}% discount applied to {products.count()} product(s)')
    
    return redirect('seller_dashboard')

@login_required
def quick_edit_product(request, product_id):
    """Quick edit product - creates edit request for admin approval"""
    try:
        role = request.user.role.role
        if role != 'seller':
            return redirect('home')
    except:
        return redirect('home')
    
    product = get_object_or_404(Product, id=product_id)
    seller_profile = get_object_or_404(SellerProfile, user=request.user)
    
    if product.seller != seller_profile:
        messages.error(request, 'You can only edit your own products')
        return redirect('seller_dashboard')
    
    if request.method == 'POST':
        from .models import ProductEditRequest
        
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        discount_percent = request.POST.get('discount_percent', '0')
        
        try:
            new_price = float(price) if price else None
            new_quantity = int(quantity) if quantity else None
            new_discount = int(discount_percent) if discount_percent else None
            
            # Validate discount range
            if new_discount is not None and not (0 <= new_discount <= 90):
                messages.warning(request, 'Discount must be between 0-90%')
                return redirect('seller_dashboard')
            
            # Check if there's already a pending edit request for this product
            existing_pending = ProductEditRequest.objects.filter(
                product=product,
                status='pending'
            ).first()
            
            if existing_pending:
                # Update existing pending request
                existing_pending.new_price = new_price
                existing_pending.new_quantity = new_quantity
                existing_pending.new_discount = new_discount
                existing_pending.save()
                messages.info(request, f'⏳ Updated edit request for {product.name}. Waiting for admin approval.')
            else:
                # Create new edit request
                ProductEditRequest.objects.create(
                    product=product,
                    seller=seller_profile,
                    original_price=product.price,
                    original_discount=product.discount_percent,
                    original_quantity=product.quantity,
                    new_price=new_price,
                    new_quantity=new_quantity,
                    new_discount=new_discount,
                    status='pending'
                )
                messages.success(request, f'✅ Edit request submitted for {product.name}. Waiting for admin approval!')
        except ValueError:
            messages.error(request, 'Invalid input values')
    
    return redirect('seller_dashboard')

@login_required
def seller_analytics(request):
    """Seller analytics and insights page"""
    try:
        role = request.user.role.role
        if role != 'seller':
            return redirect('home')
    except:
        return redirect('home')
    
    seller_profile = get_object_or_404(SellerProfile, user=request.user)
    
    # Sales data
    purchases_all = Purchase.objects.filter(seller_name=seller_profile.company_name)
    total_sales = purchases_all.count()
    total_revenue = sum(p.total_price for p in purchases_all)
    
    # Last 7 days
    purchases_7d = purchases_all.filter(
        purchased_at__gte=timezone.now() - timedelta(days=7)
    )
    sales_7d = purchases_7d.count()
    revenue_7d = sum(p.total_price for p in purchases_7d)
    
    # Last 30 days
    purchases_30d = purchases_all.filter(
        purchased_at__gte=timezone.now() - timedelta(days=30)
    )
    sales_30d = purchases_30d.count()
    revenue_30d = sum(p.total_price for p in purchases_30d)
    
    # Most sold products
    from collections import Counter
    product_sales = Counter(p.product_name for p in purchases_all)
    most_sold = [{'name': name, 'count': count} for name, count in product_sales.most_common(10)]
    
    # Reviews analysis
    reviews = Review.objects.filter(product__seller=seller_profile)
    total_reviews = reviews.count()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    rating_breakdown = seller_profile.get_rating_breakdown()
    
    # Top reviews
    top_reviews = reviews.order_by('-rating', '-created_at')[:5]
    
    context = {
        'seller': seller_profile,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'sales_7d': sales_7d,
        'revenue_7d': revenue_7d,
        'sales_30d': sales_30d,
        'revenue_30d': revenue_30d,
        'most_sold': most_sold,
        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 1),
        'rating_breakdown': rating_breakdown,
        'top_reviews': top_reviews,
        'role': 'seller',
    }
    return render(request, 'seller_analytics.html', context)

@login_required
def mark_all_alerts_read(request):
    """Mark all seller alerts as read"""
    try:
        role = request.user.role.role
        if role != 'seller':
            return redirect('home')
    except:
        return redirect('home')
    
    seller_profile = get_object_or_404(SellerProfile, user=request.user)
    Alert.objects.filter(
        product__seller=seller_profile,
        alert_type='seller',
        is_read=False
    ).update(is_read=True)
    
    messages.success(request, 'All alerts marked as read')
    return redirect('seller_alerts')

@login_required
def delete_product_from_alert(request, product_id):
    """Delete product directly from alert page"""
    try:
        role = request.user.role.role
        if role != 'seller':
            return redirect('home')
    except:
        return redirect('home')
    
    product = get_object_or_404(Product, id=product_id)
    seller_profile = get_object_or_404(SellerProfile, user=request.user)
    
    if product.seller != seller_profile:
        messages.error(request, 'You can only delete your own products')
        return redirect('seller_alerts')
    
    product_name = product.name
    product.delete()
    messages.success(request, f'{product_name} has been removed')
    
    return redirect('seller_alerts')


# ============== PAYMENT SYSTEM ==============

@login_required
def checkout(request, product_id):
    """Display checkout page with payment method selection"""
    try:
        role = request.user.role.role
        if role != 'buyer':
            messages.error(request, 'Only buyers can purchase products')
            return redirect('home')
    except:
        messages.error(request, 'Please set your role as a buyer')
        return redirect('home')

    # STRICT: Only allow checkout for approved + non-expired products from approved sellers
    product = get_object_or_404(
        Product.objects.approved_available(),
        id=product_id
    )
    
    # Get quantity from query params or default to 1
    quantity = int(request.GET.get('quantity', 1))
    
    if quantity <= 0 or quantity > product.quantity:
        messages.error(request, f'Invalid quantity. Available: {product.quantity}')
        return redirect('product_detail', product.id)
    
    # Use discounted price if available
    unit_price = product.get_discounted_price()
    total_price = unit_price * quantity
    
    context = {
        'product': product,
        'quantity': quantity,
        'total_price': total_price,
    }
    return render(request, 'checkout.html', context)


@login_required
def initiate_payment(request, product_id):
    """Initiate SSLCommerz payment"""
    if request.method != 'POST':
        messages.warning(request, 'Invalid request method')
        return redirect('checkout', product_id)
    
    try:
        role = request.user.role.role
        if role != 'buyer':
            messages.error(request, 'Only buyers can purchase products')
            return redirect('home')
    except:
        messages.error(request, 'Please set your role as a buyer')
        return redirect('home')
    
    # STRICT: Only allow payment for approved + non-expired products from approved sellers
    product = get_object_or_404(
        Product.objects.approved_available(),
        id=product_id
    )
    
    # Validate quantity
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        messages.error(request, 'Invalid quantity provided')
        return redirect('checkout', product_id)
    
    if quantity <= 0:
        messages.error(request, 'Quantity must be greater than 0')
        return redirect('checkout', product_id)
    
    if quantity > product.quantity:
        messages.error(request, f'Not enough stock available. Only {product.quantity} units in stock.')
        return redirect('checkout', product_id)
    
    # Validate payment method
    payment_method = request.POST.get('payment_method', '').strip()
    valid_methods = ['card', 'bkash', 'nagad', 'rocket', 'cellfin']
    
    if not payment_method or payment_method not in valid_methods:
        messages.error(request, 'Please select a valid payment method.')
        return redirect('checkout', product_id)
    
    # Use discounted price if available
    unit_price = product.get_discounted_price()
    total_price = unit_price * quantity
    
    # Create Purchase record with initiated status
    transaction_id = f"FT{uuid.uuid4().hex[:12].upper()}"
    purchase = Purchase.objects.create(
        buyer=request.user,
        product=product,
        product_name=product.name,
        seller_name=product.seller.company_name,
        price=unit_price,  # Store discounted price
        quantity=quantity,
        total_price=total_price,
        payment_status='initiated',
        payment_method=payment_method,
        transaction_id=transaction_id
    )
    
    # Build absolute URLs for callbacks
    base_url = request.build_absolute_uri('/')[:-1]
    
    # Prepare SSLCommerz payment data
    payment_data = {
        'store_id': settings.SSLCOMMERZ_STORE_ID,
        'store_passwd': settings.SSLCOMMERZ_STORE_PASSWORD,
        'total_amount': str(total_price),
        'currency': 'BDT',
        'tran_id': transaction_id,
        'success_url': f"{base_url}/payment/success/",
        'fail_url': f"{base_url}/payment/fail/",
        'cancel_url': f"{base_url}/payment/cancel/",
        'ipn_url': f"{base_url}/payment/ipn/",
        
        # Customer info
        'cus_name': request.user.username,
        'cus_email': request.user.email or f"{request.user.username}@freshtrack.com",
        'cus_phone': '01700000000',  # You can add phone field to user profile
        'cus_add1': 'Dhaka, Bangladesh',
        'cus_city': 'Dhaka',
        'cus_country': 'Bangladesh',
        
        # Product info
        'product_name': product.name,
        'product_category': 'Fresh Products',
        'product_profile': 'general',
        
        # Shipping info (optional)
        'shipping_method': 'NO',
        'num_of_item': quantity,
        
        # Additional parameters
        'emi_option': '0',
    }
    
    try:
        # Log payment initiation
        print(f"\n{'='*60}")
        print(f"Initiating payment for transaction: {transaction_id}")
        print(f"Amount: ৳{total_price} | Method: {payment_method}")
        print(f"SSLCommerz Store ID: {settings.SSLCOMMERZ_STORE_ID}")
        print(f"API URL: {settings.SSLCOMMERZ_API_URL}")
        print(f"Sandbox Mode: {settings.SSLCOMMERZ_IS_SANDBOX}")
        print(f"{'='*60}\n")
        
        # Call SSLCommerz API
        response = requests.post(
            settings.SSLCOMMERZ_API_URL, 
            data=payment_data,
            timeout=30
        )
        
        # Log raw response
        print(f"SSLCommerz Response Status Code: {response.status_code}")
        print(f"SSLCommerz Response Text: {response.text[:500]}")
        
        response_data = response.json()
        
        # Save gateway response
        purchase.gateway_response = json.dumps(response_data)
        purchase.save()
        
        # Log parsed response
        print(f"Parsed Response Status: {response_data.get('status')}")
        print(f"Gateway URL: {response_data.get('GatewayPageURL', 'N/A')}")
        
        if response_data.get('status') == 'SUCCESS':
            gateway_url = response_data.get('GatewayPageURL')
            if gateway_url:
                print(f"✓ Payment initiation successful! Redirecting to: {gateway_url}")
                # Redirect to SSLCommerz payment page
                return redirect(gateway_url)
            else:
                print("✗ Gateway URL not found in response")
        else:
            print(f"✗ Payment initiation failed. Status: {response_data.get('status')}")
            print(f"Failed Reason: {response_data.get('failedreason', 'Unknown')}")
        
        # If failed to get gateway URL
        purchase.payment_status = 'failed'
        purchase.save()
        
        error_msg = response_data.get('failedreason', 'Failed to initiate payment. Please try again.')
        messages.error(request, error_msg)
        return redirect('checkout', product_id)
        
    except requests.exceptions.Timeout:
        purchase.payment_status = 'failed'
        purchase.gateway_response = 'Request timeout'
        purchase.save()
        print("✗ SSLCommerz API request timeout")
        messages.error(request, 'Payment gateway timeout. Please try again.')
        return redirect('checkout', product_id)
    except requests.exceptions.RequestException as e:
        purchase.payment_status = 'failed'
        purchase.gateway_response = f'Request error: {str(e)}'
        purchase.save()
        print(f"✗ SSLCommerz API request error: {str(e)}")
        messages.error(request, 'Unable to connect to payment gateway. Please try again.')
        return redirect('checkout', product_id)
    except json.JSONDecodeError as e:
        purchase.payment_status = 'failed'
        purchase.gateway_response = f'JSON decode error: {str(e)}'
        purchase.save()
        print(f"✗ Failed to parse SSLCommerz response: {str(e)}")
        messages.error(request, 'Invalid response from payment gateway. Please try again.')
        return redirect('checkout', product_id)
    except Exception as e:
        purchase.payment_status = 'failed'
        purchase.gateway_response = f'Unexpected error: {str(e)}'
        purchase.save()
        print(f"✗ Unexpected error during payment initiation: {str(e)}")
        messages.error(request, f'Payment initialization error. Please contact support.')
        return redirect('checkout', product_id)


@csrf_exempt
def payment_success(request):
    """Handle successful payment callback"""
    if request.method in ['POST', 'GET']:
        # Get transaction ID from callback
        tran_id = request.POST.get('tran_id') or request.GET.get('tran_id')
        val_id = request.POST.get('val_id') or request.GET.get('val_id')
        amount = request.POST.get('amount') or request.GET.get('amount')
        card_type = request.POST.get('card_type') or request.GET.get('card_type')
        
        # Log callback data
        print(f"\n{'='*60}")
        print(f"Payment Success Callback Received")
        print(f"Transaction ID: {tran_id}")
        print(f"Validation ID: {val_id}")
        print(f"Amount: {amount}")
        print(f"Card Type: {card_type}")
        print(f"Method: {request.method}")
        print(f"{'='*60}\n")
        
        if not tran_id:
            print("✗ Transaction ID missing from callback")
            messages.error(request, 'Invalid payment response - missing transaction ID')
            return redirect('buyer_dashboard')
        
        if not val_id:
            print("✗ Validation ID missing from callback")
            messages.error(request, 'Invalid payment response - missing validation ID')
            return redirect('buyer_dashboard')
        
        try:
            purchase = Purchase.objects.get(transaction_id=tran_id)
            print(f"✓ Purchase found: {purchase.id} | Buyer: {purchase.buyer.username}")
            
            # CRITICAL: Always verify payment with SSLCommerz - never trust redirect alone
            validation_data = {
                'val_id': val_id,
                'store_id': settings.SSLCOMMERZ_STORE_ID,
                'store_passwd': settings.SSLCOMMERZ_STORE_PASSWORD,
            }
            
            print(f"Verifying payment with SSLCommerz...")
            print(f"Validation URL: {settings.SSLCOMMERZ_VALIDATION_URL}")
            
            validation_response = requests.get(
                settings.SSLCOMMERZ_VALIDATION_URL,
                params=validation_data,
                timeout=30
            )
            
            print(f"Validation Response Status: {validation_response.status_code}")
            validation_result = validation_response.json()
            print(f"Validation Result: {json.dumps(validation_result, indent=2)}")
            
            # Check if payment is valid
            validation_status = validation_result.get('status', '').upper()
            
            if validation_status in ['VALID', 'VALIDATED']:
                # Payment verified successfully
                print(f"✓ Payment verified successfully!")
                
                # Double-check if already processed to avoid duplicate processing
                if purchase.payment_status == 'success':
                    print(f"⚠ Payment already processed for transaction {tran_id}")
                    return render(request, 'payment_success.html', {'purchase': purchase})
                
                purchase.payment_status = 'success'
                purchase.payment_completed_at = timezone.now()
                purchase.gateway_response = json.dumps(validation_result)
                purchase.save()
                
                print(f"Updated purchase status to: success")
                
                # Reduce product quantity
                if purchase.product:
                    product = purchase.product
                    print(f"Reducing stock: {product.name} | Current: {product.quantity} | Ordered: {purchase.quantity}")
                    
                    product.quantity -= purchase.quantity
                    
                    if product.quantity <= 0:
                        print(f"Product out of stock - deleting product {product.id}")
                        product.delete()
                    else:
                        product.save()
                        print(f"New stock level: {product.quantity}")
                    
                    # Update seller stats
                    try:
                        seller = product.seller
                        seller.total_sales += purchase.quantity
                        seller.total_revenue += purchase.total_price
                        seller.save()
                        print(f"✓ Updated seller stats: {seller.company_name}")
                    except Exception as e:
                        print(f"⚠ Failed to update seller stats: {str(e)}")
                else:
                    print(f"⚠ Product not found for purchase {purchase.id}")
                
                messages.success(request, '✓ Payment successful! Your order has been confirmed.')
                return render(request, 'payment_success.html', {'purchase': purchase})
            else:
                # Validation failed
                print(f"✗ Payment verification failed. Status: {validation_status}")
                print(f"Validation result: {validation_result}")
                
                purchase.payment_status = 'failed'
                purchase.gateway_response = json.dumps(validation_result)
                purchase.save()
                
                messages.error(request, 'Payment verification failed. Your payment was not processed.')
                return redirect('payment_fail')
                
        except Purchase.DoesNotExist:
            print(f"✗ Purchase not found for transaction ID: {tran_id}")
            messages.error(request, 'Order not found in our system')
            return redirect('buyer_dashboard')
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to verify payment with SSLCommerz: {str(e)}")
            messages.error(request, 'Unable to verify payment. Please contact support with your transaction ID.')
            return redirect('buyer_dashboard')
        except Exception as e:
            print(f"✗ Unexpected error during payment verification: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Payment verification error. Please contact support.')
            return redirect('payment_fail')
    
    print("✗ Invalid request method or missing data")
    return redirect('buyer_dashboard')


@login_required
def download_invoice(request, purchase_id):
    """Generate and download premium payment invoice/receipt as PDF"""
    purchase = get_object_or_404(Purchase, id=purchase_id, buyer=request.user)
    
    if purchase.payment_status != 'success':
        messages.error(request, 'Invoice only available for successful payments')
        return redirect('buyer_history')
    
    # Create PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#10b981'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#6b7280'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1f2937'),
        spaceBefore=15,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    # Header
    story.append(Paragraph("🍃 FreshTrack", title_style))
    story.append(Paragraph("Fresh Products Marketplace", subtitle_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Invoice title
    invoice_title = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#3b82f6'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    story.append(Paragraph("PAYMENT RECEIPT", invoice_title))
    story.append(Spacer(1, 0.1*inch))
    
    # Transaction details box
    transaction_data = [
        ['Transaction ID:', str(purchase.transaction_id)],
        ['Invoice Date:', purchase.payment_completed_at.strftime('%B %d, %Y at %I:%M %p') if purchase.payment_completed_at else 'N/A'],
        ['Payment Status:', '✅ SUCCESSFUL'],
    ]
    
    transaction_table = Table(transaction_data, colWidths=[2*inch, 4*inch])
    transaction_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
    ]))
    story.append(transaction_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Customer & Seller Info
    story.append(Paragraph("Customer & Seller Information", heading_style))
    
    info_data = [
        ['Customer Name:', purchase.buyer.username, 'Seller:', purchase.seller_name],
        ['Email:', purchase.buyer.email, 'Product:', purchase.product_name],
    ]
    
    info_table = Table(info_data, colWidths=[1.5*inch, 2*inch, 1.2*inch, 2*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#374151')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Order Details
    story.append(Paragraph("Order Details", heading_style))
    
    order_data = [
        ['Description', 'Unit Price', 'Quantity', 'Total'],
        [purchase.product_name, f'৳{purchase.price:.2f}', str(purchase.quantity), f'৳{purchase.total_price:.2f}'],
    ]
    
    order_table = Table(order_data, colWidths=[3*inch, 1.5*inch, 1.2*inch, 1.5*inch])
    order_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
    ]))
    story.append(order_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Total Amount Box
    total_data = [
        ['TOTAL AMOUNT PAID:', f'৳{purchase.total_price:.2f}'],
    ]
    
    total_table = Table(total_data, colWidths=[5*inch, 2*inch])
    total_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 16),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 15),
        ('TOPPADDING', (0, 0), (-1, 0), 15),
    ]))
    story.append(total_table)
    story.append(Spacer(1, 0.4*inch))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#9ca3af'),
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("━" * 80, footer_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("Thank you for shopping with FreshTrack! 🍃", footer_style))
    story.append(Paragraph("Fresh Products, Fresh Experience", footer_style))
    story.append(Spacer(1, 0.05*inch))
    story.append(Paragraph(f"This is a computer-generated receipt. Invoice ID: {purchase.id}", footer_style))
    
    # Build PDF
    doc.build(story)
    
    # Return PDF response
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="FreshTrack_Invoice_{purchase.transaction_id}.pdf"'
    
    return response


@csrf_exempt
def payment_fail(request):
    """Handle failed payment callback"""
    tran_id = request.POST.get('tran_id') or request.GET.get('tran_id')
    error_message = request.POST.get('error') or request.GET.get('error', 'Payment failed')
    
    product_id = None
    if tran_id:
        try:
            purchase = Purchase.objects.get(transaction_id=tran_id)
            purchase.payment_status = 'failed'
            purchase.gateway_response = json.dumps(dict(request.POST) if request.POST else dict(request.GET))
            purchase.save()
            product_id = purchase.product.id if purchase.product else None
        except Purchase.DoesNotExist:
            pass
    
    context = {
        'error_message': error_message,
        'product_id': product_id,
    }
    return render(request, 'payment_failed.html', context)


@csrf_exempt
def payment_cancel(request):
    """Handle canceled payment callback"""
    tran_id = request.POST.get('tran_id') or request.GET.get('tran_id')
    
    product_id = None
    if tran_id:
        try:
            purchase = Purchase.objects.get(transaction_id=tran_id)
            purchase.payment_status = 'canceled'
            purchase.gateway_response = json.dumps(dict(request.POST) if request.POST else dict(request.GET))
            purchase.save()
            product_id = purchase.product.id if purchase.product else None
        except Purchase.DoesNotExist:
            pass
    
    context = {
        'product_id': product_id,
    }
    return render(request, 'payment_canceled.html', context)


@csrf_exempt
def payment_ipn(request):
    """Handle IPN (Instant Payment Notification) from SSLCommerz"""
    if request.method == 'POST':
        tran_id = request.POST.get('tran_id')
        val_id = request.POST.get('val_id')
        status = request.POST.get('status')
        
        if tran_id:
            try:
                purchase = Purchase.objects.get(transaction_id=tran_id)
                
                # Update payment status based on IPN
                if status == 'VALID' or status == 'VALIDATED':
                    if purchase.payment_status != 'success':
                        purchase.payment_status = 'success'
                        purchase.payment_completed_at = timezone.now()
                        purchase.gateway_response = json.dumps(dict(request.POST))
                        purchase.save()
                        
                        # Reduce product quantity if not already done
                        if purchase.product and purchase.product.quantity >= purchase.quantity:
                            product = purchase.product
                            product.quantity -= purchase.quantity
                            if product.quantity <= 0:
                                product.delete()
                            else:
                                product.save()
                elif status in ['FAILED', 'CANCELLED']:
                    purchase.payment_status = 'failed' if status == 'FAILED' else 'canceled'
                    purchase.gateway_response = json.dumps(dict(request.POST))
                    purchase.save()
                
            except Purchase.DoesNotExist:
                pass
    
    return render(request, 'payment_ipn.html')

@login_required
def add_review(request, purchase_id):
    """Add or edit review for a purchased product"""
    purchase = get_object_or_404(Purchase, id=purchase_id, buyer=request.user, payment_status='success')
    
    # Check if product still exists
    if not purchase.product:
        messages.error(request, "This product is no longer available for review.")
        return redirect('buyer_history')
    
    # Check if review already exists
    existing_review = Review.objects.filter(product=purchase.product, buyer=request.user).first()
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()
        
        if not rating:
            messages.error(request, "Please select a rating.")
            return redirect('buyer_history')
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                messages.error(request, "Rating must be between 1 and 5 stars.")
                return redirect('buyer_history')
        except ValueError:
            messages.error(request, "Invalid rating value.")
            return redirect('buyer_history')
        
        if existing_review:
            # Update existing review
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.save()
            messages.success(request, "Your review has been updated successfully!")
        else:
            # Create new review
            Review.objects.create(
                product=purchase.product,
                buyer=request.user,
                purchase=purchase,
                rating=rating,
                comment=comment
            )
            messages.success(request, "Thank you for your review!")
        
        return redirect('buyer_history')
    
    context = {
        'purchase': purchase,
        'existing_review': existing_review,
        'role': 'buyer',
    }
    return render(request, 'add_review.html', context)

@login_required
def delete_review(request, review_id):
    """Delete a review"""
    review = get_object_or_404(Review, id=review_id, buyer=request.user)
    review.delete()
    messages.success(request, "Your review has been deleted.")
    return redirect('buyer_history')

# ============== SHOPPING CART SYSTEM ==============

@login_required
def add_to_cart(request, product_id):
    """Add product to shopping cart"""
    try:
        role = request.user.role.role
        if role != 'buyer':
            messages.error(request, 'Only buyers can add products to cart')
            return redirect('home')
    except:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    product = get_object_or_404(Product, id=product_id)
    
    # Check if product is visible to buyers
    if not product.is_visible_to_buyers():
        messages.error(request, 'This product is not available')
        return redirect('buyer_dashboard')
    
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        messages.error(request, 'Quantity must be at least 1')
        return redirect('buyer_dashboard')
    
    if quantity > product.quantity:
        messages.error(request, f'Only {product.quantity} units available')
        return redirect('buyer_dashboard')
    
    # Add to cart or update quantity
    from .models import Cart
    cart_item, created = Cart.objects.get_or_create(
        buyer=request.user,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        # Update quantity if item already in cart
        cart_item.quantity += quantity
        if cart_item.quantity > product.quantity:
            cart_item.quantity = product.quantity
        cart_item.save()
        messages.success(request, f'Updated {product.name} quantity in cart')
    else:
        messages.success(request, f'Added {product.name} to cart')
    
    return redirect('view_cart')

@login_required
def view_cart(request):
    """Display shopping cart"""
    try:
        role = request.user.role.role
        if role != 'buyer':
            return redirect('home')
    except:
        return redirect('home')
    
    from .models import Cart
    cart_items = Cart.objects.filter(buyer=request.user).select_related('product', 'product__seller')
    
    # Calculate totals
    subtotal = sum(item.get_total_price() for item in cart_items)
    total_items = sum(item.quantity for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total_items': total_items,
        'role': 'buyer',
    }
    return render(request, 'cart.html', context)

@login_required
def update_cart_quantity(request, cart_item_id):
    """Update cart item quantity"""
    try:
        role = request.user.role.role
        if role != 'buyer':
            return redirect('home')
    except:
        return redirect('home')
    
    from .models import Cart
    cart_item = get_object_or_404(Cart, id=cart_item_id, buyer=request.user)
    
    action = request.POST.get('action')
    
    if action == 'increase':
        if cart_item.quantity < cart_item.product.quantity:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, 'Quantity updated')
        else:
            messages.error(request, 'Maximum quantity reached')
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            messages.success(request, 'Quantity updated')
        else:
            messages.error(request, 'Minimum quantity is 1')
    
    return redirect('view_cart')

@login_required
def remove_from_cart(request, cart_item_id):
    """Remove item from cart"""
    try:
        role = request.user.role.role
        if role != 'buyer':
            return redirect('home')
    except:
        return redirect('home')
    
    from .models import Cart
    cart_item = get_object_or_404(Cart, id=cart_item_id, buyer=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'Removed {product_name} from cart')
    return redirect('view_cart')

@login_required
def checkout_cart(request):
    """Checkout all items in cart"""
    try:
        role = request.user.role.role
        if role != 'buyer':
            return redirect('home')
    except:
        return redirect('home')
    
    from .models import Cart
    cart_items = Cart.objects.filter(buyer=request.user).select_related('product')
    
    if not cart_items.exists():
        messages.error(request, 'Your cart is empty')
        return redirect('view_cart')
    
    # Calculate totals
    subtotal = sum(item.get_total_price() for item in cart_items)
    total_items = sum(item.quantity for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total_items': total_items,
        'role': 'buyer',
    }
    return render(request, 'checkout_cart.html', context)

@login_required
def process_cart_payment(request):
    """Process payment for all cart items"""
    if request.method != 'POST':
        return redirect('view_cart')
    
    try:
        role = request.user.role.role
        if role != 'buyer':
            return redirect('home')
    except:
        return redirect('home')
    
    from .models import Cart
    cart_items = Cart.objects.filter(buyer=request.user).select_related('product', 'product__seller')
    
    if not cart_items.exists():
        messages.error(request, 'Your cart is empty')
        return redirect('view_cart')
    
    # Validate payment method
    payment_method = request.POST.get('payment_method', '').strip()
    valid_methods = ['card', 'bkash', 'nagad', 'rocket', 'cellfin']
    
    if not payment_method or payment_method not in valid_methods:
        messages.error(request, 'Please select a valid payment method.')
        return redirect('checkout_cart')
    
    # Calculate total
    total_amount = sum(item.get_total_price() for item in cart_items)
    
    # Generate unique transaction ID
    transaction_id = f"FT{uuid.uuid4().hex[:12].upper()}"
    
    # Create purchase records for each item
    purchases = []
    for item in cart_items:
        purchase = Purchase.objects.create(
            buyer=request.user,
            product=item.product,
            product_name=item.product.name,
            seller_name=item.product.seller.company_name,
            price=item.product.get_discounted_price(),
            quantity=item.quantity,
            total_price=item.get_total_price(),
            payment_status='initiated',
            payment_method=payment_method,
            transaction_id=f"{transaction_id}-{item.id}"
        )
        purchases.append(purchase)
    
    # Prepare SSLCommerz payment
    payment_data = {
        'store_id': settings.SSLCOMMERZ_STORE_ID,
        'store_passwd': settings.SSLCOMMERZ_STORE_PASSWORD,
        'total_amount': str(total_amount),
        'currency': 'BDT',
        'tran_id': transaction_id,
        'success_url': request.build_absolute_uri('/payment/cart-success/'),
        'fail_url': request.build_absolute_uri('/payment/cart-fail/'),
        'cancel_url': request.build_absolute_uri('/payment/cart-cancel/'),
        'ipn_url': request.build_absolute_uri('/payment/ipn/'),
        'cus_name': request.user.username,
        'cus_email': request.user.email or 'buyer@freshtrack.com',
        'cus_phone': '01700000000',
        'cus_add1': 'Dhaka',
        'cus_city': 'Dhaka',
        'cus_country': 'Bangladesh',
        'shipping_method': 'NO',
        'product_name': f'Cart Items ({len(cart_items)} products)',
        'product_category': 'Fresh Products',
        'product_profile': 'general',
    }
    
    try:
        response = requests.post(settings.SSLCOMMERZ_API_URL, data=payment_data)
        response_data = response.json()
        
        if response_data.get('status') == 'SUCCESS':
            # Clear cart after successful initiation
            cart_items.delete()
            return redirect(response_data['GatewayPageURL'])
        else:
            # Delete purchases if payment initiation failed
            for purchase in purchases:
                purchase.delete()
            messages.error(request, 'Payment initiation failed. Please try again.')
            return redirect('checkout_cart')
    except Exception as e:
        # Delete purchases on error
        for purchase in purchases:
            purchase.delete()
        messages.error(request, f'Payment error: {str(e)}')
        return redirect('checkout_cart')

@csrf_exempt
def payment_cart_success(request):
    """Handle successful cart payment"""
    tran_id = request.POST.get('tran_id') or request.GET.get('tran_id')
    
    purchases_list = []
    if tran_id:
        # Update all purchases with this transaction base ID
        purchases = Purchase.objects.filter(transaction_id__startswith=tran_id)
        
        for purchase in purchases:
            if purchase.payment_status != 'success':
                purchase.payment_status = 'success'
                purchase.payment_completed_at = timezone.now()
                purchase.save()
                
                # Reduce product quantity
                if purchase.product and purchase.product.quantity >= purchase.quantity:
                    product = purchase.product
                    product.quantity -= purchase.quantity
                    if product.quantity <= 0:
                        product.delete()
                    else:
                        product.save()
            
            purchases_list.append(purchase)
        
        messages.success(request, 'Payment successful! Thank you for your purchase.')
    
    return render(request, 'payment_success.html', {
        'role': 'buyer',
        'purchases': purchases_list,
        'is_cart_payment': True
    })

@csrf_exempt
def payment_cart_fail(request):
    """Handle failed cart payment"""
    tran_id = request.POST.get('tran_id') or request.GET.get('tran_id')
    
    if tran_id:
        purchases = Purchase.objects.filter(transaction_id__startswith=tran_id)
        purchases.update(payment_status='failed')
    
    messages.error(request, 'Payment failed. Please try again.')
    return render(request, 'payment_failed.html', {'role': 'buyer'})

@csrf_exempt
def payment_cart_cancel(request):
    """Handle canceled cart payment"""
    tran_id = request.POST.get('tran_id') or request.GET.get('tran_id')
    
    if tran_id:
        purchases = Purchase.objects.filter(transaction_id__startswith=tran_id)
        purchases.update(payment_status='canceled')
    
    messages.warning(request, 'Payment was canceled.')
    return render(request, 'payment_canceled.html', {'role': 'buyer'})
