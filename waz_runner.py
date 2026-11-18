"""
Main 24/7 Automated Reels Publisher for 'সেরা ইসলামিক শর্ট ওয়াজ'
১০০% আসল হুজুরদের স্টেজ/পোডিয়ামের লাইভ ভিডিও ফুটেজ (নো ওয়াটারফল/নো ফলব্যাক সিন)
সকল শীর্ষ হুজুরদের রিলস: মিজানুর রহমান আজহারী, আবু ত্বহা আদনান, শায়খ আহমাদুল্লাহ, আল্লামা সাঈদী, মাওলানা তারেক জামিল
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
from config import BASE_DIR, DOWNLOAD_DIR, OUTPUT_DIR, ASSETS_DIR, WAZ_BANK_DIR
from fb_publisher import publish_reels_video
from auto_comment_responder import reply_to_recent_comments

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
WATERMARK_PNG = os.path.join(ASSETS_DIR, "watermark_waz.png")
HISTORY_FILE = os.path.join(BASE_DIR, "posted_waz_history.json")

SCHOLAR_BANK_METADATA = [
    {
        "file": "azhari_jiber_mulya.mp4",
        "scholar": "মিজানুর রহমান আজহারী",
        "title": "মিজানুর রহমান আজহারী: জীবনের শ্রেষ্ঠ মূল্যায়ন ও সময় সচেতনতা",
        "topic": "জীবনের মূল্যায়ন ও সময়ের মূল্য",
        "nasihat": "প্রতিটি নিঃশ্বাস এক একটি মূল্যবান নেয়ামত। দুনিয়ার মোহে পড়ে আখিরাত ভুলে যাবেন না।",
        "hashtags": "#MizanurRahmanAzhari #AzhariWaz #IslamicReminder #WazShorts #BanglaWaz"
    },
    {
        "file": "azhari_smriti_roye_jay.mp4",
        "scholar": "মিজানুর রহমান আজহারী",
        "title": "মিজানুর রহমান আজহারী: মানুষ চলে যায় কিন্তু নেক আমল রয়ে যায়",
        "topic": "সদকায়ে জারিয়া ও পরকালের পুঁজি",
        "nasihat": "এমন কিছু নেক আমল রেখে যান যা কবরে আপনার আলোর কারণ হবে।",
        "hashtags": "#MizanurRahmanAzhari #AzhariShorts #IslamicBayan #HeartTouching"
    },
    {
        "file": "abutoha_jadu_shesh_jamana.mp4",
        "scholar": "আবু ত্বহা মোহাম্মদ আদনান",
        "title": "আবু ত্বহা মোহাম্মদ আদনান: শেষ জামানায় ঈমান রক্ষা ও আত্মরক্ষা",
        "topic": "শেষ জামানার ফেতনা ও আমল",
        "nasihat": "সকাল ও সন্ধ্যার মাসনুন দোয়া এবং সূরা আল-কাহাফ নিয়মিত তিলাওয়াত করুন।",
        "hashtags": "#AbuTohaAdnan #AbuTohaWaz #SheshJamana #Eman #IslamicReels"
    },
    {
        "file": "sayedi_emotional_waz.mp4",
        "scholar": "আল্লামা দেলাওয়ার হোসাইন সাঈদী",
        "title": "আল্লামা দেলাওয়ার হোসাইন সাঈদী: কালজয়ী আবেগঘন নসিহত ও তওবার আহ্বান",
        "topic": "খাটি তওবা ও আল্লাহর রহমত",
        "nasihat": "নিশ্চয়ই মহান আল্লাহ তওবাকারীদের অত্যন্ত ভালোবাসেন।",
        "hashtags": "#DelowarHossainSayedi #AllamaSayedi #SayediWaz #QuranerDawat"
    },
    {
        "file": "ahmadullah_life_advice.mp4",
        "scholar": "শায়খ আহমাদুল্লাহ",
        "title": "শায়খ আহমাদুল্লাহ: উত্তম চরিত্র ও সুন্দর পারিবারিক জীবনের শিক্ষা",
        "topic": "উত্তম আখলাক ও সুন্নত",
        "nasihat": "রাসুলুল্লাহ (সা.) বলেছেন: তোমাদের মধ্যে সর্বোত্তম ব্যক্তি সে, যে পরিবারের কাছে উত্তম।",
        "hashtags": "#ShaykhAhmadullah #AhmadullahWaz #Sunnah #FamilyLife #IslamicReminder"
    },
    {
        "file": "tariq_jamil_iman_reminder.mp4",
        "scholar": "মাওলানা তারেক জামিল",
        "title": "মাওলানা তারেক জামিল: অন্তরের প্রশান্তি ও আল্লাহর অসীম রহমত",
        "topic": "আল্লাহর জিকির ও দিলের প্রশান্তি",
        "nasihat": "কঠিন বিপদেও হতাশ হবেন না, আল্লাহ তার বান্দার অতি নিকটে।",
        "hashtags": "#MaulanaTariqJamil #TariqJamilBangla #HeartTouchingWaz #PeaceOfMind"
    }
]

def load_posted_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_posted_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[WARN] Failed to save history: {e}")

def pick_next_scholar_clip():
    history = load_posted_history()
    available = [item for item in SCHOLAR_BANK_METADATA if item["file"] not in history]
    if not available:
        print("[*] All scholar clips shared once! Resetting cycle for fresh dynamic rotation...")
        history = []
        available = SCHOLAR_BANK_METADATA

    selected = random.choice(available)
    history.append(selected["file"])
    save_posted_history(history)
    return selected

def apply_anti_copyright_and_watermark(input_video_path: str, output_path: str):
    """
    - 9:16 Vertical Crop / Scale (720x1280)
    - Anti-Copyright Audio Normalization + Volume Boost
    - Subtle Speed Adjustment (1.025x)
    - Overlay Official Page Watermark
    - Strip Metadata
    """
    speed_factor = random.choice([1.02, 1.03, 1.025])
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
        "-c:a", "aac", "-b:a", "128k",
        "-map_metadata", "-1",
        output_path
    ]

    subprocess.run(cmd, check=True)
    return output_path

def generate_caption(meta: dict):
    scholar = meta["scholar"]
    title = meta["title"]
    nasihat = meta["nasihat"]
    hashtags = meta["hashtags"]

    caption = (
        f"🎙️ {title}

"
        f"💡 জীবনঘনিষ্ঠ মূল্যবান নসিহত:
"{nasihat}"

"
        f"দ্বীনের সুন্দর বার্তা ছড়িয়ে দিতে ভিডিওটি লাইক করুন ও শেয়ার করে টাইমলাইনে রেখে দিন। 🤍🤲

"
        f"{hashtags} #IslamicWaz #WazReels #ViralShorts #Sunnah"
    )
    return caption

def run():
    print("===========================================================")
    print("🕌 Starting 'সেরা ইসলামিক শর্ট ওয়াজ' 24/7 Automated Reels Runner")
    print("===========================================================")

    meta = pick_next_scholar_clip()
    video_filename = meta["file"]
    source_path = os.path.join(WAZ_BANK_DIR, video_filename)

    if not os.path.exists(source_path):
        # Fallback search locally
        alt_paths = [os.path.join(BASE_DIR, "assets_waz_bank", video_filename), video_filename]
        for p in alt_paths:
            if os.path.exists(p):
                source_path = p
                break

    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Scholar video clip not found: {source_path}")

    ts = int(time.time())
    processed_output = os.path.join(OUTPUT_DIR, f"waz_reel_{ts}.mp4")

    print(f"[*] Selected Scholar: {meta['scholar']} | Clip: {video_filename}")
    print(f"[*] Processing real-scene vertical reel with watermark & anti-copyright...")
    apply_anti_copyright_and_watermark(source_path, processed_output)

    caption = generate_caption(meta)
    print(f"[*] Publishing Reel to Facebook Page...")
    res = publish_reels_video(processed_output, caption=caption, title=meta["title"])
    print(f"✅ Successfully Published Reel! Details: {res}")

    # Cleanup processed local output
    if os.path.exists(processed_output):
        try: os.remove(processed_output)
        except Exception: pass

    # Contextual Auto-Comment Responder
    try:
        reply_to_recent_comments()
    except Exception as e:
        print(f"[WARN] Auto-comment responder notice: {e}")

if __name__ == "__main__":
    run()
