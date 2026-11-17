"""
Islamic Waz Short Reels Downloader & Anti-Copyright Engine
Downloads, optimizes, and prepares viral 9:16 vertical Waz reels for
Mizanur Rahman Azhari, Abu Toha Adnan, Allama Sayedi, Ahmadullah, etc.
Includes a rich verified archive pool of authentic Bangla Waz & lectures.
"""

import os
import re
import sys
import json
import random
import logging
import subprocess
import requests
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

WAZ_SCHOLARS_QUERIES = [
    {
        "scholar": "মিজানুর রহমান আজহারী",
        "hashtag": "#mizanur_rahman_azhari",
        "queries": [
            "mizanur rahman azhari emotional short bayan reels",
            "azhari best motivational speech islamic shorts",
            "মিজানুর রহমান আজহারী সেরা শর্ট ওয়াজ",
            "azhari heart touching waz reels"
        ]
    },
    {
        "scholar": "আবু ত্বহা মোহাম্মদ আদনান",
        "hashtag": "#abutohaadnan",
        "queries": [
            "abu toha muhammad adnan emotional status shorts",
            "abu toha adnan powerful bayan waz shorts",
            "আবু ত্বহা মোহাম্মদ আদনান শর্ট ওয়াজ",
            "abu toha adnan islamic reminders reels"
        ]
    },
    {
        "scholar": "আল্লামা দেলাওয়ার হোসাইন সাঈদী",
        "hashtag": "#delowarhossainsayedi",
        "queries": [
            "allama delowar hossain sayedi emotional bayan shorts",
            "sayedi best waz clip reels",
            "আল্লামা সাঈদী হৃদয়স্পর্শী ওয়াজ শর্টস"
        ]
    },
    {
        "scholar": "শায়খ আহমাদুল্লাহ",
        "hashtag": "#shaykhahmadullah",
        "queries": [
            "shaykh ahmadullah islamic advice shorts",
            "শায়খ আহমাদুল্লাহ উপদেশ মূলক কথা শর্টস",
            "ahmadullah short waz status reels"
        ]
    },
    {
        "scholar": "মুফতি জামশেদ মজুমদার",
        "hashtag": "#jamshedmajumdar",
        "queries": [
            "mufti jamshed majumdar waz shorts",
            "জামশেদ মজুমদার শর্ট ওয়াজ রিল"
        ]
    }
]

# ভেরিফাইড প্রামাণ্য ইসলামিক ওয়াজ ও লেকচার অডিও পুল (উচ্চমানের অরিজিনাল অডিও)
FALLBACK_ISLAMIC_SPEECHES = [
    {
        "scholar": "আবু ত্বহা মোহাম্মদ আদনান",
        "title": "আবু ত্বহা মোহাম্মদ আদনান: ফিতনাময় পরিবেশ ও ঈমান রক্ষার আমল",
        "hashtag": "#abutohaadnan",
        "audio_url": "https://archive.org/download/abu-toha-bangla-waz-mahfil/Fitnamoy-Poribesh-ALQURANS.COM.mp3",
        "offset": 120,
    },
    {
        "scholar": "আবু ত্বহা মোহাম্মদ আদনান",
        "title": "আবু ত্বহা মোহাম্মদ আদনান: কিয়ামতের বাস্তব আলামত ও প্রস্তুতি",
        "hashtag": "#abutohaadnan",
        "audio_url": "https://archive.org/download/abu-toha-bangla-waz-mahfil/Kiyamoter-Alamot-ALQURANS.COM.mp3",
        "offset": 90,
    },
    {
        "scholar": "আবু ত্বহা মোহাম্মদ আদনান",
        "title": "আবু ত্বহা মোহাম্মদ আদনান: মহাবিশ্ব সৃষ্টি ও মহান আল্লাহর কুদরত",
        "hashtag": "#abutohaadnan",
        "audio_url": "https://archive.org/download/abu-toha-bangla-waz-mahfil/Mohabisso-Sristi-O-Tar-Rohosso-ALQURANS.COM.mp3",
        "offset": 150,
    },
    {
        "scholar": "আবু ত্বহা মোহাম্মদ আদনান",
        "title": "আবু ত্বহা মোহাম্মদ আদনান: বিশ্বনবী হযরত মুহাম্মদ (সাঃ) এর জীবনের শ্রেষ্ঠ শিক্ষা",
        "hashtag": "#abutohaadnan",
        "audio_url": "https://archive.org/download/abu-toha-bangla-waz-mahfil/Rasul-Saw-er-Jiboni-ALQURANS.COM.mp3",
        "offset": 60,
    },
    {
        "scholar": "আল্লামা নুরুল ইসলাম ওলীপুরী",
        "title": "আল্লামা নুরুল ইসলাম ওলীপুরী: জীবনের শ্রেষ্ঠ শিক্ষা ও আমল",
        "hashtag": "#nurulislamolipuri",
        "audio_url": "https://archive.org/download/AllamaNurulIslamOlipuri1/Shikhkha-HathazariBarshikShommelon-MaulanaNurulIslamOlipuri.mp3",
        "offset": 45,
    },
    {
        "scholar": "মন জুড়ানো বাংলা গজল",
        "title": "বাদশাহ তুমি দীন ও দুনিয়ার (মন জুড়ানো বাংলা গজল)",
        "hashtag": "#islamic_gojol",
        "audio_url": "https://archive.org/download/prottasha/Badsha-tumi-din-o-duniyar.mp3",
        "offset": 20,
    },
    {
        "scholar": "মন জুড়ানো বাংলা গজল",
        "title": "আমি এক গুনাহগার বান্দা (হৃদয়স্পর্শী বাংলা গজল)",
        "hashtag": "#islamic_nasheed",
        "audio_url": "https://archive.org/download/prottasha/Ami-ak-gunahgar-banda.mp3",
        "offset": 18,
    }
]

# নান্দনিক লাইভ মোশন নেচার ব্যাকগ্রাউন্ড (ঝর্ণা ও জলপ্রপাত)
VERIFIED_NATURE_VIDEO = "https://ia800703.us.archive.org/32/items/quran-recitation-peaceful-nature/FernCreekFalls-720.mp4"


def download_file(url: str, dest_path: str, timeout: int = 40) -> bool:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        r = requests.get(url, stream=True, timeout=timeout, headers=headers)
        if r.status_code == 200:
            with open(dest_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
            if os.path.exists(dest_path) and os.path.getsize(dest_path) > 10000:
                return True
    except Exception as e:
        logging.warning(f"Download failed for {url}: {e}")
    return False


def synthesize_fallback_waz_reel(output_path: str, scholar_info: dict = None) -> tuple:
    """
    Synthesizes a 9:16 vertical Islamic Waz reel with live nature video background,
    authentic Islamic speech audio, and anti-copyright frequency shift.
    """
    tmp_dir = os.path.join(os.path.dirname(os.path.abspath(output_path)), "tmp_synthesis")
    os.makedirs(tmp_dir, exist_ok=True)

    bg_video_path = os.path.join(tmp_dir, "nature_bg.mp4")
    if not os.path.exists(bg_video_path) or os.path.getsize(bg_video_path) < 50000:
        logging.info(f"Downloading live motion nature background from {VERIFIED_NATURE_VIDEO}...")
        if not download_file(VERIFIED_NATURE_VIDEO, bg_video_path, timeout=60):
            logging.error("Failed to download nature background video")
            return "", {}

    # অডিও নির্বাচন
    selected_speech = random.choice(FALLBACK_ISLAMIC_SPEECHES)
    if scholar_info:
        for s in FALLBACK_ISLAMIC_SPEECHES:
            if s.get("scholar") == scholar_info.get("scholar"):
                selected_speech = s
                break

    speech_filename = f"speech_{abs(hash(selected_speech['audio_url'])) % 10000}.mp3"
    speech_path = os.path.join(tmp_dir, speech_filename)
    if not os.path.exists(speech_path) or os.path.getsize(speech_path) < 10000:
        logging.info(f"Downloading speech audio: {selected_speech['title']}...")
        if not download_file(selected_speech["audio_url"], speech_path, timeout=60):
            for candidate in FALLBACK_ISLAMIC_SPEECHES:
                cand_path = os.path.join(tmp_dir, f"speech_alt_{abs(hash(candidate['audio_url'])) % 10000}.mp3")
                if download_file(candidate["audio_url"], cand_path, timeout=40):
                    speech_path = cand_path
                    selected_speech = candidate
                    break

    if not os.path.exists(speech_path) or os.path.getsize(speech_path) < 10000:
        logging.error("Failed to download any Islamic audio")
        return "", {}

    duration = 30
    offset = selected_speech.get("offset", 30)
    logging.info(f"Synthesizing 9:16 Waz Reel: {selected_speech['title']} ({duration}s)...")

    # 9:16 ভার্টিক্যাল ভিডিও ফিল্টার + ওয়াজ অডিও ম্যাপিং
    video_filter = "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[v]"
    audio_filter = f"asetrate=44100*1.04,atempo=0.98,volume=1.9,aecho=0.8:0.8:20:0.2,afade=t=in:st=0:d=1,afade=t=out:st={duration-2}:d=2"

    cmd = [
        "ffmpeg", "-y",
        "-ss", "0", "-t", str(duration), "-i", bg_video_path,
        "-ss", str(offset), "-t", str(duration), "-i", speech_path,
        "-filter_complex", video_filter,
        "-map", "[v]",
        "-map", "1:a:0",
        "-af", audio_filter,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_path
    ]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 50000:
            logging.info(f"Waz reel synthesized successfully: {output_path} ({os.path.getsize(output_path)} bytes)")
            meta = {
                "title": selected_speech["title"],
                "scholar": selected_speech.get("scholar", "ইসলামিক নসিহত"),
                "hashtag": selected_speech.get("hashtag", "#islamic_waz"),
                "caption": f"{selected_speech['title']} | সেরা সংক্ষিপ্ত ইসলামিক নসিহত\n\n{selected_speech.get('hashtag', '#islamic_waz')} #IslamicWaz #Shorts #Reels #BanglaWaz #Islam"
            }
            return output_path, meta
        else:
            logging.error(f"FFmpeg error: {res.stderr[-400:]}")
    except Exception as e:
        logging.error(f"FFmpeg synthesis exception: {e}")

    return "", {}


def download_waz_short(output_path: str, scholar_index: int = None) -> tuple:
    """
    Main entry point: downloads a viral Waz Short reel or synthesizes a high-retention reel.
    """
    if scholar_index is not None:
        scholar_info = WAZ_SCHOLARS_QUERIES[scholar_index % len(WAZ_SCHOLARS_QUERIES)]
    else:
        scholar_info = random.choice(WAZ_SCHOLARS_QUERIES)

    query = random.choice(scholar_info["queries"])
    logging.info(f"Target Scholar: {scholar_info['scholar']} | Query: {query}")

    # yt-dlp সার্চ করার চেষ্টা
    tmp_video = output_path.replace(".mp4", "_raw.mp4")
    cmd = [
        "yt-dlp",
        "--extractor-args", "youtube:player_client=android",
        "--no-playlist",
        "--format", "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--match-filter", "duration <= 90",
        "--max-filesize", "80M",
        "--output", tmp_video,
        f"ytsearch1:{query}"
    ]

    downloaded = False
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=50)
        if res.returncode == 0 and os.path.exists(tmp_video) and os.path.getsize(tmp_video) > 50000:
            # অ্যান্টি-কপিরাইট ফিল্টার সহ রেন্ডার
            af = "asetrate=44100*1.04,atempo=0.98,volume=1.8,aecho=0.8:0.8:20:0.2"
            vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1"
            f_cmd = [
                "ffmpeg", "-y", "-i", tmp_video,
                "-vf", vf, "-af", af,
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                "-c:a", "aac", "-b:a", "192k", "-t", "60",
                output_path
            ]
            f_res = subprocess.run(f_cmd, capture_output=True, text=True, timeout=120)
            if f_res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 50000:
                downloaded = True
                meta = {
                    "title": f"{scholar_info['scholar']}: সেরা সংক্ষিপ্ত নসিহত",
                    "scholar": scholar_info["scholar"],
                    "hashtag": scholar_info["hashtag"],
                    "caption": f"{scholar_info['scholar']} | সেরা শর্ট ওয়াজ ও নসিহত\n\n{scholar_info['hashtag']} #IslamicWaz #Shorts #Reels #BanglaWaz #Islam"
                }
                return output_path, meta
    except Exception as e:
        logging.warning(f"yt-dlp attempt failed: {e}")

    # ফলব্যাক সিন্থেসিস (১০০% নির্ভরযোগ্য)
    logging.info("Falling back to guaranteed internal Islamic Waz reel synthesis...")
    return synthesize_fallback_waz_reel(output_path, scholar_info)
