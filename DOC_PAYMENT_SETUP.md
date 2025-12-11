# Payment System Setup Guide - FreshTrack

## Overview
FreshTrack uses **SSLCommerz** as the payment gateway for processing payments in Bangladesh. This guide explains how to set up and test the payment system.

---

## 🔧 Configuration

### 1. Environment Variables

Copy `.env.example` to `.env` and configure your SSLCommerz credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```env
# For Testing (Sandbox)
SSLCOMMERZ_STORE_ID=testbox
SSLCOMMERZ_STORE_PASSWORD=qwerty
SSLCOMMERZ_IS_SANDBOX=True

# For Production
# SSLCOMMERZ_STORE_ID=your_live_store_id
# SSLCOMMERZ_STORE_PASSWORD=your_live_store_password
# SSLCOMMERZ_IS_SANDBOX=False
```

### 2. Get SSLCommerz Credentials

**For Sandbox Testing:**
- Store ID: `testbox`
- Store Password: `qwerty`
- These are default credentials provided by SSLCommerz for testing

**For Production:**
1. Register at: https://developer.sslcommerz.com/registration/
2. Complete KYC verification
3. Get your live Store ID and Password
4. Update `.env` with live credentials
5. Set `SSLCOMMERZ_IS_SANDBOX=False`

---

## 📋 Payment Flow

### Step 1: Buyer Checkout
1. Buyer browses products and clicks "Buy Now"
2. Buyer selects quantity and proceeds to checkout
3. Buyer selects payment method:
   - Credit/Debit Card
   - bKash
   - Nagad
   - Rocket
   - CellFin

### Step 2: Payment Initiation
1. Backend creates `Purchase` record with status `initiated`
2. Backend calls SSLCommerz API with:
   - Amount
   - Transaction ID (unique: `FT{uuid}`)
   - Customer info
   - Callback URLs (success/fail/cancel/ipn)
3. SSLCommerz returns `GatewayPageURL`
4. Buyer is redirected to SSLCommerz payment page

### Step 3: Payment Processing
1. Buyer enters payment details on SSLCommerz page
2. SSLCommerz processes the payment
3. SSLCommerz redirects to appropriate callback URL:
   - `/payment/success/` - Payment successful
   - `/payment/fail/` - Payment failed
   - `/payment/cancel/` - Payment canceled

### Step 4: Payment Verification
**CRITICAL: Never trust redirect alone - always verify!**

1. Backend receives callback with `tran_id` and `val_id`
2. Backend calls SSLCommerz Validation API
3. If validation status is `VALID` or `VALIDATED`:
   - Update purchase status to `success`
   - Reduce product stock
   - Update seller stats
   - Show success page
4. If validation fails:
   - Update status to `failed`
   - Show error message

---

## 🧪 Testing

### Test in Sandbox Mode

1. Make sure `SSLCOMMERZ_IS_SANDBOX=True` in `.env`

2. Use test credentials:
   ```
   Store ID: testbox
   Store Password: qwerty
   ```

3. Test credit card numbers (provided by SSLCommerz):
   ```
   Card Number: 4111111111111111
   Expiry: Any future date (e.g., 12/25)
   CVV: Any 3 digits (e.g., 123)
   Name: Test User
   ```

4. Test mobile banking:
   - Select bKash/Nagad/Rocket
   - Use dummy numbers provided on gateway page
   - Complete mock payment flow

5. Monitor console logs for debugging:
   ```python
   # Logs show:
   # - Payment initiation
   # - SSLCommerz API response
   # - Gateway URL
   # - Callback data
   # - Verification result
   # - Stock updates
   ```

### Expected Sandbox Behavior

✅ **Success Flow:**
```
1. Click "Proceed to Payment"
2. Redirect to SSLCommerz sandbox page
3. Enter test card details
4. Click "Submit"
5. Redirect to /payment/success/
6. See confirmation message
7. Stock reduced
8. Purchase visible in buyer history
```

❌ **Failure Flow:**
```
1. Click "Proceed to Payment"
2. Redirect to SSLCommerz sandbox page
3. Click "Fail" button (sandbox feature)
4. Redirect to /payment/fail/
5. See error message
6. Stock NOT reduced
```

---

## 🛠️ Troubleshooting

### Error: "Failed to initiate payment"

**Causes:**
1. Invalid Store ID or Password
2. SSLCommerz API is down
3. Network/firewall issues
4. Invalid callback URLs

**Solutions:**
1. Check `.env` credentials
2. Verify `SSLCOMMERZ_IS_SANDBOX` is `True` for testing
3. Check console logs for detailed error
4. Ensure your server is accessible (use ngrok for local testing)

### Error: "Payment verification failed"

**Causes:**
1. Invalid `val_id` from gateway
2. Validation API timeout
3. Transaction already processed

**Solutions:**
1. Check gateway response in console logs
2. Verify validation URL is correct
3. Check `Purchase` model `gateway_response` field

### Stock not reduced after payment

**Causes:**
1. Payment verification failed
2. Product deleted before processing
3. Database error

**Solutions:**
1. Check purchase `payment_status` in admin
2. Look for errors in console logs
3. Verify `payment_success` callback was called

---

## 🔒 Security Best Practices

### 1. Never Trust Client-Side Success
```python
# ❌ WRONG - Never do this
if request.GET.get('payment_status') == 'success':
    # Process payment

# ✅ CORRECT - Always verify with gateway
validation_response = requests.get(VALIDATION_URL, params={...})
if validation_response.json().get('status') == 'VALID':
    # Process payment
```

### 2. Use HTTPS in Production
```python
# In production:
# - Use HTTPS for callback URLs
# - Enable SSL certificate
# - Set SECURE_SSL_REDIRECT = True in settings.py
```

### 3. Validate Transaction IDs
```python
# Ensure transaction_id is unique
transaction_id = f"FT{uuid.uuid4().hex[:12].upper()}"
```

### 4. Log Gateway Responses
```python
# Save gateway response for debugging
purchase.gateway_response = json.dumps(response_data)
purchase.save()
```

### 5. Handle Duplicate Callbacks
```python
# Check if already processed
if purchase.payment_status == 'success':
    return  # Already processed, skip
```

---

## 📊 Database Fields

### Purchase Model Fields:
- `payment_status`: initiated → success/failed/canceled
- `payment_method`: card/bkash/nagad/rocket/cellfin
- `transaction_id`: Unique transaction identifier
- `gateway_response`: JSON response from SSLCommerz
- `purchased_at`: Order creation timestamp
- `payment_completed_at`: Payment completion timestamp

---

## 🌐 Callback URLs

All callback URLs must be publicly accessible:

- **Success URL:** `https://yourdomain.com/payment/success/`
- **Fail URL:** `https://yourdomain.com/payment/fail/`
- **Cancel URL:** `https://yourdomain.com/payment/cancel/`
- **IPN URL:** `https://yourdomain.com/payment/ipn/`

**For Local Testing:**
Use ngrok to expose local server:
```bash
ngrok http 8000
```
Then update callback URLs with ngrok URL.

---

## 🚀 Going to Production

### Checklist:

1. ✅ Get live SSLCommerz credentials
2. ✅ Update `.env` with live credentials
3. ✅ Set `SSLCOMMERZ_IS_SANDBOX=False`
4. ✅ Enable HTTPS on your domain
5. ✅ Update callback URLs to production domain
6. ✅ Test with small real transaction
7. ✅ Set up error monitoring (Sentry/etc)
8. ✅ Configure email notifications
9. ✅ Set up backup/recovery procedures
10. ✅ Monitor transaction logs regularly

---

## 📞 Support

- **SSLCommerz Support:** support@sslcommerz.com
- **Developer Portal:** https://developer.sslcommerz.com/
- **FreshTrack Issues:** Check console logs and Purchase.gateway_response field

---

## 💡 Tips

1. **Always test in sandbox before going live**
2. **Keep transaction logs for at least 1 year**
3. **Set up automated alerts for failed payments**
4. **Monitor gateway response times**
5. **Have a manual verification process as backup**
6. **Keep credentials secure - never commit to git**
7. **Use environment variables for all sensitive data**
8. **Implement retry logic for network failures**
9. **Set up proper error tracking (Sentry)**
10. **Regularly reconcile payments with SSLCommerz reports**

---

**Last Updated:** November 29, 2025
