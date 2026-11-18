"""
Facebook Reels & Video Publisher for Islamic Waz Short Reels
Supports Facebook Graph API v22.0 Video Reels resumable upload protocol
"""

import os
import sys
import time
import requests

GRAPH_API_VERSION = "v22.0"
BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

# Guaranteed Permanent (Never-Expiring) Page Access Token & ID Fallback
DEFAULT_WAZ_PAGE_ID = "1541701802352983"
PERMANENT_WAZ_ACCESS_TOKEN = "EAAe1H3izQCYBTCSEu0hsdmYztnSiFPLlxbO1PwjZAMZBDL96VhST1KwwTcgs3SNM29ZBoZAsg15RRPkZCwn3TFh6PkUfvo7f65A17bub3eZBLiEeimaZBhG4f5YQywXbbLzly6o8Cpqzttt9t3rfA95fZAIbxLU5Hjbb5PIvjPSeiQZAUOvXJ5mY2ZAN5ZAoiZCDjBztceC8"


def publish_reels_video(video_path: str, caption: str, page_id: str = None, access_token: str = None) -> str:
    page_id = page_id or os.environ.get("FB_PAGE_ID") or DEFAULT_WAZ_PAGE_ID
    
    # Priority: Permanent Token Fallback ensures 24/7 never-expiring publishing
    access_token = PERMANENT_WAZ_ACCESS_TOKEN or os.environ.get("FB_PAGE_ACCESS_TOKEN")

    if not page_id or not access_token:
        raise ValueError("FB_PAGE_ID or FB_PAGE_ACCESS_TOKEN is missing!")

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found at: {video_path}")

    file_size = os.path.getsize(video_path)
    print(f"[*] Starting Reels upload for video: {video_path} ({file_size / (1024*1024):.2f} MB)")

    # Phase 1: Initialize Reels Upload Session
    init_url = f"{BASE_URL}/{page_id}/video_reels"
    init_payload = {
        "upload_phase": "start",
        "access_token": access_token
    }

    init_resp = requests.post(init_url, data=init_payload, timeout=30)
    init_data = init_resp.json()

    if "video_id" not in init_data:
        print(f"[!] Session init error: {init_data}")
        # Try fallback token
        if access_token != PERMANENT_WAZ_ACCESS_TOKEN:
            print("[*] Retrying with permanent backup Page Access Token...")
            access_token = PERMANENT_WAZ_ACCESS_TOKEN
            init_payload["access_token"] = access_token
            init_resp = requests.post(init_url, data=init_payload, timeout=30)
            init_data = init_resp.json()

        if "video_id" not in init_data:
            raise RuntimeError(f"Failed to initialize Reels upload: {init_data}")

    video_id = init_data["video_id"]
    upload_url = init_data.get("upload_url", f"https://rupload.facebook.com/video-upload/{GRAPH_API_VERSION}/{video_id}")
    print(f"[+] Initialized Reel Video ID: {video_id}")

    # Phase 2: Upload Binary Video Data
    headers = {
        "Authorization": f"OAuth {access_token}",
        "offset": "0",
        "file_size": str(file_size),
        "Content-Type": "application/octet-stream"
    }

    with open(video_path, "rb") as f:
        video_bytes = f.read()

    upload_resp = requests.post(upload_url, headers=headers, data=video_bytes, timeout=180)
    if upload_resp.status_code != 200:
        raise RuntimeError(f"Video chunk upload failed (status {upload_resp.status_code}): {upload_resp.text}")

    print("[+] Video payload uploaded successfully to Facebook.")

    # Phase 3: Finalize and Publish Reel
    finish_url = f"{BASE_URL}/{page_id}/video_reels"
    finish_payload = {
        "upload_phase": "finish",
        "access_token": access_token,
        "video_id": video_id,
        "video_state": "PUBLISHED",
        "description": caption
    }

    finish_resp = requests.post(finish_url, data=finish_payload, timeout=30)
    finish_data = finish_resp.json()

    if finish_data.get("success") is True or "id" in finish_data or "post_id" in finish_data:
        print(f"[SUCCESS] Islamic Waz Reel published successfully! Video ID: {video_id}")
        return str(video_id)
    else:
        print(f"[!] Publish status: {finish_data}")
        return str(video_id)
