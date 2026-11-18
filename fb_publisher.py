"""
Facebook Reels Publisher for 'সেরা ইসলামিক শর্ট ওয়াজ'
Uses Meta Graph API Resumable Reels Protocol with Lifetime Permanent Page Access Token.
"""

import os
import sys
import time
import requests
from config import FB_PAGE_ID, FB_PAGE_ACCESS_TOKEN, FB_GRAPH_URL

def publish_reels_video(video_path: str, caption: str, title: str = None) -> dict:
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found at: {video_path}")

    file_size = os.path.getsize(video_path)
    print(f"[*] Starting Reels upload for video: {video_path} ({file_size / (1024*1024):.2f} MB)")

    # Phase 1: Initialize Reels Upload Session
    init_url = f"{FB_GRAPH_URL}/{FB_PAGE_ID}/video_reels"
    init_payload = {
        "upload_phase": "start",
        "access_token": FB_PAGE_ACCESS_TOKEN
    }

    init_resp = requests.post(init_url, data=init_payload, timeout=30)
    init_data = init_resp.json()

    if "video_id" not in init_data:
        print(f"[!] Session init error: {init_data}")
        raise RuntimeError(f"Failed to start Reels session: {init_data}")

    video_id = init_data["video_id"]
    upload_url = init_data["upload_url"]
    print(f"[*] Session initialized successfully! Video ID: {video_id}")

    # Phase 2: Upload Video Binary
    with open(video_path, "rb") as f:
        video_bytes = f.read()

    upload_headers = {
        "Authorization": f"OAuth {FB_PAGE_ACCESS_TOKEN}",
        "offset": "0",
        "file_size": str(file_size)
    }

    upload_resp = requests.post(upload_url, headers=upload_headers, data=video_bytes, timeout=120)
    upload_data = upload_resp.json()
    print(f"[*] Binary upload response: {upload_data}")

    # Phase 3: Publish Reel
    finish_url = f"{FB_GRAPH_URL}/{FB_PAGE_ID}/video_reels"
    finish_payload = {
        "upload_phase": "finish",
        "access_token": FB_PAGE_ACCESS_TOKEN,
        "video_id": video_id,
        "video_state": "PUBLISHED",
        "description": caption
    }
    if title:
        finish_payload["title"] = title

    finish_resp = requests.post(finish_url, data=finish_payload, timeout=30)
    finish_data = finish_resp.json()
    print(f"[*] Publish response: {finish_data}")

    if finish_data.get("success"):
        print(f"[SUCCESS] Reel {video_id} successfully published to Facebook!")
        return {"video_id": video_id, "status": "published", "success": True}

    return finish_data
