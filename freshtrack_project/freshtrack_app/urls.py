from django.urls import path
from . import views
from . import api_tracking

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('buyer/', views.buyer_dashboard, name='buyer_dashboard'),
    path('buyer/history/', views.buyer_history, name='buyer_history'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/buy/', views.buy_product, name='buy_product'),
    path('review/add/<int:purchase_id>/', views.add_review, name='add_review'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),
    
    # Shopping Cart URLs
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:cart_item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/checkout/', views.checkout_cart, name='checkout_cart'),
    path('cart/process-payment/', views.process_cart_payment, name='process_cart_payment'),
    path('payment/cart-success/', views.payment_cart_success, name='payment_cart_success'),
    path('payment/cart-fail/', views.payment_cart_fail, name='payment_cart_fail'),
    path('payment/cart-cancel/', views.payment_cart_cancel, name='payment_cart_cancel'),
    
    # Payment system URLs
    path('checkout/<int:product_id>/', views.checkout, name='checkout'),
    path('payment/initiate/<int:product_id>/', views.initiate_payment, name='initiate_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/fail/', views.payment_fail, name='payment_fail'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    path('payment/ipn/', views.payment_ipn, name='payment_ipn'),
    path('invoice/download/<int:purchase_id>/', views.download_invoice, name='download_invoice'),
    
    path('seller/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/add-product/', views.add_product, name='add_product'),
    path('seller/edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('seller/quick-edit/<int:product_id>/', views.quick_edit_product, name='quick_edit_product'),
    path('seller/alerts/', views.seller_alerts, name='seller_alerts'),
    path('seller/analytics/', views.seller_analytics, name='seller_analytics'),
    path('seller/apply-discount/<int:product_id>/', views.apply_discount, name='apply_discount'),
    path('seller/bulk-delete/', views.bulk_delete_products, name='bulk_delete_products'),
    path('seller/bulk-discount/', views.bulk_apply_discount, name='bulk_apply_discount'),
    path('alert/<int:alert_id>/read/', views.mark_alert_read, name='mark_alert_read'),
    path('alert/mark-all-read/', views.mark_all_alerts_read, name='mark_all_alerts_read'),
    path('alert/delete-product/<int:product_id>/', views.delete_product_from_alert, name='delete_product_from_alert'),
    
    path('moderation/', views.admin_dashboard, name='admin_dashboard'),
    path('moderation/sales-analytics/', views.admin_sales_analytics, name='admin_sales_analytics'),
    path('moderation/products/', views.admin_products, name='admin_products'),
    path('moderation/sellers/', views.admin_sellers, name='admin_sellers'),
    path('moderation/users/', views.admin_users, name='admin_users'),
    path('moderation/approve/<int:product_id>/', views.approve_product, name='approve_product'),
    path('moderation/reject/<int:product_id>/', views.reject_product, name='reject_product'),
    path('moderation/pending/<int:product_id>/', views.pending_product, name='pending_product'),
    path('moderation/approve-user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('moderation/reject-user/<int:user_id>/', views.reject_user, name='reject_user'),
    path('moderation/hold-user/<int:user_id>/', views.hold_user, name='hold_user'),
    path('moderation/approve-edit/<int:request_id>/', views.approve_edit_request, name='approve_edit_request'),
    path('moderation/reject-edit/<int:request_id>/', views.reject_edit_request, name='reject_edit_request'),
    
    # Tracking Features API
    path('api/product/<int:product_id>/hours/', api_tracking.api_product_hours, name='api_product_hours'),
    path('api/money-saving-deals/', api_tracking.api_money_saving_deals, name='api_money_saving_deals'),
    path('api/waste-risk-products/', api_tracking.api_waste_risk_products, name='api_waste_risk_products'),
    path('api/waste-stats/', api_tracking.api_waste_stats, name='api_waste_stats'),
    path('api/seller-alerts/', api_tracking.api_seller_alerts, name='api_seller_alerts'),
    path('api/alert/<int:alert_id>/read/', api_tracking.api_mark_alert_read, name='api_mark_alert_read'),
    path('api/product/<int:product_id>/apply-discount/', api_tracking.api_apply_recommended_discount, name='api_apply_discount'),
    path('api/hot-deals/', api_tracking.api_hot_deals, name='api_hot_deals'),
]
