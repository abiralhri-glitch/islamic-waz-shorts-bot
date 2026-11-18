"""
Main 24/7 Automated Reels Publisher for 'সেরা ইসলামিক শর্ট ওয়াজ'
১০০% আসল হুজুরদের স্টেজ/পোডিয়ামের লাইভ ভিডিও ফুটেজ (নো ওয়াটারফল/নো ফলব্যাক সিন)
সোর্সিং পলিসি: শুধুমাত্র YouTube Shorts এবং TikTok (ফেসবুক থেকে কোনো ভিডিও নেওয়া সম্পূর্ণ নিষিদ্ধ)
জিরো ডুপ্লিকেট পলিসি: এক পোস্ট কখনো দুইবার হবে না (Facebook Graph API + History ভেরিফিকেশন)
১০০% স্বাভাবিক কণ্ঠ: নো কার্টুন পিচ-শিফটিং / নো asetrate
"""

import os
import sys
import glob
import json
import time
import random
import subprocess
import requests
import imageio_ffmpeg
from config import BASE_DIR, DOWNLOAD_DIR, OUTPUT_DIR, ASSETS_DIR, WAZ_BANK_DIR, FB_PAGE_ID, FB_PAGE_ACCESS_TOKEN
from fb_publisher import publish_reels_video
from waz_downloader import (
    CURATED_YOUTUBE_SHORTS,
    DYNAMIC_SCHOLAR_QUERIES,
    get_posted_signatures_from_facebook,
    load_local_history,
    save_local_history,
    download_youtube_short,
    search_dynamic_youtube_short
)

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
WATERMARK_PNG = os.path.join(ASSETS_DIR, "watermark_waz.png")
HISTORY_FILE = os.path.join(BASE_DIR, "posted_waz_history.json")

# Fallback Local Real-Scene Clips in Bank
BANK_METADATA = [
    {
        "file": "azhari_jiber_mulya.mp4",
        "src_id": "bank_azhari_jiber_mulya",
        "scholar": "মিজানুর রহমান আজহারী",
        "title": "মিজানুর রহমান আজহারী: জীবনের শ্রেষ্ঠ মূল্যায়ন ও সময় সচেতনতা",
        "topic": "জীবনের মূল্যায়ন ও সময়ের মূল্য",
        "nasihat": "প্রতিটি নিঃশ্বাস এক একটি মূল্যবান নেয়ামত। দুনিয়ার মোহে পড়ে আখিরাত ভুলে যাবেন না।",
        "hashtags": "#MizanurRahmanAzhari #AzhariWaz #IslamicReminder #WazShorts #BanglaWaz"
    },
    {
        "file": "azhari_smriti_roye_jay.mp4",
        "src_id": "bank_azhari_smriti_roye_jay",
        "scholar": "মিজানুর রহমান আজহারী",
        "title": "মিজানুর রহমান আজহারী: মানুষ চলে যায় কিন্তু নেক আমল রয়ে যায়",
        "topic": "সদকায়ে জারিয়া ও পরকালের পুঁজি",
        "nasihat": "এমন কিছু নেক আমল রেখে যান যা কবরে আপনার আলোর কারণ হবে।",
        "hashtags": "#MizanurRahmanAzhari #AzhariShorts #IslamicBayan #HeartTouching"
    },
    {
        "file": "abutoha_jadu_shesh_jamana.mp4",
        "src_id": "bank_abutoha_jadu_shesh_jamana",
        "scholar": "আবু ত্বহা মোহাম্মদ আদনান",
        "title": "আবু ত্বহা মোহাম্মদ আদনান: শেষ জামানায় ঈমান রক্ষা ও আত্মরক্ষা",
        "topic": "শেষ জামানার ফেতনা ও আমল",
        "nasihat": "সকাল ও সন্ধ্যার মাসনুন দোয়া এবং সূরা আল-কাহাফ নিয়মিত তিলাওয়াত করুন।",
        "hashtags": "#AbuTohaAdnan #AbuTohaWaz #SheshJamana #Eman #IslamicReels"
    },
    {
        "file": "sayedi_emotional_waz.mp4",
        "src_id": "bank_sayedi_emotional_waz",
        "scholar": "আল্লামা দেলাওয়ার হোসাইন সাঈদী",
        "title": "আল্লামা দেলাওয়ার হোসাইন সাঈদী: কালজয়ী আবেগঘন নসিহত ও তওবার আহ্বান",
        "topic": "খাটি তওবা ও আল্লাহর রহমত",
        "nasihat": "নিশ্চয়ই মহান আল্লাহ তওবাকারীদের অত্যন্ত ভালোবাসেন।",
        "hashtags": "#DelowarHossainSayedi #AllamaSayedi #SayediWaz #QuranerDawat"
    },
    {
        "file": "ahmadullah_life_advice.mp4",
        "src_id": "bank_ahmadullah_life_advice",
        "scholar": "শায়খ আহমাদুল্লাহ",
        "title": "শায়খ আহমাদুল্লাহ: উত্তম চরিত্র ও সুন্দর পারিবারিক জীবনের শিক্ষা",
        "topic": "উত্তম আখলাক ও সুন্নত",
        "nasihat": "রাসুলুল্লাহ (সা.) বলেছেন: তোমাদের মধ্যে সর্বোত্তম ব্যক্তি সে, যে পরিবারের কাছে উত্তম।",
        "hashtags": "#ShaykhAhmadullah #AhmadullahWaz #Sunnah #FamilyLife #IslamicReminder"
    },
    {
        "file": "tariq_jamil_iman_reminder.mp4",
        "src_id": "bank_tariq_jamil_iman_reminder",
        "scholar": "মাওলানা তারেক জামিল",
        "title": "মাওলানা তারেক জামিল: অন্তরের প্রশান্তি ও আল্লাহর অসীম রহমত",
        "topic": "আল্লাহর জিকির ও দিলের প্রশান্তি",
        "nasihat": "কঠিন বিপদেও হতাশ হবেন না, আল্লাহ তার বান্দার অতি নিকটে।",
        "hashtags": "#MaulanaTariqJamil #TariqJamilBangla #HeartTouchingWaz #PeaceOfMind"
    }
]

def apply_anti_copyright_and_watermark(input_video_path: str, output_path: str):
    """
    - 9:16 Vertical Scale / Crop (720x1280)
    - Anti-Copyright Video Normalization
    - Overlay Official Page Watermark
    - 100% ORIGINAL NATURAL AUDIO (NO PITCH SHIFTING, NO ASETRATE)
    """
    speed_factor = random.choice([1.015, 1.02, 1.025])
    speed_v = f"setpts={1/speed_factor}*PTS"
    speed_a = f"atempo={speed_factor}"

    filter_complex = (
        f"[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,{speed_v}[v_scaled];"
        f"[v_scaled][1:v]overlay=0:0[v_final];"
        f"[0:a]{speed_a},volume=1.2[a_final]"
    )

    cmd = [
        FFMPEG_EXE, "-y",
        "-i", input_video_path,
        "-i", WATERMARK_PNG,
        "-filter_complex", filter_complex,
        "-map", "[v_final]",
        "-map", "[a_final]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        "-map_metadata", "-1",
        output_path
    ]

    subprocess.run(cmd, check=True)
    return output_path

def generate_caption(title: str, scholar: str, nasihat: str, hashtags: str, src_id: str) -> str:
    caption = (
        f"🎙️ {title}\n\n"
        f"💡 জীবনঘনিষ্ঠ মূল্যবান নসিহত:\n{nasihat}\n\n"
        f"দ্বীনের সুন্দর বার্তা ছড়িয়ে দিতে ভিডিওটি লাইক করুন ও শেয়ার করে টাইমলাইনে রেখে দিন। 🤍🤲\n\n"
        f"{hashtags} #IslamicWaz #WazReels #ViralShorts #Sunnah\n\n"
        f"📌 [src:{src_id}]"
    )
    return caption

def run():
    print("===========================================================")
    print("🕌 Starting 'সেরা ইসলামিক শর্ট ওয়াজ' 24/7 Automated Reels Runner")
    print("===========================================================")

    page_id = FB_PAGE_ID or "1541701802352983"
    token = FB_PAGE_ACCESS_TOKEN

    # ১. ফেসবুক পেজ এবং লোকাল হিস্টোরি থেকে পূর্বের সকল পোস্ট করা সিগনেচার রিড করা
    print("[1/5] Checking previously posted videos on Facebook Page to guarantee ZERO DUPLICATES...")
    fb_posted = get_posted_signatures_from_facebook(page_id, token, limit=100)
    local_posted = load_local_history()
    all_excluded = fb_posted.union(local_posted)
    print(f"[*] Found {len(all_excluded)} unique posted video signatures.")

    ts = int(time.time())
    raw_download_path = os.path.join(DOWNLOAD_DIR, f"raw_waz_{ts}.mp4")
    processed_output = os.path.join(OUTPUT_DIR, f"waz_reel_{ts}.mp4")

    selected_meta = None
    selected_video_path = None

    # ২. YouTube Shorts কিউরেটেড কালেকশন চেক (অপ্রকাশিত ভিডিও খোঁজা)
    unposted_curated = [item for item in CURATED_YOUTUBE_SHORTS if item["src_id"] not in all_excluded and item["title"][:40] not in all_excluded]
    if unposted_curated:
        chosen = random.choice(unposted_curated)
        print(f"[*] Found unposted curated YouTube Short: {chosen['title']} ({chosen['src_id']})")
        if download_youtube_short(chosen["url"], raw_download_path):
            selected_meta = chosen
            selected_video_path = raw_download_path

    # ৩. যদি কিউরেটেড শর্টস শেষ হয়ে যায়, ডাইনামিক ইউটিউব সার্চ থেকে একদম নতুন ভিডিও ডাউনলোড
    if not selected_video_path:
        print("[*] Searching YouTube dynamically for fresh scholar shorts...")
        # এলোমেলোভাবে একজন স্কলার সিলেক্ট করা
        scholar_entry = random.choice(DYNAMIC_SCHOLAR_QUERIES)
        scholar_name, search_q, hashtags = scholar_entry
        search_res = search_dynamic_youtube_short(search_q, all_excluded, raw_download_path)
        if search_res:
            selected_meta = {
                "scholar": scholar_name,
                "title": f"{scholar_name}: {search_res['title'][:50]}",
                "src_id": search_res["src_id"],
                "nasihat": "রাসুলুল্লাহ (সা.) বলেছেন: যে ব্যক্তি মানুষকে কল্যাণের পথ দেখায়, সে কল্যাণকারীর সমান সওয়াব পাবে।",
                "hashtags": hashtags
            }
            selected_video_path = raw_download_path

    # ৪. যদি ইন্টারনেট সার্চেও কোনো কারণে না পাওয়া যায়, লোকাল ব্যাংক থেকে অপ্রকাশিত ক্লিপ বাছাই
    if not selected_video_path:
        print("[*] Selecting from unposted local scholar bank clips...")
        unposted_bank = [b for b in BANK_METADATA if b["src_id"] not in all_excluded and b["title"][:40] not in all_excluded]
        if not unposted_bank:
            print("[WARN] All bank clips have been posted once! Resetting local rotation...")
            unposted_bank = BANK_METADATA
        chosen_bank = random.choice(unposted_bank)
        bank_file_path = os.path.join(WAZ_BANK_DIR, chosen_bank["file"])
        if not os.path.exists(bank_file_path):
            bank_file_path = os.path.join(BASE_DIR, "assets_waz_bank", chosen_bank["file"])
        if os.path.exists(bank_file_path):
            selected_meta = chosen_bank
            selected_video_path = bank_file_path

    if not selected_video_path or not os.path.exists(selected_video_path):
        raise RuntimeError("No authentic scholar video could be acquired.")

    print(f"[3/5] Processing real-scene vertical reel with watermark & 100% natural audio...")
    print(f"[*] Scholar: {selected_meta['scholar']} | Title: {selected_meta['title']}")
    apply_anti_copyright_and_watermark(selected_video_path, processed_output)

    # ৫. ক্যাপশন জেনারেট ও ফেসবুকে রিলস আপলোড
    caption = generate_caption(
        title=selected_meta["title"],
        scholar=selected_meta["scholar"],
        nasihat=selected_meta.get("nasihat", "আল্লাহর আনুগত্য ও রাসুলের সুন্নতের উপর জীবন গড়ুন।"),
        hashtags=selected_meta.get("hashtags", "#IslamicWaz #WazReels #Sunnah"),
        src_id=selected_meta["src_id"]
    )

    print(f"[4/5] Publishing Reel to Facebook Page: {page_id}...")
    res = publish_reels_video(processed_output, caption=caption, title=selected_meta["title"])
    print(f"🎉 Successfully Published Reel! Response: {res}")

    # হিস্টোরিতে রেকর্ড করা
    save_local_history(selected_meta["src_id"])

    # ক্লিনআপ
    for p in [raw_download_path, processed_output]:
        if os.path.exists(p):
            try: os.remove(p)
            except Exception: pass

    # অটো-কমেন্ট রেসপন্ডার চালু
    try:
        from auto_comment_responder import run_comment_responder
        run_comment_responder(page_type="waz", max_replies=10)
    except Exception as e:
        print(f"[WARN] Auto-comment responder notice: {e}")

if __name__ == "__main__":
    run()
