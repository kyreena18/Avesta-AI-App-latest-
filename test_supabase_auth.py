"""
Test script to verify Supabase authentication is working
Run this to check if your Supabase credentials and authentication are set up correctly
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("=" * 60)
print("SUPABASE AUTHENTICATION TEST")
print("=" * 60)

# Check if credentials are set
if not SUPABASE_URL or SUPABASE_URL == "your-supabase-url":
    print("❌ ERROR: SUPABASE_URL not set in .env file")
    exit(1)

if not SUPABASE_KEY or SUPABASE_KEY == "your-supabase-anon-key":
    print("❌ ERROR: SUPABASE_KEY not set in .env file")
    exit(1)

print(f"✓ Supabase URL: {SUPABASE_URL[:30]}...")
print(f"✓ Supabase Key: {SUPABASE_KEY[:20]}...")
print()

# Initialize Supabase client
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✓ Supabase client initialized successfully")
except Exception as e:
    print(f"❌ ERROR: Failed to initialize Supabase client: {e}")
    exit(1)

# Test registration
print("\n" + "=" * 60)
print("TESTING USER REGISTRATION")
print("=" * 60)

test_email = f"test_{os.urandom(4).hex()}@example.com"
test_password = "testpassword123"
test_name = "Test User"

print(f"Test email: {test_email}")
print(f"Test password: {test_password}")

try:
    result = supabase.auth.sign_up({
        "email": test_email,
        "password": test_password,
        "options": {
            "data": {
                "name": test_name
            }
        }
    })
    
    if result and result.user:
        print(f"✓ User created successfully!")
        print(f"  User ID: {result.user.id}")
        print(f"  Email: {result.user.email}")
        
        if result.session:
            print(f"✓ Session created (email confirmation may be disabled)")
            print(f"  Access Token: {result.session.access_token[:30]}...")
        else:
            print("⚠ Session not created (email confirmation may be enabled)")
            print("  User will need to confirm email before logging in")
        
        # Test login
        print("\n" + "=" * 60)
        print("TESTING USER LOGIN")
        print("=" * 60)
        
        try:
            login_result = supabase.auth.sign_in_with_password({
                "email": test_email,
                "password": test_password
            })
            
            if login_result and login_result.user:
                print(f"✓ Login successful!")
                print(f"  User ID: {login_result.user.id}")
                if login_result.session:
                    print(f"✓ Session created")
                else:
                    print("⚠ No session (email may need confirmation)")
            else:
                print("❌ Login failed: No user returned")
        except Exception as e:
            print(f"⚠ Login test failed: {e}")
            print("  This might be expected if email confirmation is required")
        
    else:
        print("❌ User creation failed: No user returned")
        
except Exception as e:
    print(f"❌ Registration failed: {e}")
    print("\nCommon issues:")
    print("  1. Check if email confirmation is enabled in Supabase Dashboard")
    print("  2. Verify your SUPABASE_URL and SUPABASE_KEY are correct")
    print("  3. Check Supabase project status and API settings")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print("\nTo disable email confirmation in Supabase:")
print("  1. Go to Supabase Dashboard → Authentication → Settings")
print("  2. Disable 'Enable email confirmations'")
print("  3. Save changes")
