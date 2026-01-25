"""
Supabase Configuration Example
Copy this file to supabase_config.py and fill in your credentials
"""

import os
from supabase import create_client, Client

# ========================================
# SUPABASE CREDENTIALS - FILL THESE IN
# ========================================
# Get these from: https://app.supabase.com → Your Project → Settings → API
#
# 1. Project URL: https://xxxxx.supabase.co
# 2. Anon Key: Long string starting with eyJ...

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project-id.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your-anon-key-here")

# ========================================
# DO NOT EDIT BELOW THIS LINE
# ========================================

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
