# FreshTrack Eco-Friendly Design Guide

## 🌿 Overview
This guide explains the new fresh, eco-friendly design system for FreshTrack.

## 🎨 Color Palette

### Primary Colors
- **Fresh Primary**: `#10b981` (Emerald green) - Main brand color
- **Fresh Secondary**: `#34d399` (Light green) - Accents & highlights
- **Fresh Accent**: `#6ee7b7` (Mint) - Subtle highlights

### Earthy Tones
- **Earth Brown**: `#92857a` - Text accents
- **Earth Sand**: `#f5f3f0` - Soft backgrounds
- **Earth Cream**: `#faf9f7` - Page background

### Status Colors
- **Fresh**: `#10b981` ✓ (Green) - Product is fresh
- **Warning**: `#f59e0b` ⚠ (Amber) - Expiring within 3 days
- **Urgent**: `#f97316` 🔥 (Orange) - Expiring within 1 day
- **Critical**: `#ef4444` ❗ (Red) - Expiring today
- **Expired**: `#6b7280` ✕ (Gray) - Already expired

## 📋 Implementation Steps

### Step 1: Update Your Templates

Replace the old `style.css` link with the new eco-friendly stylesheet:

```html
<!-- In your base.html or individual templates -->
<link rel="stylesheet" href="{% static 'css/freshtrack-eco.css' %}">
```

### Step 2: Add Summary Cards to Dashboards

**Buyer Dashboard Example:**

```html
<!-- Add this after the h1 heading -->
<div class="summary-cards">
    <div class="summary-card">
        <div class="summary-card-icon">🛒</div>
        <div class="summary-card-value">{{ total_products }}</div>
        <div class="summary-card-label">Available Products</div>
    </div>
    
    <div class="summary-card">
        <div class="summary-card-icon">⚠️</div>
        <div class="summary-card-value">{{ expiring_soon }}</div>
        <div class="summary-card-label">Expiring Soon</div>
    </div>
    
    <div class="summary-card">
        <div class="summary-card-icon">🌿</div>
        <div class="summary-card-value">{{ fresh_products }}</div>
        <div class="summary-card-label">Fresh Items</div>
    </div>
    
    <div class="summary-card">
        <div class="summary-card-icon">🏪</div>
        <div class="summary-card-value">{{ total_sellers }}</div>
        <div class="summary-card-label">Active Sellers</div>
    </div>
</div>
```

**Seller Dashboard Example:**

```html
<div class="summary-cards">
    <div class="summary-card">
        <div class="summary-card-icon">📦</div>
        <div class="summary-card-value">{{ total_products }}</div>
        <div class="summary-card-label">Your Products</div>
    </div>
    
    <div class="summary-card">
        <div class="summary-card-icon">💰</div>
        <div class="summary-card-value">৳{{ total_revenue|floatformat:2 }}</div>
        <div class="summary-card-label">Total Revenue</div>
    </div>
    
    <div class="summary-card">
        <div class="summary-card-icon">📈</div>
        <div class="summary-card-value">{{ total_sales }}</div>
        <div class="summary-card-label">Total Sales</div>
    </div>
    
    <div class="summary-card">
        <div class="summary-card-icon">⏰</div>
        <div class="summary-card-value">{{ expiring_soon }}</div>
        <div class="summary-card-label">Expiring Soon</div>
    </div>
</div>
```

### Step 3: Update Product Cards

Replace your current product card structure with:

```html
<div class="product-grid">
    {% for product in products %}
    <div class="product-card">
        <!-- Product Image -->
        <div class="product-image">
            <!-- Image will show emoji placeholder by default -->
            <!-- You can replace with: <img src="{{ product.image.url }}" alt="{{ product.name }}"> -->
        </div>
        
        <!-- Product Header -->
        <div class="product-header">
            <h3 class="product-name">{{ product.name }}</h3>
            <div class="product-price">৳{{ product.price|floatformat:2 }}</div>
        </div>
        
        <!-- Product Info -->
        <div class="product-info">
            <div class="info-row">
                <span class="label">Seller:</span>
                <span class="value">{{ product.seller.company_name }}</span>
            </div>
            
            <div class="info-row">
                <span class="label">Stock:</span>
                <span class="value">{{ product.quantity }} units</span>
            </div>
            
            <div class="info-row">
                <span class="label">Expires:</span>
                <span class="value">{{ product.expiry_datetime|date:"M d, Y" }}</span>
            </div>
            
            <!-- Countdown Timer -->
            <div class="countdown-timer" id="countdown-{{ product.id }}">
                Calculating...
            </div>
            
            <!-- Urgency Badge -->
            <span class="urgency-badge {{ product.urgency_level }}">
                {{ product.urgency_level|title }}
            </span>
        </div>
        
        <!-- Product Footer -->
        <div class="product-footer">
            <a href="{% url 'product_detail' product.id %}" class="btn btn-primary btn-block">
                View Details
            </a>
        </div>
    </div>
    {% endfor %}
</div>
```

### Step 4: Add Urgency Badge Filter (Optional)

Create a template filter to calculate urgency level:

**In `templatetags/product_filters.py`:**

```python
from datetime import timedelta
from django.utils import timezone

@register.filter
def urgency_level(expiry_datetime):
    """Calculate urgency level based on expiry time"""
    if not expiry_datetime:
        return 'normal'
    
    now = timezone.now()
    if expiry_datetime < now:
        return 'expired'
    
    time_left = expiry_datetime - now
    
    if time_left.total_seconds() < 3600:  # Less than 1 hour
        return 'critical'
    elif time_left.days == 0:  # Same day
        return 'urgent'
    elif time_left.days <= 3:  # 3 days or less
        return 'warning'
    elif time_left.days <= 7:  # Up to 1 week
        return 'normal'
    else:
        return 'fresh'
```

**Usage in template:**

```html
<span class="urgency-badge {{ product.expiry_datetime|urgency_level }}">
    {{ product.expiry_datetime|urgency_level|title }}
</span>
```

### Step 5: Update Navigation

Your navigation should automatically use the new eco-friendly styles. Make sure your HTML follows this structure:

```html
<nav class="navbar">
    <div class="navbar-content">
        <a href="{% url 'home' %}" class="logo">FreshTrack</a>
        
        <ul class="nav-links">
            <li><a href="{% url 'buyer_dashboard' %}">Products</a></li>
            <li><a href="{% url 'buyer_history' %}">My Orders</a></li>
            <li><a href="{% url 'logout' %}">Logout</a></li>
        </ul>
    </div>
</nav>
```

## 🎯 Design Features

### 1. **Leaf Animations**
- Logo has floating leaf animation
- Product images have gentle floating effect
- Summary card icons bounce subtly

### 2. **Fresh Color Scheme**
- Soft green gradients throughout
- Earthy cream background with subtle pattern
- White cards with green accents

### 3. **Modern UI Elements**
- Rounded corners (0.75rem - 1.5rem)
- Soft shadows with green tint
- Smooth transitions (300ms)
- Hover effects with lift animation

### 4. **Urgency System**
- **Fresh** (7+ days): Green with checkmark ✓
- **Normal** (4-7 days): Blue
- **Warning** (2-3 days): Amber with warning ⚠
- **Urgent** (1 day): Orange with fire 🔥 + pulse animation
- **Critical** (<1 day): Red with alert ❗ + fast pulse
- **Expired**: Gray with X ✕

### 5. **Responsive Design**
- Mobile-first approach
- Grid adjusts automatically
- Touch-friendly button sizes
- Collapsible navigation on mobile

## 📱 Responsive Breakpoints

- **Desktop**: 1280px+
- **Tablet**: 768px - 1279px
- **Mobile**: 320px - 767px

## 🔧 Customization Tips

### Change Primary Color
```css
:root {
    --fresh-primary: #10b981; /* Change this to your preferred green */
}
```

### Adjust Card Spacing
```css
:root {
    --space-xl: 2rem; /* Increase for more spacing */
}
```

### Modify Border Radius
```css
:root {
    --radius-xl: 1.5rem; /* Make cards more/less rounded */
}
```

## ✨ Icons Reference

Use these emoji icons throughout the interface:

- 🌿 Leaf - Brand, freshness
- 🌱 Seedling - Growth, new
- 🥬 Leafy Green - Products
- 🛒 Shopping Cart - Orders
- 📦 Package - Inventory
- 💰 Money Bag - Revenue
- 📈 Chart - Analytics
- ⏰ Clock - Time
- ⚠️ Warning - Alerts
- 🔥 Fire - Urgent
- ✓ Checkmark - Success
- ✕ X Mark - Error/Expired
- ♻️ Recycle - Sustainability

## 📝 Complete Example Template

See `buyer_dashboard_example.html` for a full working example with all components integrated.

## 🚀 Migration Checklist

- [ ] Replace old `style.css` with `freshtrack-eco.css`
- [ ] Add summary cards to all dashboards
- [ ] Update product card structure
- [ ] Add urgency badge filter
- [ ] Test on mobile devices
- [ ] Verify all buttons use new classes
- [ ] Check countdown timers work
- [ ] Test hover animations

## 💡 Best Practices

1. **Use semantic HTML** - Proper heading hierarchy
2. **Keep it clean** - Don't overcrowd cards
3. **Highlight expiry** - Make urgency badges prominent
4. **Mobile-first** - Test on small screens first
5. **Accessibility** - Use proper color contrast
6. **Performance** - Optimize images if you add them

## 🎨 Design Philosophy

**FreshTrack's eco-friendly design embodies:**
- 🌿 **Freshness** - Clean, crisp, inviting
- 🌱 **Growth** - Dynamic animations, positive vibes
- ♻️ **Sustainability** - Earthy tones, natural feel
- 🧘 **Calm** - Soft colors, ample spacing
- 📱 **Modern** - Responsive, touch-friendly

---

**Need Help?** Check existing templates in `freshtrack_app/templates/` for examples.
