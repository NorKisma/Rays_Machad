# OTP-Based Password Reset Feature

## Overview
The Madrasah Management System now supports **OTP (One-Time Password)** based password reset functionality. Users can securely reset their passwords by receiving a 6-digit code via email.

## How It Works

### 1. User Requests Password Reset
- User navigates to the "Forgot Password" page
- User enters their email address
- System generates a 6-digit OTP code and sends it to the user's email
- OTP is valid for **10 minutes**

### 2. OTP Verification
- User is redirected to the OTP verification page
- User enters the 6-digit code received via email
- The form auto-submits when 6 digits are entered
- System validates the OTP:
  - Checks if OTP exists and matches
  - Checks if OTP hasn't expired
  - Checks if OTP hasn't been used already

### 3. Password Reset
- After successful OTP verification, user is redirected to set a new password
- User enters and confirms their new password
- Password must be at least 8 characters long
- System updates the password and clears the OTP session

## Features

### Security Features
✅ **Time-Limited OTPs**: Each OTP expires after 10 minutes
✅ **Single-Use OTPs**: Once verified, an OTP cannot be reused
✅ **Session-Based Flow**: Uses secure session storage to maintain state
✅ **Automatic Invalidation**: Previous OTPs are invalidated when a new one is requested

### User Experience Features
✅ **Auto-Submit**: OTP form automatically submits when 6 digits are entered
✅ **Number-Only Input**: OTP field only accepts numeric characters
✅ **Visual Feedback**: Clear success/error messages at each step
✅ **Resend Option**: Users can request a new OTP if needed
✅ **Debug Mode**: In development, OTP is displayed on screen if email fails

### Accessibility Features
✅ **Multi-Language Support**: Works with English, Arabic, and Somali
✅ **RTL Support**: Proper right-to-left display for Arabic
✅ **Theme Support**: Works with both light and dark themes
✅ **Mobile Responsive**: Optimized for all screen sizes

## File Structure

### Backend Files
```
app/models/otp.py                          # OTP model with generation and verification logic
app/blueprints/auth/routes.py              # Updated routes for OTP flow
app/blueprints/auth/forms.py               # OTP verification forms
migrations/versions/902c2146adec_*.py      # Database migration for OTP table
```

### Frontend Files
```
app/blueprints/auth/templates/
├── forgot_password.html                   # Initial password reset request
├── verify_otp.html                        # OTP verification page
└── reset_password_otp.html                # New password setup page
```

## API Endpoints

### 1. Request Password Reset
**Route**: `/forgot-password`
**Method**: GET, POST
**Description**: Generates and sends OTP to user's email

### 2. Verify OTP
**Route**: `/verify-otp`
**Method**: GET, POST
**Description**: Validates the OTP code entered by user
**Session Required**: `reset_email`

### 3. Reset Password with OTP
**Route**: `/reset-password-otp`
**Method**: GET, POST
**Description**: Allows user to set new password after OTP verification
**Session Required**: `otp_verified`, `verified_user_id`

## Database Schema

### OTP Table
```sql
CREATE TABLE otps (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER NOT NULL,
    code VARCHAR(6) NOT NULL,
    purpose VARCHAR(50) NOT NULL DEFAULT 'password_reset',
    is_used BOOLEAN DEFAULT FALSE,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
```

## Email Configuration

The OTP is sent via email using Flask-Mail. Make sure your `.env` file has the following configuration:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

### Gmail Users
If using Gmail, you need to:
1. Enable 2-Factor Authentication
2. Generate an App-Specific Password
3. Use the app password in `MAIL_PASSWORD`

## Testing

### Development Mode
When `FLASK_ENV=development` and email sending fails:
- OTP is displayed on screen as a flash message
- User can still complete the password reset flow
- Useful for testing without email configuration

### Manual Testing Checklist
- [ ] Request password reset with valid email
- [ ] Verify OTP email is received
- [ ] Enter correct OTP code
- [ ] Verify redirect to password reset page
- [ ] Set new password
- [ ] Login with new password
- [ ] Test with expired OTP (wait 10 minutes)
- [ ] Test with invalid OTP
- [ ] Test with already-used OTP
- [ ] Test resend OTP functionality

## Error Handling

### Common Error Messages
- **"Invalid OTP code"**: OTP doesn't match or doesn't exist
- **"OTP has expired"**: More than 10 minutes have passed
- **"Please request a password reset first"**: Direct access to verify-otp without session
- **"Please verify your OTP first"**: Direct access to reset-password-otp without verification

### Error Scenarios Handled
1. Email sending failure (with debug fallback)
2. Invalid/expired OTP
3. Session hijacking attempts
4. Direct URL access without proper flow
5. Reuse of already-verified OTP

## Future Enhancements

### Potential Improvements
- [ ] SMS OTP support
- [ ] Rate limiting on OTP requests
- [ ] Account lockout after multiple failed attempts
- [ ] OTP length customization
- [ ] Different OTP purposes (login verification, account activation)
- [ ] Email templates with better formatting
- [ ] Logging of OTP attempts for security audit

## Troubleshooting

### OTP Not Received
1. Check spam/junk folder
2. Verify email configuration in `.env`
3. Check server logs for email errors
4. Test with debug mode enabled

### OTP Verification Fails
1. Ensure OTP hasn't expired (10-minute window)
2. Check for typos in OTP entry
3. Verify database connection
4. Check server time synchronization

### Session Issues
1. Ensure browser cookies are enabled
2. Check Flask SECRET_KEY is set
3. Verify session configuration

## Security Considerations

### Best Practices Implemented
✅ OTPs are randomly generated using `secrets` module
✅ OTPs expire after 10 minutes
✅ Used OTPs are marked and cannot be reused
✅ Session data is cleared after password reset
✅ Previous OTPs are invalidated when new one is requested

### Security Recommendations
- Keep `SECRET_KEY` secure and random
- Use HTTPS in production
- Monitor failed OTP attempts
- Implement rate limiting
- Consider adding CAPTCHA for multiple failures
- Regular security audits

## Support

For issues or questions:
- Check the error logs in `/var/www/RaysTech/madrasah_mgmt/`
- Review Flask application logs
- Contact system administrator

---

**Version**: 1.0.0
**Last Updated**: 2026-02-07
**Author**: Madrasah Management System Team
