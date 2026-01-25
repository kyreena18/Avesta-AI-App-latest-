# Authentication Troubleshooting Guide

## Issue: Credentials Not Getting Saved / No Validation

If registration and login are not working, follow these steps:

### Step 1: Verify Supabase Connection

Run the test script to check if your Supabase connection is working:

```bash
python test_supabase_auth.py
```

This will:
- Check if your `.env` file has correct credentials
- Test user registration
- Test user login
- Show any errors

### Step 2: Check Your .env File

Make sure your `.env` file contains:

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
```

**Where to find these:**
1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Select your project
3. Go to Settings → API
4. Copy the "Project URL" → `SUPABASE_URL`
5. Copy the "anon public" key → `SUPABASE_KEY`

### Step 3: Check Email Confirmation Settings

Supabase may require email confirmation by default. This means:
- Users can register, but won't get a session immediately
- They need to click a confirmation link in their email
- Only then can they log in

**To disable email confirmation (for testing):**
1. Go to Supabase Dashboard → Authentication → Settings
2. Find "Enable email confirmations"
3. Toggle it OFF
4. Save changes

**To keep email confirmation enabled:**
- Users will receive a confirmation email after registration
- They must click the link before logging in
- Check spam folder if email doesn't arrive

### Step 4: Check Supabase Auth Status

1. Go to Supabase Dashboard → Authentication → Users
2. Try registering a user through your app
3. Check if the user appears in the Users list
4. If user appears but can't login, check:
   - Email confirmation status (should be "Confirmed" or "Unconfirmed")
   - User metadata

### Step 5: Check Application Logs

When running your Flask app, check the console output for:
- Registration attempts
- Login attempts
- Any error messages

The app now includes logging that shows:
- When registration/login is attempted
- What the result is
- Any errors that occur

### Step 6: Common Issues and Solutions

#### Issue: "Registration failed: [error message]"

**Possible causes:**
1. **Invalid credentials** - Check your `.env` file
2. **Email already exists** - Try a different email
3. **Password too weak** - Use at least 6 characters
4. **Network issues** - Check internet connection
5. **Supabase project paused** - Check Supabase dashboard

**Solution:**
- Run `test_supabase_auth.py` to see detailed error
- Check Supabase Dashboard → Project Settings → Status

#### Issue: "Login failed: Invalid credentials"

**Possible causes:**
1. **Wrong email/password** - Double-check credentials
2. **Email not confirmed** - Check email for confirmation link
3. **User doesn't exist** - Register first
4. **Password changed** - Reset password if needed

**Solution:**
- Try registering again with a new email
- Check if email confirmation is required
- Verify user exists in Supabase Dashboard → Authentication → Users

#### Issue: "Session not available"

**Possible causes:**
1. **Email confirmation required** - User hasn't confirmed email
2. **Session expired** - Try logging in again
3. **Supabase Auth misconfigured** - Check Supabase settings

**Solution:**
- Disable email confirmation for testing (see Step 3)
- Or ensure users confirm their email before logging in

### Step 7: Verify Database Tables

Make sure you've run the SQL schema in Supabase:

1. Go to Supabase Dashboard → SQL Editor
2. Copy and paste the contents of `COPY_TO_SUPABASE_SQL_EDITOR.sql`
3. Click "Run" to execute
4. Verify tables are created:
   - `users` (optional, for profile data)
   - `jobs`
   - `shortlists`
   - `notes`
   - `interviews`

**Note:** The `auth.users` table is created automatically by Supabase - you don't need to create it manually.

### Step 8: Test the Full Flow

1. **Start your Flask app:**
   ```bash
   python platform_app_supabase.py
   ```

2. **Open browser:** http://localhost:5000

3. **Try to register:**
   - Go to `/register`
   - Enter email, password, name
   - Submit form
   - Check for success/error message

4. **Check Supabase Dashboard:**
   - Go to Authentication → Users
   - See if new user appears

5. **Try to login:**
   - Go to `/login`
   - Enter same email/password
   - Submit form
   - Should redirect to dashboard if successful

### Still Having Issues?

1. **Check Supabase Status:**
   - Visit https://status.supabase.com
   - Check if there are any outages

2. **Review Error Messages:**
   - Check browser console (F12)
   - Check Flask app console output
   - Check Supabase Dashboard → Logs

3. **Verify API Keys:**
   - Make sure you're using the "anon public" key, not the "service_role" key
   - The anon key is safe for client-side use
   - The service_role key should NEVER be used in client code

4. **Check Row Level Security (RLS):**
   - Make sure RLS policies allow authenticated users
   - The SQL schema includes proper policies

### Quick Test Commands

```bash
# Test Supabase connection
python test_supabase_auth.py

# Run Flask app with debug
python platform_app_supabase.py

# Check if .env file exists and has correct format
# (On Windows PowerShell)
Get-Content .env

# (On Linux/Mac)
cat .env
```

### Need More Help?

- Check Supabase Documentation: https://supabase.com/docs
- Check Supabase Auth Docs: https://supabase.com/docs/guides/auth
- Review your Flask app logs for detailed error messages
