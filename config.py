import os
from dotenv import load_dotenv

load_dotenv()

# Facebook Graph API Credentials for 'সেরা ইসলামিক শর্ট ওয়াজ' (Page ID: 1541701802352983)
# Verified Lifetime Permanent Page Access Token (expires_at: 0 - NEVER EXPIRES)
PERMANENT_WAZ_TOKEN = "EAAe1H3izQCYBTDOpKlJZAxRSHI1BYDzKy5ZC2bZAWi4XTtui2ZC12j3V6oDLfD78HzYDjtStPvkqdzGmb7QyUtLbbPftqhLngyPK6udrc0Ky6eaX6ElOL6FcbwK01VD6irDCnU6k5QPmVl3zwugUyDS6g7Jh3Cy0Xbq7D1ucrOjRjDR1XiW595wjDewAKu9aniZBe"

FB_PAGE_ID = os.getenv("FB_PAGE_ID", "1541701802352983")
FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN") or PERMANENT_WAZ_TOKEN

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
