"""
Supabase Configuration
Store your Supabase credentials here or use environment variables
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

# Supabase configuration
# Get these from your Supabase project settings: https://app.supabase.com/project/_/settings/api
SUPABASE_URL = os.getenv("SUPABASE_URL", "your-supabase-url")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your-supabase-anon-key")

# Validate credentials
if SUPABASE_URL == "your-supabase-url" or SUPABASE_KEY == "your-supabase-anon-key":
    raise ValueError(
        "Please set SUPABASE_URL and SUPABASE_KEY in your .env file. "
        "Get these from: https://app.supabase.com → Your Project → Settings → API"
    )

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
