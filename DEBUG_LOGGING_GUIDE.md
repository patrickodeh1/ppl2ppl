## Production Logging Configuration

### Current Setup (Production)

**Log Levels:**
- ✅ `INFO` - Normal operations (registrations, logins, emails sent)
- ✅ `WARNING` - Unexpected but handled (unverified email login attempts)
- ✅ `ERROR` - Failures (email errors, exceptions)
- ❌ `DEBUG` - Disabled (database queries, detailed traces)

**What You See:**
```
[INFO] 2026-01-03 17:01:03 authentication New user registered: user@example.com
[INFO] 2026-01-03 17:01:04 authentication Verification email sent to user@example.com
[WARNING] 2026-01-03 17:01:10 authentication Login attempt with unverified email: user@example.com
[ERROR] 2026-01-03 17:02:00 authentication FAILED to send verification email to user@example.com: SMTPAuthenticationError: (535, b'5.7.8 Incorrect authentication')
```

**What You DON'T See:**
```
[DEBUG] 2026-01-03 17:01:03 django.db.backends SELECT "authentication_customuser"."id"...  (200+ lines hidden)
```

---

## Enable Debug Logging (When Investigating Errors)

If you get a 500 error and need to debug, temporarily enable DEBUG logging:

### Option 1: Environment Variable (Railway)
1. Go to Railway Dashboard
2. Select your service
3. Go to "Variables"
4. Add: `DEBUG_LOGS=true`
5. Redeploy

Then the app will log database queries too.

### Option 2: Direct Code Change
Edit `ppl/settings.py` line 336 temporarily:
```python
'django.db.backends': {
    'handlers': ['console', 'file'],  # Change from [] to ['console', 'file']
    'level': 'DEBUG',                  # Change from ERROR to DEBUG
    'propagate': False,
},
```

Commit and push, then revert after debugging.

### What DEBUG Logs Show:
```
[DEBUG] 2026-01-03 17:01:03 django.db.backends (0.002) SELECT "authentication_customuser"."id", "authentication_customuser"."email"... FROM "authentication_customuser" WHERE "authentication_customuser"."email" = 'user@example.com'
```

This helps you see:
- ✓ All database queries
- ✓ Query execution time
- ✓ Full stack traces
- ✓ Variable values

---

## Log Levels Reference

| Level | Use Case | Show in Production? |
|-------|----------|-------------------|
| DEBUG | Database queries, detailed traces | ❌ No (too verbose) |
| INFO | User actions, successful operations | ✅ Yes |
| WARNING | Potential issues that are handled | ✅ Yes |
| ERROR | Failures and exceptions | ✅ Yes |
| CRITICAL | System failures | ✅ Yes |

---

## How to Interpret Logs

### INFO - Normal Operations (Green ✅)
```
[INFO] 2026-01-03 17:01:03 authentication New user registered: user@example.com
```
Everything working as expected.

### WARNING - Suspicious Activity (Yellow ⚠️)
```
[WARNING] 2026-01-03 17:01:10 authentication Login attempt with unverified email: user@example.com
```
User tried to login but hasn't verified email. Expected behavior - redirected to verification page.

### ERROR - Something Failed (Red ❌)
```
[ERROR] 2026-01-03 17:02:00 authentication FAILED to send verification email to user@example.com: SMTPAuthenticationError: (535, b'5.7.8 Incorrect authentication')
```
Action to take:
1. Note the error type: `SMTPAuthenticationError`
2. Note the detail: `Incorrect authentication` (wrong email credentials)
3. Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in Railway

---

## Example: Debugging Email Not Sending

**Logs you see (Production):**
```
[INFO] 2026-01-03 17:01:03 authentication New user registered: test@example.com
[ERROR] 2026-01-03 17:01:04 authentication FAILED to send verification email to test@example.com: SMTPAuthenticationError: (535, b'5.7.8 Incorrect authentication')
```

**Problem identified:** SMTP authentication error (wrong credentials)

**Solution:** 
1. Enable DEBUG logging
2. Deploy again
3. Try registering
4. Check logs for full error details
5. Fix the issue (check email credentials in Railway environment variables)
6. Disable DEBUG logging
7. Redeploy

---

## Log File Location

**Production (Railway):**
- Console logs: Visible in Railway Dashboard → Logs tab
- File logs: Stored in container but ephemeral (lost on restart)

**Local Development:**
- All logs: `logs/django.log`
- Console: Terminal output

---

## TL;DR

- Production only shows INFO/WARNING/ERROR (clean)
- Database queries hidden unless you enable DEBUG
- When you see ERROR, enable DEBUG to investigate
- Most errors will have hints in the ERROR message itself

Current production is perfect for normal operations! 🚀
