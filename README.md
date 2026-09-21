# Casaio-Website
Django Dropshipping Website

## Razorpay Live Payments

The payment integration defaults to live mode and reads credentials from environment variables. Never commit Razorpay credentials to the repository.

PowerShell setup for the local server:

```powershell
$env:RAZORPAY_MODE = "live"
$env:RAZORPAY_KEY_ID = "rzp_live_your_key_id"
$env:RAZORPAY_KEY_SECRET = "your_live_key_secret"
python manage.py runserver
```

Use the live Key ID and Secret from the Razorpay Dashboard. The application rejects test keys when `RAZORPAY_MODE` is `live`. The previously exposed Razorpay secret must be revoked and regenerated before accepting real payments.
