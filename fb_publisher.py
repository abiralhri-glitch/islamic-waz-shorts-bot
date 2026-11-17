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

def publish_reels_video(video_path: str, caption: str, page_id: str = None, access_token: str = None) -> str:
    page_id = page_id or os.environ.get("FB_PAGE_ID")
    access_token = access_token or os.environ.get("FB_PAGE_ACCESS_TOKEN")

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

    resp = requests.post(init_url, data=init_payload, timeout=30)
    data = resp.json()
    if "video_id" not in data or "upload_url" not in data:
        print(f"[!] Reels init failed: {data}. Falling back to standard video upload...")
        return publish_standard_video(video_path, caption, page_id, access_token)

    video_id = data["video_id"]
    upload_url = data["upload_url"]
    print(f"[+] Initialized Reel upload session: Video ID {video_id}")

    # Phase 2: Upload Binary Video Data
    with open(video_path, "rb") as f:
        video_bytes = f.read()

    upload_headers = {
        "Authorization": f"OAuth {access_token}",
        "offset": "0",
        "file_size": str(file_size)
    }

    upload_resp = requests.post(upload_url, headers=upload_headers, data=video_bytes, timeout=180)
    print(f"[+] Upload payload status: {upload_resp.status_code}")

    # Phase 3: Finish and Publish
    finish_payload = {
        "upload_phase": "finish",
        "access_token": access_token,
        "video_id": video_id,
        "video_state": "PUBLISHED",
        "description": caption
    }

    finish_resp = requests.post(init_url, data=finish_payload, timeout=30)
    finish_data = finish_resp.json()
    print(f"[+] Finish Reels result: {finish_data}")

    if finish_data.get("success"):
        print(f"[SUCCESS] Reel successfully published! Video ID: {video_id}")
        return video_id
    else:
        print(f"[!] Reels finish issue: {finish_data}. Video ID: {video_id}")
        return video_id

def publish_standard_video(video_path: str, caption: str, page_id: str, access_token: str) -> str:
    url = f"{BASE_URL}/{page_id}/videos"
    with open(video_path, "rb") as f:
        files = {"source": f}
        data = {
            "description": caption,
            "access_token": access_token
        }
        resp = requests.post(url, files=files, data=data, timeout=180)
    res = resp.json()
    if "id" in res:
        print(f"[SUCCESS] Standard video published! Video ID: {res['id']}")
        return res["id"]
    raise RuntimeError(f"Video upload failed: {res}")
