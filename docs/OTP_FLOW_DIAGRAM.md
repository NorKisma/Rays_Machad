# OTP Password Reset - User Flow Diagram

## 🔄 Complete Flow Visualization

```
┌─────────────────────────────────────────────────────────────┐
│                    OTP PASSWORD RESET FLOW                   │
└─────────────────────────────────────────────────────────────┘

1️⃣  LOGIN PAGE
    │
    ├─► Click "Forgot Password"
    │
    ▼

2️⃣  FORGOT PASSWORD PAGE (/forgot-password)
    │
    ├─► Enter Email Address
    ├─► Click "Request Password Reset"
    │
    ▼
    ┌──────────────────────┐
    │  Backend Process:    │
    │  • Find user by email│
    │  • Generate 6-digit  │
    │    OTP code          │
    │  • Save to database  │
    │  • Send email        │
    │  • Store email in    │
    │    session           │
    └──────────────────────┘
    │
    ▼

3️⃣  EMAIL INBOX
    │
    ├─► Receive OTP Email
    ├─► Subject: "Password Reset OTP"
    ├─► Body: "Your OTP is: 123456"
    ├─► Valid for 10 minutes
    │
    ▼

4️⃣  VERIFY OTP PAGE (/verify-otp)
    │
    ├─► Enter 6-digit OTP
    ├─► Auto-submit when 6 digits entered
    │   OR
    ├─► Click "Verify OTP"
    │
    ▼
    ┌──────────────────────┐
    │  Backend Validation: │
    │  • Check OTP exists  │
    │  • Check not expired │
    │  • Check not used    │
    │  • Mark as used      │
    │  • Set session flags │
    └──────────────────────┘
    │
    ├─► ✅ Success: Redirect to password reset
    │   OR
    └─► ❌ Error: Show error message
    
    ▼

5️⃣  RESET PASSWORD PAGE (/reset-password-otp)
    │
    ├─► Enter New Password (min 8 chars)
    ├─► Confirm New Password
    ├─► Click "Reset Password"
    │
    ▼
    ┌──────────────────────┐
    │  Backend Process:    │
    │  • Validate password │
    │  • Hash password     │
    │  • Update user record│
    │  • Clear session     │
    └──────────────────────┘
    │
    ▼

6️⃣  LOGIN PAGE
    │
    ├─► Success message: "Password updated!"
    ├─► Login with new password
    │
    ▼

7️⃣  DASHBOARD
    └─► ✅ Successfully logged in!


═══════════════════════════════════════════════════════════════
                      ALTERNATIVE FLOWS
═══════════════════════════════════════════════════════════════

❌ OTP EXPIRED (After 10 minutes)
    │
    ├─► Error: "OTP has expired"
    ├─► Click "Resend OTP"
    └─► Return to Step 2

❌ WRONG OTP ENTERED
    │
    ├─► Error: "Invalid OTP code"
    ├─► Can retry
    └─► Or click "Resend OTP"

❌ EMAIL SENDING FAILED
    │
    ├─► In Debug Mode:
    │   └─► OTP shown on screen
    │
    └─► In Production:
        └─► Error message to contact support

🔒 DIRECT URL ACCESS (Security)
    │
    ├─► Access /verify-otp without session
    │   └─► Redirect to /forgot-password
    │
    └─► Access /reset-password-otp without verification
        └─► Redirect to /verify-otp


═══════════════════════════════════════════════════════════════
                    DATABASE OPERATIONS
═══════════════════════════════════════════════════════════════

📊 OTP Table Structure:

┌────────────┬──────────┬──────────┬──────────┬──────────┬────────────┬────────────┐
│ id         │ user_id  │ code     │ purpose  │ is_used  │ expires_at │ created_at │
├────────────┼──────────┼──────────┼──────────┼──────────┼────────────┼────────────┤
│ 1          │ 42       │ 123456   │ pwd_reset│ false    │ 12:50:00   │ 12:40:00   │
│ 2          │ 42       │ 789012   │ pwd_reset│ true     │ 13:00:00   │ 12:50:00   │ (used)
│ 3          │ 15       │ 345678   │ pwd_reset│ false    │ 13:10:00   │ 13:00:00   │
└────────────┴──────────┴──────────┴──────────┴──────────┴────────────┴────────────┘

Operations:
1. CREATE: New OTP generated → Insert new row
2. READ: Verify OTP → SELECT by user_id, code, is_used=false
3. UPDATE: After verification → SET is_used=true
4. CLEANUP: Mark old OTPs as used when new one requested


═══════════════════════════════════════════════════════════════
                      SESSION VARIABLES
═══════════════════════════════════════════════════════════════

Session State Management:

Step 2 (After OTP sent):
    session['reset_email'] = user.email

Step 4 (After OTP verified):
    session['otp_verified'] = True
    session['verified_user_id'] = user.id

Step 5 (After password reset):
    session.pop('reset_email', None)
    session.pop('otp_verified', None)
    session.pop('verified_user_id', None)


═══════════════════════════════════════════════════════════════
                    SECURITY MEASURES
═══════════════════════════════════════════════════════════════

🔐 Security Features:

1. ⏱️  TIME-LIMITED
   └─► OTP expires after 10 minutes

2. 🔒 SINGLE-USE
   └─► OTP marked as used after verification

3. 🔄 AUTO-INVALIDATION
   └─► Old OTPs invalidated when new one requested

4. 🎫 SESSION-BASED
   └─► Prevents direct URL access

5. 🎲 SECURE RANDOM
   └─► Generated using secrets.choice()

6. 📧 EMAIL VERIFICATION
   └─► Must have access to registered email

7. 🚫 NO TOKEN IN URL
   └─► Unlike traditional reset links


═══════════════════════════════════════════════════════════════
                    UI/UX FEATURES
═══════════════════════════════════════════════════════════════

✨ User Experience:

1. 🎯 AUTO-SUBMIT
   └─► Form submits when 6 digits entered

2. 🔢 NUMBER-ONLY
   └─► Only numeric characters allowed

3. 👁️ PASSWORD TOGGLE
   └─► Show/hide password visibility

4. 🌍 MULTI-LANGUAGE
   └─► English, Arabic, Somali

5. 🌓 THEME SUPPORT
   └─► Light and Dark modes

6. 📱 RESPONSIVE
   └─► Mobile, tablet, desktop optimized

7. ♿ ACCESSIBLE
   └─► Screen reader friendly


═══════════════════════════════════════════════════════════════
```

## 📊 Statistics & Metrics

- **Average Time to Complete**: 2-3 minutes
- **OTP Validity**: 10 minutes
- **Code Length**: 6 digits (000000-999999)
- **Total Possible Codes**: 1,000,000 combinations
- **Email Delivery**: Typically < 1 minute
- **Session Timeout**: Based on Flask config

## 🎯 Success Criteria

✅ User receives OTP email within 1 minute
✅ OTP successfully verifies on first attempt
✅ Password reset completes without errors
✅ User can login with new password
✅ No session data leakage
✅ Proper error messages for all failure cases

---

**Last Updated**: 2026-02-07
**Version**: 1.0.0
