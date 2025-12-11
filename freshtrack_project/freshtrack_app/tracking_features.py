"""
Fresh Track Features Implementation
- Hour-Based Tracking
- Smart Alerts
- Save Money (Discounts)
- Reduce Waste
"""

from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import Product, Alert, Purchase
from django.db.models import Q

class HourBasedTracking:
    """Track exactly how many hours remain before expiry"""
    
    @staticmethod
    def get_hours_remaining(product):
        """Get exact hours remaining for a product"""
        now = timezone.now()
        if now >= product.expiry_datetime:
            return 0
        delta = product.expiry_datetime - now
        hours = delta.total_seconds() / 3600
        return round(hours, 1)
    
    @staticmethod
    def get_hours_status(product):
        """Get status based on hours remaining"""
        hours = HourBasedTracking.get_hours_remaining(product)
        
        if hours <= 0:
            return {'status': 'expired', 'class': 'danger', 'label': 'EXPIRED'}
        elif hours < 1:
            return {'status': 'last_chance', 'class': 'danger', 'label': f'{int(hours*60)} minutes left'}
        elif hours < 6:
            return {'status': 'urgent', 'class': 'danger', 'label': f'{hours:.1f}h left - HOT DEAL!'}
        elif hours < 24:
            return {'status': 'soon', 'class': 'warning', 'label': f'{hours:.1f}h left'}
        elif hours < 48:
            return {'status': 'warning', 'class': 'warning', 'label': f'{hours:.1f}h left'}
        else:
            return {'status': 'normal', 'class': 'success', 'label': f'{hours:.1f}h left'}
    
    @staticmethod
    def get_all_products_with_hours(queryset=None):
        """Get all products with hour tracking info"""
        if queryset is None:
            queryset = Product.objects.approved_available()
        
        products_with_hours = []
        for product in queryset:
            product.hours_remaining = HourBasedTracking.get_hours_remaining(product)
            product.hours_status = HourBasedTracking.get_hours_status(product)
            products_with_hours.append(product)
        
        # Sort by hours remaining (urgent items first)
        return sorted(products_with_hours, key=lambda x: x.hours_remaining)


class SmartAlerts:
    """Generate smart alerts for products nearing expiry"""
    
    @staticmethod
    def create_seller_alert(product, alert_level, message):
        """Create alert for seller about their product"""
        alert, created = Alert.objects.get_or_create(
            product=product,
            alert_type='seller',
            alert_level=alert_level,
            defaults={
                'message': message,
                'priority': SmartAlerts._get_priority(alert_level),
            }
        )
        return alert
    
    @staticmethod
    def create_buyer_alert(product, alert_level, message):
        """Create alert for buyers about hot deals"""
        alert, created = Alert.objects.get_or_create(
            product=product,
            alert_type='buyer',
            alert_level=alert_level,
            defaults={
                'message': message,
                'priority': SmartAlerts._get_priority(alert_level),
            }
        )
        return alert
    
    @staticmethod
    def _get_priority(alert_level):
        """Convert alert level to priority"""
        priority_map = {
            'last_chance': 1,  # Critical
            'urgent': 1,       # Critical
            'soon': 2,         # High
            'warning': 3,      # Medium
            'normal': 4,       # Low
        }
        return priority_map.get(alert_level, 4)
    
    @staticmethod
    def check_and_create_alerts(product):
        """Check product and create appropriate alerts"""
        hours = HourBasedTracking.get_hours_remaining(product)
        
        # Critical alerts (< 1 hour)
        if 0 < hours < 1:
            SmartAlerts.create_seller_alert(
                product, 'last_chance',
                f"⏰ URGENT: Product '{product.name}' expires in less than 1 hour! "
                f"Consider a deep discount to sell quickly."
            )
            SmartAlerts.create_buyer_alert(
                product, 'last_chance',
                f"🔥 LAST CHANCE: '{product.name}' expires in less than 1 hour! Grab it now!"
            )
        
        # Urgent alerts (1-6 hours)
        elif 1 <= hours < 6:
            SmartAlerts.create_seller_alert(
                product, 'urgent',
                f"⚠️ URGENT: Product '{product.name}' expires in {hours:.1f} hours. "
                f"Apply a discount to accelerate sales."
            )
            SmartAlerts.create_buyer_alert(
                product, 'urgent',
                f"🎉 HOT DEAL: '{product.name}' - {hours:.1f} hours left for amazing savings!"
            )
        
        # Soon alerts (6-24 hours)
        elif 6 <= hours < 24:
            SmartAlerts.create_seller_alert(
                product, 'soon',
                f"📢 REMINDER: Product '{product.name}' expires in {hours:.1f} hours."
            )
        
        # Warning alerts (24-48 hours)
        elif 24 <= hours < 48:
            SmartAlerts.create_seller_alert(
                product, 'warning',
                f"📋 INFO: Product '{product.name}' expires in {hours:.1f} hours."
            )
    
    @staticmethod
    def get_seller_alerts(user, unread_only=False):
        """Get all alerts for a seller"""
        try:
            seller_profile = user.seller_profile if hasattr(user, 'seller_profile') else None
            if not seller_profile:
                return Alert.objects.none()
            
            alerts = Alert.objects.filter(
                alert_type='seller',
                product__seller=seller_profile
            ).order_by('priority', '-created_at')
            
            if unread_only:
                alerts = alerts.filter(is_read=False)
            
            return alerts
        except:
            return Alert.objects.none()
    
    @staticmethod
    def mark_alert_as_read(alert):
        """Mark an alert as read"""
        alert.is_read = True
        alert.save()


class SaveMoney:
    """Find and promote discounted items nearing expiry"""
    
    @staticmethod
    def get_money_saving_deals(queryset=None):
        """Get products with discounts, sorted by potential savings"""
        if queryset is None:
            queryset = Product.objects.approved_available()
        
        deals = []
        for product in queryset:
            discount = product.get_final_discount()
            if discount > 0:
                savings = product.get_savings()
                deals.append({
                    'product': product,
                    'discount': discount,
                    'savings': float(savings),
                    'hours': HourBasedTracking.get_hours_remaining(product)
                })
        
        # Sort by savings amount (highest first)
        return sorted(deals, key=lambda x: x['savings'], reverse=True)
    
    @staticmethod
    def recommend_discount_for_product(product):
        """Recommend a discount based on expiry time"""
        hours = HourBasedTracking.get_hours_remaining(product)
        
        if hours <= 0:
            return 0  # Already expired
        elif hours < 1:
            return 50  # Less than 1 hour - deep discount
        elif hours < 6:
            return 35  # Urgent - significant discount
        elif hours < 12:
            return 25  # Soon - moderate discount
        elif hours < 24:
            return 15  # Within a day - light discount
        elif hours < 48:
            return 10  # Within 2 days - minimal discount
        
        return 0  # No discount needed
    
    @staticmethod
    @staticmethod
    def apply_auto_discount(product):
        """Automatically apply recommended discount"""
        recommended = SaveMoney.recommend_discount_for_product(product)
        if recommended > 0:
            product.discount_percent = recommended
            product.save()
            return recommended
        return 0
    
    @staticmethod
    def get_discounted_products_by_category(category=None):
        """Get all discounted products, optionally by category"""
        products = Product.objects.filter(
            Q(discount_percentage__gt=0) | Q(discount_percent__gt=0),
            status='approved',
            expiry_datetime__gt=timezone.now()
        ).select_related('seller')
        
        with_hours = []
        for product in products:
            with_hours.append({
                'product': product,
                'discount': product.get_final_discount(),
                'savings': float(product.get_savings()),
                'original': float(product.original_price or product.price),
                'discounted': float(product.get_discounted_price()),
            })
        
        return sorted(with_hours, key=lambda x: x['savings'], reverse=True)


class ReduceWaste:
    """Help prevent food and product waste"""
    
    @staticmethod
    def get_products_at_waste_risk(hours_threshold=6):
        """Get products at risk of being wasted (expiring soon)"""
        threshold_time = timezone.now() + timedelta(hours=hours_threshold)
        
        at_risk = Product.objects.filter(
            status='approved',
            expiry_datetime__lte=threshold_time,
            expiry_datetime__gt=timezone.now()
        ).select_related('seller')
        
        risk_products = []
        for product in at_risk:
            hours = HourBasedTracking.get_hours_remaining(product)
            quantity_at_risk = product.quantity  # Assuming quantity hasn't been purchased
            
            risk_products.append({
                'product': product,
                'hours': hours,
                'quantity': quantity_at_risk,
                'total_value': float(product.price * quantity_at_risk),
                'risk_level': ReduceWaste._calculate_risk_level(hours)
            })
        
        return sorted(risk_products, key=lambda x: x['hours'])
    
    @staticmethod
    def _calculate_risk_level(hours):
        """Calculate waste risk level"""
        if hours < 1:
            return 'critical'
        elif hours < 3:
            return 'high'
        elif hours < 6:
            return 'medium'
        return 'low'
    
    @staticmethod
    def get_waste_prevention_stats():
        """Get statistics about waste prevention efforts"""
        now = timezone.now()
        
        # Products saved by discount
        discounted_products = Product.objects.filter(
            Q(discount_percentage__gt=0) | Q(discount_percent__gt=0),
            status='approved',
            expiry_datetime__gt=now
        )
        
        total_discount_value = sum(
            float(p.get_savings() * p.quantity) for p in discounted_products
        )
        
        # Products at risk
        at_risk = Product.objects.filter(
            status='approved',
            expiry_datetime__lte=now + timedelta(hours=6),
            expiry_datetime__gt=now
        ).count()
        
        # Recently purchased (within last 24 hours)
        recent_purchases = Purchase.objects.filter(
            payment_status='success',
            purchased_at__gte=now - timedelta(hours=24)
        ).count()
        
        return {
            'total_discount_value': round(total_discount_value, 2),
            'products_at_risk': at_risk,
            'recent_purchases': recent_purchases,
            'estimated_waste_prevented': round(total_discount_value * 0.7, 2),  # Estimate 70% prevent waste
        }
    
    @staticmethod
    def get_expiry_calendar(days_ahead=7):
        """Get calendar of product expiries for the next N days"""
        now = timezone.now()
        calendar = {}
        
        for day in range(days_ahead):
            current_day = now + timedelta(days=day)
            day_start = current_day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            products = Product.objects.filter(
                status='approved',
                expiry_datetime__gte=day_start,
                expiry_datetime__lt=day_end
            ).count()
            
            calendar[current_day.date()] = products
        
        return calendar


class DashboardStats:
    """Get statistics for dashboard display"""
    
    @staticmethod
    def get_buyer_dashboard_stats(user):
        """Get stats for buyer dashboard"""
        return {
            'hot_deals': Product.objects.filter(
                status='approved',
                expiry_datetime__lt=timezone.now() + timedelta(hours=6),
                expiry_datetime__gt=timezone.now()
            ).count(),
            'total_savings': sum(
                float(p.get_savings()) for p in Product.objects.approved_available()
                if p.get_final_discount() > 0
            ),
            'recent_purchases': Purchase.objects.filter(
                buyer=user,
                payment_status='success'
            ).count(),
        }
    
    @staticmethod
    def get_seller_dashboard_stats(user):
        """Get stats for seller dashboard"""
        try:
            seller = user.seller_profile if hasattr(user, 'seller_profile') else None
            if not seller:
                return {}
            
            products = seller.products.all()
            
            return {
                'total_products': products.count(),
                'products_expiring_soon': products.filter(
                    expiry_datetime__lte=timezone.now() + timedelta(hours=24),
                    expiry_datetime__gt=timezone.now()
                ).count(),
                'products_expired': products.filter(
                    expiry_datetime__lte=timezone.now()
                ).count(),
                'total_quantity': sum(p.quantity for p in products),
                'value_at_risk': sum(
                    float(p.price * p.quantity) for p in products
                    if p.expiry_datetime <= timezone.now() + timedelta(hours=24)
                ),
            }
        except:
            return {}


def initialize_tracking_for_product(product):
    """Initialize all tracking features for a new product"""
    HourBasedTracking.get_hours_remaining(product)
    SmartAlerts.check_and_create_alerts(product)
    return True
