import os
from dotenv import load_dotenv

load_dotenv()

# Facebook Graph API Credentials for 'Jannat' (Page ID: 1251877234677514)
# Verified Lifetime Permanent Page Access Token (expires_at: 0 - NEVER EXPIRES)
PERMANENT_JANNAT_TOKEN = "EAAe1H3izQCYBTMAHOW6UHJ9kMJL3VsrjVy9nZCDBrSPZAG7GkYe7uTGCya2GZAMZCLkBwTFPFbTmR4OSPRf3BOZCONj5IBuNlSSPUtXstbTF3QExEvbsjpKr4TtrVxKizGEfoCQqHlZAaaRG5ZA7yZCIVLC909cBUZCwZAWfkmVYZAvIP2k911vONYSUEkMTpeHKqFNsMw3GOw1"

FB_PAGE_ID = "1251877234677514"
FB_PAGE_ACCESS_TOKEN = PERMANENT_JANNAT_TOKEN

# Meta Graph API Base URL
FB_GRAPH_API_VERSION = "v21.0"
FB_GRAPH_URL = f"https://graph.facebook.com/{FB_GRAPH_API_VERSION}"

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
WAZ_BANK_DIR = os.path.join(ASSETS_DIR, "waz_bank")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(WAZ_BANK_DIR, exist_ok=True)
