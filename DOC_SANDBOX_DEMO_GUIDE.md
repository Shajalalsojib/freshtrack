# 🧪 SSLCommerz Sandbox Demo Configuration Guide

## ✅ Current Configuration

Your FreshTrack system is **already configured** with SSLCommerz Sandbox (demo) mode!

### Configuration in `settings.py`:
```python
SSLCOMMERZ_STORE_ID = 'testbox'
SSLCOMMERZ_STORE_PASSWORD = 'qwerty'
SSLCOMMERZ_IS_SANDBOX = True
```

### API Endpoints:
```python
# Sandbox URLs (currently active)
SSLCOMMERZ_API_URL = 'https://sandbox.sslcommerz.com/gwprocess/v4/api.php'
SSLCOMMERZ_VALIDATION_URL = 'https://sandbox.sslcommerz.com/validator/api/validationserverAPI.php'
```

---

## 🎮 How Sandbox Mode Works

### What is Sandbox Mode?
- **Test environment** provided by SSLCommerz
- **No real money** is processed
- Uses **fake/demo credentials**
- Simulates real payment flow
- Perfect for development and testing

### What Happens:
1. ✅ Creates real Purchase records in database
2. ✅ Reduces product stock (for testing)
3. ✅ Generates transaction IDs
4. ✅ Redirects to SSLCommerz demo gateway
5. ✅ Processes demo payment
6. ✅ Returns to your app with success/fail
7. ✅ Verifies with sandbox validation API
8. ❌ **NO real money charged**

---

## 💳 Test Credentials - Credit/Debit Cards

### Test Visa Card (ALWAYS WORKS):
```
Card Number: 4111 1111 1111 1111
Expiry Date: 12/25 (any future date)
CVV: 123 (any 3 digits)
Cardholder: Test User (any name)
```

### Test Mastercard:
```
Card Number: 5555 5555 5555 4444
Expiry Date: 12/25
CVV: 123
Cardholder: Test User
```

### Test American Express:
```
Card Number: 3782 822463 10005
Expiry Date: 12/25
CVV: 1234 (4 digits for AMEX)
Cardholder: Test User
```

### Important Notes:
- ✅ Any future expiry date works (e.g., 12/25, 01/26, 06/30)
- ✅ Any CVV works (123, 456, 789, etc.)
- ✅ Any cardholder name works
- ✅ These cards only work in **Sandbox mode**
- ❌ Do NOT use real card numbers in sandbox!

---

## 📱 Test Credentials - Mobile Banking

### On Gateway Page:
When you select bKash, Nagad, Rocket, or CellFin, the sandbox gateway page will show:

**For bKash/Nagad/Rocket:**
1. Select the payment method
2. Gateway shows demo form
3. Enter any test mobile number (e.g., 01700000000)
4. Click "Success" button to simulate successful payment
5. OR click "Fail" button to simulate failed payment

**Demo Buttons Available:**
- ✅ **Success** - Simulates successful payment
- ❌ **Fail** - Simulates failed payment
- ⚠️ **Cancel** - Simulates canceled payment

---

## 🔄 Complete Demo Payment Flow

### Step 1: Navigate to Checkout
```
http://127.0.0.1:8000/
↓
Login as Buyer
↓
Click "Buy Now" on any product
↓
Select quantity → Click "Proceed to Checkout"
```

### Step 2: Select Payment Method
```
On checkout page:
✅ Read the purple "SANDBOX MODE" box
✅ Note the test card credentials displayed
✅ Select payment method (Card recommended)
✅ Click "🔒 Proceed to Payment"
```

### Step 3: SSLCommerz Demo Gateway
```
You'll be redirected to:
https://sandbox.sslcommerz.com/...

What you'll see:
📋 Demo payment form
💳 Input fields for card details
🧪 "This is a test transaction" notice
```

### Step 4: Enter Test Credentials
```
If Card selected:
→ Enter: 4111 1111 1111 1111
→ Expiry: 12/25
→ CVV: 123
→ Name: Test User
→ Click "Submit" or "Pay Now"

If Mobile Banking selected:
→ Enter any test number: 01700000000
→ Click "Success" button (for successful demo)
→ OR click "Fail" button (for failed demo)
```

### Step 5: Gateway Processing
```
Gateway processes demo payment:
✅ Validates test credentials
✅ Simulates payment processing
✅ Generates demo transaction
```

### Step 6: Redirect to Your App
```
Success Case:
→ Redirects to: /payment/success/
→ Shows: "Payment Successful!" with DEMO badge
→ Stock reduced
→ Purchase record created

Failure Case:
→ Redirects to: /payment/fail/
→ Shows: "Payment Failed" with test card info
→ Stock NOT reduced

Cancel Case:
→ Redirects to: /payment/cancel/
→ Shows: "Payment Canceled"
→ Stock NOT reduced
```

### Step 7: Backend Verification
```python
# Your backend automatically:
1. Receives callback from gateway
2. Extracts transaction_id and val_id
3. Calls SSLCommerz Validation API:
   GET https://sandbox.sslcommerz.com/validator/api/validationserverAPI.php
   params: {val_id, store_id, store_passwd}
4. Checks if status == 'VALID' or 'VALIDATED'
5. Updates purchase.payment_status = 'success'
6. Reduces product.quantity
7. Updates seller stats
8. Shows success page
```

---

## 🎯 Testing Scenarios

### ✅ Successful Payment Demo
```bash
# What to do:
1. Select payment method: Card
2. Enter test card: 4111 1111 1111 1111
3. Expiry: 12/25, CVV: 123
4. Click Submit

# Expected Result:
✓ Redirect to success page
✓ See "Payment Successful!" with DEMO badge
✓ Order details displayed
✓ Stock reduced
✓ Purchase in buyer history
✓ Console shows verification logs

# Database Changes:
✓ Purchase.payment_status = 'success'
✓ Product.quantity reduced
✓ Seller.total_sales increased
```

### ❌ Failed Payment Demo
```bash
# What to do:
Option 1: Use invalid card (any random numbers)
Option 2: On gateway page, click "Fail" button
Option 3: Close browser before completing

# Expected Result:
✓ Redirect to fail page
✓ See "Payment Failed" with test card info
✓ Helpful error message
✗ Stock NOT reduced
✗ Payment NOT processed

# Database Changes:
✓ Purchase.payment_status = 'failed'
✗ Product.quantity unchanged
✗ Seller stats unchanged
```

### ⚠️ Canceled Payment Demo
```bash
# What to do:
1. Start payment
2. On gateway page, click "Cancel" button

# Expected Result:
✓ Redirect to cancel page
✓ See "Payment Canceled" message
✗ Stock NOT reduced
✗ Payment NOT processed

# Database Changes:
✓ Purchase.payment_status = 'canceled'
✗ Product.quantity unchanged
```

---

## 🔍 Verification & Debugging

### Watch Console Logs
Your terminal shows detailed logs:
```
=============================================================
Initiating payment for transaction: FT1A2B3C4D5E
Amount: ৳150.00 | Method: card
SSLCommerz Store ID: testbox
API URL: https://sandbox.sslcommerz.com/...
Sandbox Mode: True
=============================================================

SSLCommerz Response Status Code: 200
Parsed Response Status: SUCCESS
Gateway URL: https://sandbox.sslcommerz.com/...

✓ Payment initiation successful! Redirecting to gateway

=============================================================
Payment Success Callback Received
Transaction ID: FT1A2B3C4D5E
Validation ID: 2024112900...
=============================================================

✓ Purchase found: 123 | Buyer: testuser
Verifying payment with SSLCommerz...
Validation Response Status: 200
✓ Payment verified successfully!
Reducing stock: Fresh Apple | Current: 10 | Ordered: 1
New stock level: 9
✓ Updated seller stats: Fresh Fruits Ltd
```

### Check Database
```bash
# In Django admin:
http://127.0.0.1:8000/admin/

# Check Purchase model:
- payment_status should be 'success' (or 'failed'/'canceled')
- transaction_id should be unique (FT...)
- gateway_response should contain JSON data
- payment_completed_at should have timestamp

# Check Product model:
- quantity should be reduced (if payment successful)

# Check SellerProfile model:
- total_sales should be incremented
- total_revenue should be updated
```

---

## 🧪 Sandbox vs Production

### Sandbox (Current - Demo):
```
Store ID: testbox
Password: qwerty
URL: sandbox.sslcommerz.com
Purpose: Testing & Development
Money: NO real money
Cards: Test cards only (4111 1111 1111 1111)
Status: ✅ CURRENTLY ACTIVE
```

### Production (Future - Real):
```
Store ID: your_live_store_id
Password: your_live_password
URL: securepay.sslcommerz.com
Purpose: Real business transactions
Money: REAL money processed
Cards: Real customer cards
Status: ⏸️ NOT ACTIVE (requires registration)
```

---

## 📋 Sandbox Features

### What Works in Sandbox:
- ✅ Complete payment flow
- ✅ All payment methods (Card, bKash, Nagad, etc.)
- ✅ Success/Fail/Cancel redirects
- ✅ Transaction verification
- ✅ Gateway callbacks
- ✅ IPN notifications
- ✅ Stock management
- ✅ Order history
- ✅ Console logging

### What's Different from Production:
- 🧪 Uses test credentials (not real cards)
- 🧪 No real money charged
- 🧪 Faster processing (instant)
- 🧪 Can force success/fail outcomes
- 🧪 Unlimited testing (no limits)
- 🧪 Demo gateway interface

---

## 🛠️ Configuration Locations

### 1. Backend Settings
```python
# File: freshtrack_project/settings.py
SSLCOMMERZ_STORE_ID = 'testbox'
SSLCOMMERZ_STORE_PASSWORD = 'qwerty'
SSLCOMMERZ_IS_SANDBOX = True  # ← Controls sandbox mode
```

### 2. Views
```python
# File: freshtrack_app/views.py
# Functions:
- initiate_payment() → Calls sandbox API
- payment_success() → Verifies with sandbox validation API
- payment_fail() → Handles failed demo payments
- payment_cancel() → Handles canceled demo payments
```

### 3. URLs
```python
# File: freshtrack_app/urls.py
path('checkout/<int:product_id>/', views.checkout),
path('payment/initiate/<int:product_id>/', views.initiate_payment),
path('payment/success/', views.payment_success),
path('payment/fail/', views.payment_fail),
path('payment/cancel/', views.payment_cancel),
path('payment/ipn/', views.payment_ipn),
```

### 4. Templates
```html
<!-- Files updated to show DEMO badges: -->
- checkout.html → Shows test credentials
- payment_success.html → Shows DEMO badge
- payment_failed.html → Shows test card info
- payment_canceled.html → Shows DEMO badge
```

---

## 🎓 Understanding Sandbox Gateway

### When You Click "Proceed to Payment":
```
1. Your app sends request to:
   POST https://sandbox.sslcommerz.com/gwprocess/v4/api.php
   
2. With data:
   - store_id: testbox
   - store_passwd: qwerty
   - total_amount: 150.00
   - tran_id: FT1A2B3C4D5E
   - success_url: your_app/payment/success/
   - fail_url: your_app/payment/fail/
   - customer info
   - product info

3. Gateway responds with:
   {
     "status": "SUCCESS",
     "GatewayPageURL": "https://sandbox.sslcommerz.com/EasyCheckOut/..."
   }

4. Your app redirects buyer to GatewayPageURL

5. Buyer sees demo payment form
```

### On Gateway Page:
```
SSLCommerz Sandbox Demo Gateway
================================

[Test Transaction Notice]

Card Payment:
  Card Number: [________]
  Expiry: [__/__]
  CVV: [___]
  Name: [________]
  
  [Submit Button]

OR

Mobile Banking:
  Select Method: [bKash ▼]
  Mobile: [___________]
  
  [Success Button] [Fail Button]
```

### After Submitting:
```
Gateway processes → Redirects to your app:

Success: your_app/payment/success/?tran_id=FT...&val_id=...
Fail: your_app/payment/fail/?tran_id=FT...
Cancel: your_app/payment/cancel/?tran_id=FT...
```

---

## 🔐 Security in Sandbox

### Still Secure:
- ✅ Uses HTTPS
- ✅ Validates credentials
- ✅ Verifies transactions
- ✅ CSRF protection
- ✅ Secure callbacks

### Differences from Production:
- 🧪 Test credentials widely known
- 🧪 No KYC requirements
- 🧪 No transaction limits
- 🧪 Predictable outcomes

---

## 📝 Quick Test Checklist

Before testing, make sure:

- [ ] Server is running: `python manage.py runserver`
- [ ] Logged in as Buyer
- [ ] Products available with stock
- [ ] Internet connection active
- [ ] Browser allows redirects
- [ ] Console/terminal visible for logs

Test successful payment:
- [ ] Select product → Buy Now
- [ ] Choose Card payment method
- [ ] Click Proceed to Payment
- [ ] Enter: 4111 1111 1111 1111
- [ ] Enter: 12/25, CVV: 123
- [ ] Click Submit
- [ ] See success page with DEMO badge
- [ ] Check stock reduced
- [ ] Check purchase in history

---

## 💡 Pro Tips

1. **Always use test card 4111 1111 1111 1111** - It always works!
2. **Watch terminal logs** - They show everything
3. **Check purple DEMO box** on checkout page for credentials
4. **Use Success/Fail buttons** in mobile banking for testing
5. **Test all payment methods** - Card, bKash, Nagad, Rocket
6. **Try failure scenarios** too - Click fail button or use invalid card
7. **Check database** after each test
8. **Keep browser console open** for any JavaScript errors

---

## 🚀 Ready to Test!

Your system is **fully configured** for sandbox testing!

**Just do:**
```bash
python manage.py runserver
```

Then test with:
- Card: **4111 1111 1111 1111**
- Expiry: **12/25**
- CVV: **123**

**It will work perfectly!** 🎉

---

## 📞 Need Help?

**Issue:** "Failed to initiate payment"
- Check internet connection
- Verify settings.py has store_id='testbox'
- Check console logs for error details

**Issue:** Gateway page doesn't load
- Check SSLCOMMERZ_API_URL is sandbox URL
- Verify network allows HTTPS connections
- Try different browser

**Issue:** Payment succeeds but stock not reduced
- Check payment_success view logs
- Verify validation API response
- Check Purchase.payment_status in database

**Issue:** Can't see DEMO badges
- Clear browser cache
- Hard refresh (Ctrl+F5)
- Check template files updated

---

**Status:** ✅ READY FOR SANDBOX TESTING
**Mode:** 🧪 DEMO/TEST ENVIRONMENT
**Real Money:** ❌ NO (Sandbox Only)
**Last Updated:** November 29, 2025
