# 🎮 Quick Sandbox Demo Test - FreshTrack

## ⚡ 30-Second Test

```bash
# 1. Start server
python manage.py runserver

# 2. Open browser
http://127.0.0.1:8000/

# 3. Login as buyer → Buy any product

# 4. On checkout page, use:
Card: 4111 1111 1111 1111
Expiry: 12/25
CVV: 123

# 5. Click "Proceed to Payment" → Complete on gateway

# ✅ Done! See success page with DEMO badge
```

---

## 🧪 Sandbox Configuration (Already Set!)

```python
# settings.py - NO CHANGES NEEDED!
SSLCOMMERZ_STORE_ID = 'testbox'          # ✅ Default sandbox
SSLCOMMERZ_STORE_PASSWORD = 'qwerty'     # ✅ Default sandbox
SSLCOMMERZ_IS_SANDBOX = True             # ✅ Demo mode ON
```

---

## 💳 Test Cards (Copy & Paste)

### Main Test Card (Always Works):
```
Card Number: 4111 1111 1111 1111
Expiry Date: 12/25
CVV: 123
Name: Test User
```

### Alternative Test Cards:
```
Mastercard: 5555 5555 5555 4444
AMEX: 3782 822463 10005
```

---

## 📱 Mobile Banking Test

On gateway page:
- Select bKash/Nagad/Rocket
- Enter any test mobile: `01700000000`
- Click **"Success"** button → Payment succeeds ✅
- Click **"Fail"** button → Payment fails ❌

---

## 🎯 What Happens

### ✅ Successful Demo Payment:
```
Checkout → Enter test card → Submit
    ↓
Redirect to SSLCommerz sandbox gateway
    ↓
Gateway processes demo payment
    ↓
Redirect back to /payment/success/
    ↓
✓ See "Payment Successful!" with DEMO badge
✓ Stock reduced (demo)
✓ Purchase record created
✓ Console shows logs
```

### ❌ Failed Demo Payment:
```
Use invalid card OR click "Fail" button
    ↓
Redirect to /payment/fail/
    ↓
✗ See error with test card instructions
✗ Stock NOT reduced
✗ Payment NOT processed
```

---

## 🔍 How to Verify

### 1. Console Logs (Terminal):
```
=============================================================
Initiating payment for transaction: FT1A2B3C4D5E
✓ Payment initiation successful!
✓ Payment verified successfully!
Reducing stock: Product | Current: 10 | Ordered: 1
New stock level: 9
=============================================================
```

### 2. Success Page:
- Purple "SANDBOX MODE" badge at top
- Green success message
- Order details with transaction ID
- Blue info box: "This was a test transaction"

### 3. Database:
```python
# Django admin: http://127.0.0.1:8000/admin/
Purchase.payment_status = 'success'
Purchase.transaction_id = 'FT...'
Product.quantity reduced by order quantity
```

---

## 🎨 UI Updates (Already Done!)

### Checkout Page:
- 🟣 Purple "SANDBOX MODE" box with test credentials
- 💳 Test card number displayed: 4111 1111 1111 1111
- 📱 Mobile banking test instructions
- 🔒 "Currently in Sandbox Mode" notice

### Success Page:
- 🟣 "SANDBOX MODE - Test Payment Only" badge
- ✅ Animated success icon
- 💚 Green gradient order details card
- ℹ️ Demo info box explaining no real money charged

### Failed Page:
- 🟣 "SANDBOX MODE" badge
- ❌ Error message
- 💡 Test card credentials box (for retry)
- 📝 Common failure reasons

### Canceled Page:
- 🟣 "SANDBOX MODE" badge
- ⚠️ Cancelation notice
- ℹ️ "No charges made" message

---

## 🚀 URLs & Endpoints

### Your App URLs:
```
http://127.0.0.1:8000/checkout/1/         → Checkout page
http://127.0.0.1:8000/payment/initiate/1/ → Start payment
http://127.0.0.1:8000/payment/success/    → Success callback
http://127.0.0.1:8000/payment/fail/       → Fail callback
http://127.0.0.1:8000/payment/cancel/     → Cancel callback
```

### SSLCommerz Sandbox URLs:
```
https://sandbox.sslcommerz.com/gwprocess/v4/api.php
  → Payment initiation API

https://sandbox.sslcommerz.com/validator/api/validationserverAPI.php
  → Payment verification API

https://sandbox.sslcommerz.com/EasyCheckOut/...
  → Demo payment gateway page
```

---

## 🔐 Security Flow

```
1. Buyer clicks "Proceed to Payment"
   ↓
2. Backend creates Purchase (status='initiated')
   ↓
3. Backend calls SSLCommerz sandbox API
   ↓
4. Receives GatewayPageURL
   ↓
5. Redirect buyer to sandbox gateway
   ↓
6. Buyer enters test credentials
   ↓
7. Gateway processes demo payment
   ↓
8. Gateway redirects to /payment/success/
   ↓
9. Backend VERIFIES with validation API ⚠️ CRITICAL!
   ↓
10. If status=='VALID':
    ✓ Update payment_status='success'
    ✓ Reduce stock
    ✓ Update seller stats
    ✓ Show success page
```

**Key Point:** Backend ALWAYS verifies with SSLCommerz - never trusts redirect alone!

---

## 🧪 Test Scenarios

### ✅ Test 1: Successful Card Payment
```
Method: Card
Card: 4111 1111 1111 1111
Expiry: 12/25
CVV: 123
Expected: Success page, stock reduced
```

### ✅ Test 2: Successful bKash Payment
```
Method: bKash
On gateway: Click "Success" button
Expected: Success page, stock reduced
```

### ❌ Test 3: Failed Payment
```
Method: Card
On gateway: Click "Fail" button
Expected: Fail page, stock NOT reduced
```

### ⚠️ Test 4: Canceled Payment
```
Method: Any
On gateway: Click "Cancel" button
Expected: Cancel page, stock NOT reduced
```

### 🔒 Test 5: Invalid Card
```
Method: Card
Card: 1234 5678 9012 3456 (invalid)
Expected: Error on gateway or fail page
```

---

## 📊 Database Changes

### After Successful Payment:
```sql
-- Purchase table
payment_status: 'initiated' → 'success'
payment_completed_at: NULL → current timestamp
gateway_response: JSON response from SSLCommerz

-- Product table
quantity: 10 → 9 (reduced by order quantity)

-- SellerProfile table
total_sales: +1
total_revenue: +150.00
```

### After Failed Payment:
```sql
-- Purchase table
payment_status: 'initiated' → 'failed'
gateway_response: Error details

-- Product table
quantity: 10 (unchanged)

-- SellerProfile table
No changes
```

---

## 💡 Quick Tips

1. **Purple box = Sandbox info** - Look for it on checkout page
2. **4111 1111 1111 1111** - The magic test card that always works
3. **12/25 works** - Any future date is fine
4. **123 for CVV** - Any 3 digits work
5. **Watch terminal** - Shows detailed logs
6. **Success/Fail buttons** - In mobile banking on gateway
7. **DEMO badges** - Appear on all payment result pages
8. **No real money** - Everything is simulation

---

## 🎯 Current Status

```
✅ Sandbox Mode: ACTIVE
✅ Test Credentials: CONFIGURED
✅ Demo UI: UPDATED
✅ Gateway: CONNECTED
✅ Verification: WORKING
✅ Callbacks: CONFIGURED
✅ Logging: ENABLED
✅ Templates: DEMO BADGES ADDED

🚀 STATUS: READY TO TEST!
```

---

## 🎬 Complete Test Walkthrough

```
Step 1: Start Server
--------------------------------------
$ cd freshtrack-master
$ python manage.py runserver
→ Server running at http://127.0.0.1:8000/

Step 2: Open Browser & Login
--------------------------------------
→ Go to http://127.0.0.1:8000/
→ Click "Login"
→ Enter buyer credentials
→ Click "Login"

Step 3: Select Product
--------------------------------------
→ Browse products
→ Find product with stock > 0
→ Click "Buy Now"
→ Select quantity: 1
→ Click "Proceed to Checkout"

Step 4: Checkout Page
--------------------------------------
→ See purple "SANDBOX MODE" box
→ Note test card: 4111 1111 1111 1111
→ Select payment method: "Credit/Debit Card"
→ Click "🔒 Proceed to Payment"

Step 5: SSLCommerz Gateway (Demo)
--------------------------------------
→ Redirected to sandbox.sslcommerz.com
→ See demo payment form
→ Enter test card:
  • Card: 4111 1111 1111 1111
  • Expiry: 12/25
  • CVV: 123
  • Name: Test User
→ Click "Submit" or "Pay Now"

Step 6: Processing
--------------------------------------
→ Gateway processes demo payment
→ Shows "Processing..." animation
→ Redirects back to your app

Step 7: Success Page
--------------------------------------
→ See "Payment Successful!" with DEMO badge
→ Order details displayed
→ Transaction ID shown
→ "Test transaction" info box

Step 8: Verify Changes
--------------------------------------
→ Go to "Purchase History"
→ See completed order
→ Check product page
→ Stock reduced by 1

✅ TEST COMPLETE!
```

---

## 🐛 Troubleshooting Quick Fix

### "Failed to initiate payment"
```bash
# Check:
1. Internet connected?
2. Settings has store_id='testbox'?
3. Terminal shows error details?

# Fix:
→ Check console logs
→ Verify settings.py configuration
→ Try restarting server
```

### Gateway page blank/not loading
```bash
# Check:
1. Browser blocks pop-ups/redirects?
2. Firewall blocks sandbox.sslcommerz.com?
3. HTTPS connection allowed?

# Fix:
→ Allow redirects in browser
→ Try different browser
→ Check firewall settings
```

### Success page but stock not reduced
```bash
# Check:
1. Terminal shows "Reducing stock"?
2. Purchase.payment_status is 'success'?
3. Verification completed?

# Fix:
→ Check payment_success view logs
→ Verify validation API response
→ Check database Purchase record
```

---

## 📞 Need Help?

**Check Terminal First!**
All errors are logged with details:
```
✓ Success messages start with checkmark
✗ Error messages start with X
⚠ Warning messages start with warning sign
```

**Files to Check:**
- `SANDBOX_DEMO_GUIDE.md` - Complete guide
- `README_PAYMENT.md` - Quick start
- `PAYMENT_SETUP.md` - Detailed setup
- Terminal console logs - Real-time debugging

---

## 🎉 Summary

```
Your FreshTrack payment system is configured for sandbox demo testing!

✅ Configuration: testbox / qwerty
✅ Test Card: 4111 1111 1111 1111
✅ Demo UI: Purple badges + test credentials
✅ Verification: Automatic with SSLCommerz
✅ Security: Full verification flow
✅ Logging: Detailed console output

Just run the server and test!
NO real money will be charged!
Everything is demo/simulation!

🚀 You're ready to test!
```

---

**Last Updated:** November 29, 2025
**Mode:** 🧪 Sandbox/Demo Only
**Real Money:** ❌ NO
**Status:** ✅ Ready to Test
