# Quick Payment Testing Guide

## ⚡ Quick Start

### 1. Default Test Credentials (Already Configured)
```
Store ID: testbox
Password: qwerty
Mode: Sandbox
```
These are already set in `settings.py` - you can start testing immediately!

### 2. Start Server
```bash
cd freshtrack-master
python manage.py runserver
```

### 3. Test Payment Flow

**Login as Buyer:**
1. Navigate to http://127.0.0.1:8000/
2. Login with buyer account
3. Browse products and click "Buy Now"
4. Select quantity
5. Click "Proceed to Checkout"

**Complete Payment:**
1. Select payment method (Card/bKash/Nagad/Rocket/CellFin)
2. Click "Proceed to Payment"
3. You'll be redirected to SSLCommerz sandbox page
4. Use test card: `4111 1111 1111 1111` (Visa)
5. Expiry: Any future date (e.g., 12/25)
6. CVV: 123
7. Click "Submit"

**Expected Result:**
- ✅ Redirected to success page
- ✅ Order confirmed message
- ✅ Product stock reduced
- ✅ Purchase visible in buyer history

---

## 🧪 Test Scenarios

### ✅ Successful Payment
```
Card: 4111 1111 1111 1111
Expiry: 12/25
CVV: 123
Result: Payment Success ✓
```

### ❌ Failed Payment
On sandbox gateway page, click "Fail" button
```
Result: Payment Failed ✗
Stock: Not reduced
```

### ⛔ Canceled Payment
On sandbox gateway page, click "Cancel" button
```
Result: Payment Canceled
Stock: Not reduced
```

---

## 📊 Check Payment Status

### In Django Admin:
1. Go to http://127.0.0.1:8000/admin/
2. Navigate to "Purchases"
3. Check `payment_status` field:
   - `initiated` - Payment started
   - `success` - Payment completed ✓
   - `failed` - Payment failed ✗
   - `canceled` - Payment canceled

### In Console Logs:
Watch terminal output for detailed logs:
```
=============================================================
Initiating payment for transaction: FT...
Amount: ৳100.00 | Method: card
=============================================================

✓ Payment initiation successful!
✓ Payment verified successfully!
Updated purchase status to: success
Reducing stock: Product Name | Current: 10 | Ordered: 1
New stock level: 9
✓ Updated seller stats: Company Name
```

---

## 🔍 Debugging Checklist

### If "Failed to initiate payment" error:

1. **Check credentials:**
   ```bash
   # In settings.py, verify:
   SSLCOMMERZ_STORE_ID = 'testbox'
   SSLCOMMERZ_STORE_PASSWORD = 'qwerty'
   SSLCOMMERZ_IS_SANDBOX = True
   ```

2. **Check internet connection:**
   - SSLCommerz API requires internet access
   - Test: `ping sandbox.sslcommerz.com`

3. **Check console logs:**
   - Look for detailed error messages in terminal
   - Check "SSLCommerz Response Status Code"
   - Check "Failed Reason" message

4. **Common issues:**
   - ❌ Store ID/Password mismatch
   - ❌ SSLCommerz API down
   - ❌ Network/firewall blocking
   - ❌ Invalid callback URLs

### If payment succeeds but stock not reduced:

1. Check `payment_status` in database
2. Look for errors in verification step
3. Check if product was deleted
4. Verify callback URL was called

---

## 🎯 What Each File Does

### Views (`views.py`):
- `checkout()` - Display checkout page
- `initiate_payment()` - Create order & call SSLCommerz API
- `payment_success()` - Verify payment & update stock
- `payment_fail()` - Handle failed payments
- `payment_cancel()` - Handle canceled payments
- `payment_ipn()` - Handle instant notifications

### Template (`checkout.html`):
- Payment method selection
- Form validation
- Submit to `initiate_payment`

### Settings (`settings.py`):
- SSLCommerz credentials
- API URLs (sandbox/production)

### URLs (`urls.py`):
- `/checkout/<id>/` - Checkout page
- `/payment/initiate/<id>/` - Start payment
- `/payment/success/` - Payment success callback
- `/payment/fail/` - Payment fail callback
- `/payment/cancel/` - Payment cancel callback
- `/payment/ipn/` - IPN callback

---

## 🚀 Next Steps

### For Local Testing:
✓ Use default credentials (`testbox` / `qwerty`)
✓ Test with sandbox card numbers
✓ Monitor console logs

### For Production:
1. Register at https://developer.sslcommerz.com/registration/
2. Get live Store ID & Password
3. Update `.env` file:
   ```env
   SSLCOMMERZ_STORE_ID=your_live_store_id
   SSLCOMMERZ_STORE_PASSWORD=your_live_password
   SSLCOMMERZ_IS_SANDBOX=False
   ```
4. Enable HTTPS
5. Update callback URLs
6. Test with real payment

---

## 📞 Need Help?

**Console shows errors:**
- Read the error message carefully
- Check credentials in settings.py
- Verify internet connection

**Payment succeeds but no confirmation:**
- Check browser console for errors
- Verify callback URLs are accessible
- Check database for purchase record

**Stock not reducing:**
- Check payment_status is 'success'
- Look for verification errors in logs
- Check product quantity field

---

**Pro Tip:** Keep terminal window visible while testing to see real-time logs!

```bash
# Example successful log output:
=============================================================
Initiating payment for transaction: FT1A2B3C4D5E
Amount: ৳150.00 | Method: bkash
=============================================================
✓ Payment initiation successful! Redirecting to gateway
✓ Payment verified successfully!
Reducing stock: Fresh Banana | Current: 50 | Ordered: 2
New stock level: 48
✓ Updated seller stats: Fresh Fruits Ltd
```
