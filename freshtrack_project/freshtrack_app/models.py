from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.db.models import Q

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

class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    company_info = models.TextField(blank=True, null=True)
    rating = models.FloatField(default=0)
    total_sales = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_verified = models.BooleanField(default=False)
    response_rate = models.FloatField(default=0, help_text="Response rate percentage")
    delivery_score = models.FloatField(default=0, help_text="Delivery score out of 5")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name
    
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
        """Restore products to their previous state when seller is re-approved"""
        # Products that were rejected due to seller rejection can be set back to pending
        # Admin still needs to approve them individually
        self.products.filter(status='rejected').update(status='pending')
    
    def get_rating_breakdown(self):
        """Returns percentage of each star rating"""
        total_reviews = Review.objects.filter(product__seller=self).count()
        if total_reviews == 0:
            return {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        
        breakdown = {}
        for star in range(1, 6):
            count = Review.objects.filter(product__seller=self, rating=star).count()
            breakdown[star] = round((count / total_reviews) * 100, 1)
        return breakdown

class Product(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]

    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.IntegerField(default=0, help_text="Discount percentage 0-100")
    discount_percent = models.IntegerField(default=0, help_text="Manual discount percentage (0-90)")
    quantity = models.IntegerField()
    manufacturing_date = models.DateTimeField()
    expiry_datetime = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Custom manager
    objects = ProductManager()

    def save(self, *args, **kwargs):
        # Store original price if not set
        if self.original_price is None:
            self.original_price = self.price
        
        # Auto-update status to expired if time has passed
        if timezone.now() >= self.expiry_datetime and self.status != 'expired':
            self.status = 'expired'
        
        super().save(*args, **kwargs)
    
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

    def remaining_seconds(self):
        """Returns remaining seconds until expiry"""
        now = timezone.now()
        if now >= self.expiry_datetime:
            return 0
        delta = self.expiry_datetime - now
        return max(0, int(delta.total_seconds()))

    def remaining_hours(self):
        return max(0, int(self.remaining_seconds() / 3600))

    def countdown_display(self):
        """Returns countdown display - ONLY SECONDS"""
        seconds = self.remaining_seconds()
        if seconds <= 0:
            return "EXPIRED"
        return f"{seconds} seconds"

    def alert_level(self):
        seconds = self.remaining_seconds()
        if seconds <= 0:
            return 'expired'
        elif seconds < 3600:  # < 1 hour
            return 'last_chance'
        elif seconds < 21600:  # < 6 hours
            return 'urgent'
        elif seconds < 86400:  # < 24 hours
            return 'soon'
        elif seconds < 172800:  # < 48 hours
            return 'warning'
        return 'normal'

    def recommended_discount(self):
        """Returns recommended discount based on expiry time"""
        seconds = self.remaining_seconds()
        hours = seconds / 3600
        
        if hours <= 0:
            return 0
        elif hours <= 6:
            return 30
        elif hours <= 24:
            return 10
        elif hours <= 48:
            return 5
        return 0

    def has_discount(self):
        return self.discount_percentage > 0 or self.discount_percent > 0

    def get_final_discount(self):
        """Returns the effective discount (manual or auto)"""
        return max(self.discount_percent, self.discount_percentage)

    def get_discounted_price(self):
        """Calculate and return the discounted price"""
        discount = self.get_final_discount()
        if discount > 0:
            return self.price * (Decimal('1') - Decimal(str(discount)) / Decimal('100'))
        return self.price

    def get_savings(self):
        """Calculate savings amount"""
        discount = self.get_final_discount()
        if discount > 0:
            return self.price * (Decimal(str(discount)) / Decimal('100'))
        return Decimal('0')

    def apply_discount(self, percentage):
        """Apply discount and update price"""
        if percentage < 0 or percentage > 100:
            return False
        
        if self.original_price is None:
            self.original_price = self.price
        
        self.discount_percentage = percentage
        self.price = self.original_price * (Decimal('1') - Decimal(str(percentage)) / Decimal('100'))
        self.save()
        return True

    def get_average_rating(self):
        """Calculate average rating from reviews"""
        reviews = self.reviews.all()
        if not reviews:
            return 0
        total = sum(review.rating for review in reviews)
        return round(total / len(reviews), 1)
    
    def get_rating_count(self):
        """Get total number of reviews"""
        return self.reviews.count()
    
    def get_rating_stars(self):
        """Get rating as stars display"""
        avg = self.get_average_rating()
        full_stars = int(avg)
        half_star = 1 if (avg - full_stars) >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        return {
            'full': full_stars,
            'half': half_star,
            'empty': empty_stars,
            'average': avg
        }

    def __str__(self):
        return self.name

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    purchase = models.OneToOneField('Purchase', on_delete=models.CASCADE, related_name='review', null=True, blank=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'buyer']

    def __str__(self):
        return f"{self.buyer.username} - {self.product.name} - {self.rating}★"

class Alert(models.Model):
    ALERT_TYPE_CHOICES = [
        ('seller', 'Seller Alert'),
        ('buyer', 'Buyer Alert'),
    ]
    
    PRIORITY_CHOICES = [
        (1, 'Critical'),
        (2, 'High'),
        (3, 'Medium'),
        (4, 'Low'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=10, choices=ALERT_TYPE_CHOICES)
    alert_level = models.CharField(max_length=20)
    message = models.TextField()
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=3)
    is_read = models.BooleanField(default=False)
    action_taken = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['priority', '-created_at']

    def __str__(self):
        return f"{self.alert_type} - {self.alert_level}"

class UserRole(models.Model):
    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    ]
    
    APPROVAL_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')
    is_approved = models.CharField(max_length=20, choices=APPROVAL_STATUS, default='pending')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
    def is_seller_active(self):
        """Check if this is an active approved seller"""
        return self.role == 'seller' and self.is_approved == 'approved'

class Purchase(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('initiated', 'Payment Initiated'),
        ('pending', 'Pending'),
        ('success', 'Payment Success'),
        ('failed', 'Payment Failed'),
        ('canceled', 'Payment Canceled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Credit/Debit Card'),
        ('bkash', 'bKash'),
        ('nagad', 'Nagad'),
        ('rocket', 'Rocket'),
        ('cellfin', 'CellFin'),
        ('other', 'Other'),
    ]
    
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=255)
    seller_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment fields
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    gateway_response = models.TextField(null=True, blank=True, help_text="JSON response from payment gateway")
    
    purchased_at = models.DateTimeField(auto_now_add=True)
    payment_completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.buyer.username} - {self.product_name} - {self.payment_status}"
    
    class Meta:
        ordering = ['-purchased_at']

class Cart(models.Model):
    """Shopping cart for buyers to add multiple products before checkout"""
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-added_at']
        unique_together = ['buyer', 'product']
    
    def get_total_price(self):
        """Calculate total price for this cart item"""
        return self.product.get_discounted_price() * self.quantity
    
    def __str__(self):
        return f"{self.buyer.username} - {self.product.name} x {self.quantity}"

class ProductEditRequest(models.Model):
    """Stores pending edit requests from sellers that require admin approval"""
    EDIT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='edit_requests')
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE)
    
    # Original values
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    original_discount = models.IntegerField()
    original_quantity = models.IntegerField()
    
    # Requested changes
    new_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    new_discount = models.IntegerField(null=True, blank=True)
    new_quantity = models.IntegerField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=EDIT_STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_edits')
    
    def __str__(self):
        return f"Edit Request for {self.product.name} - {self.status}"
    
    def apply_changes(self):
        """Apply the approved changes to the product"""
        if self.new_price is not None:
            self.product.price = self.new_price
        if self.new_discount is not None:
            self.product.discount_percent = self.new_discount
        if self.new_quantity is not None:
            self.product.quantity = self.new_quantity
        self.product.save()
    
    class Meta:
        ordering = ['-requested_at']
