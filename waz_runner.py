"""
Main Execution Script for Islamic Waz Short Reels Auto-Poster
Integrates Waz downloader, video processing, and Facebook Graph API Reels Publisher.
"""

import os
import sys
import logging
from waz_downloader import prepare_waz_reel_for_publishing
from fb_publisher import publish_reels_video

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def run():
    logging.info("=== Starting Islamic Waz Short Reels Publisher ===")
    
    # 1. Prepare vertical Waz reel video
    reel_data = prepare_waz_reel_for_publishing()
    if not reel_data or not reel_data.get("video_path") or not os.path.exists(reel_data["video_path"]):
        logging.error("Failed to prepare Waz reel video.")
        sys.exit(1)
        
    video_path = reel_data["video_path"]
    caption = reel_data["caption"]
    scholar = reel_data.get("scholar", "ইসলামিক স্কলার")
    title = reel_data.get("title", "ওয়াজ শর্ট")
    
    logging.info(f"Video Prepared: {video_path} (Size: {os.path.getsize(video_path)} bytes)")
    logging.info(f"Scholar: {scholar} | Title: {title}")
    logging.info(f"Caption Preview:\n{caption[:100]}...")
    
    # 2. Publish vertical reel to Facebook
    res = publish_reels_video(video_path, caption)
    if res:
        logging.info(f"[SUCCESS] Successfully published Islamic Waz Reel to Facebook! Result: {res}")
    else:
        logging.error("Failed to publish Waz Reel to Facebook.")
        sys.exit(1)


    # 3. Contextual Auto-Comment Responder
    try:
        from auto_comment_responder import run_comment_responder
        run_comment_responder(page_type="waz", max_replies=10)
    except Exception as e:
        logging.warning(f"Auto comment responder warning: {e}")

if __name__ == "__main__":
    run()
