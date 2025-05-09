import os
from dotenv import load_dotenv
from supabase import create_client, Client
from logging_setup import logger

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("Missing Supabase environment variables.")
    raise EnvironmentError("Missing Supabase environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
logger.info("Supabase client initialized successfully.")