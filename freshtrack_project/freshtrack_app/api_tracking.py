"""
API endpoints for tracking features
Provides JSON data for AJAX requests and dynamic updates
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Product, Alert
from .tracking_features import HourBasedTracking, SmartAlerts, SaveMoney, ReduceWaste
import json


@login_required
@require_http_methods(["GET"])
def api_product_hours(request, product_id):
    """Get real-time hours remaining for a product"""
    try:
        product = Product.objects.get(id=product_id)
        
        # Check visibility
        if not product.is_visible_to_buyers() and request.user.username != product.seller.user.username:
            return JsonResponse({'error': 'Not found'}, status=404)
        
        hours = HourBasedTracking.get_hours_remaining(product)
        status = HourBasedTracking.get_hours_status(product)
        
        return JsonResponse({
            'hours': hours,
            'status': status['status'],
            'label': status['label'],
            'class': status['class']
        })
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)


@login_required
@require_http_methods(["GET"])
def api_money_saving_deals(request):
    """Get top money-saving deals"""
    try:
        deals = SaveMoney.get_money_saving_deals(Product.objects.approved_available())[:10]
        
        response_data = []
        for deal in deals:
            response_data.append({
                'id': deal['product'].id,
                'name': deal['product'].name,
                'discount': deal['discount'],
                'savings': deal['savings'],
                'hours': deal['hours'],
                'price': float(deal['product'].price),
                'discounted_price': float(deal['product'].get_discounted_price()),
            })
        
        return JsonResponse({
            'deals': response_data,
            'count': len(response_data)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def api_waste_risk_products(request):
    """Get products at waste risk"""
    try:
        risk_products = ReduceWaste.get_products_at_waste_risk(hours_threshold=24)[:10]
        
        response_data = []
        for product_risk in risk_products:
            product = product_risk['product']
            response_data.append({
                'id': product.id,
                'name': product.name,
                'hours': product_risk['hours'],
                'quantity': product_risk['quantity'],
                'value': product_risk['total_value'],
                'risk_level': product_risk['risk_level'],
            })
        
        return JsonResponse({
            'products': response_data,
            'count': len(response_data)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def api_waste_stats(request):
    """Get waste prevention statistics"""
    try:
        stats = ReduceWaste.get_waste_prevention_stats()
        
        return JsonResponse({
            'total_discount_value': stats['total_discount_value'],
            'products_at_risk': stats['products_at_risk'],
            'recent_purchases': stats['recent_purchases'],
            'estimated_waste_prevented': stats['estimated_waste_prevented'],
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def api_seller_alerts(request):
    """Get seller alerts"""
    try:
        alerts = SmartAlerts.get_seller_alerts(request.user, unread_only=True)
        
        response_data = []
        for alert in alerts:
            response_data.append({
                'id': alert.id,
                'product_name': alert.product.name,
                'message': alert.message,
                'priority': alert.priority,
                'alert_level': alert.alert_level,
                'created_at': alert.created_at.isoformat(),
            })
        
        return JsonResponse({
            'alerts': response_data,
            'count': len(response_data)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def api_mark_alert_read(request, alert_id):
    """Mark an alert as read"""
    try:
        alert = Alert.objects.get(id=alert_id)
        
        # Check if user owns this alert
        if alert.product.seller.user != request.user:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        SmartAlerts.mark_alert_as_read(alert)
        
        return JsonResponse({'status': 'success', 'message': 'Alert marked as read'})
    except Alert.DoesNotExist:
        return JsonResponse({'error': 'Alert not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def api_apply_recommended_discount(request, product_id):
    """Apply recommended discount to a product"""
    try:
        product = Product.objects.get(id=product_id)
        
        # Check if user is the seller
        if product.seller.user != request.user:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        recommended = SaveMoney.recommend_discount_for_product(product)
        
        if recommended > 0:
            product.discount_percent = recommended
            product.save()
            
            # Update alerts
            SmartAlerts.check_and_create_alerts(product)
            
            return JsonResponse({
                'status': 'success',
                'discount': recommended,
                'original_price': float(product.original_price or product.price),
                'discounted_price': float(product.get_discounted_price()),
                'message': f'Discount of {recommended}% applied successfully!'
            })
        else:
            return JsonResponse({
                'status': 'info',
                'message': 'No discount needed at this time'
            })
    
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def api_hot_deals(request):
    """Get hot deals (products expiring within 6 hours)"""
    try:
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Q
        
        now = timezone.now()
        hot_deals = Product.objects.filter(
            status='approved',
            expiry_datetime__lte=now + timedelta(hours=6),
            expiry_datetime__gt=now
        ).select_related('seller').order_by('expiry_datetime')[:20]
        
        response_data = []
        for product in hot_deals:
            hours = HourBasedTracking.get_hours_remaining(product)
            response_data.append({
                'id': product.id,
                'name': product.name,
                'hours': hours,
                'discount': product.get_final_discount(),
                'original_price': float(product.original_price or product.price),
                'discounted_price': float(product.get_discounted_price()),
                'savings': float(product.get_savings()),
            })
        
        return JsonResponse({
            'deals': response_data,
            'count': len(response_data)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
