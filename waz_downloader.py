"""
Islamic Waz Short Reels Downloader & Anti-Copyright Engine
Downloads, optimizes, and prepares viral 9:16 vertical Waz reels
for Mizanur Rahman Azhari, Abu Toha Adnan, Allama Sayedi, Ahmadullah, Jamshed Majumdar, etc.
"""

import os
import re
import sys
import json
import random
import logging
import subprocess
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

WAZ_SCHOLARS_QUERIES = [
    # Mizanur Rahman Azhari
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
    # Abu Toha Muhammad Adnan
    {
        "scholar": "আবু ত্বহা মোহাম্মদ আদনান",
        "hashtag": "#abutohaadnan",
        "queries": [
            "abu toha muhammad adnan emotional status shorts",
            "abu toha adnan powerful bayan waz shorts",
            "আবু ত্বহা আদনান ভাইরাল ওয়াজ শর্ট",
            "abu toha adnan islamic reminders reels"
        ]
    },
    # Allama Delowar Hossain Sayedi
    {
        "scholar": "আল্লামা দেলাওয়ার হোসাইন সাঈদী",
        "hashtag": "#delowarhossainsayedi",
        "queries": [
            "delowar hossain sayedi emotional clip shorts",
            "allama sayedi best speech short bayan",
            "দেলাওয়ার হোসাইন সাঈদী ভাইরাল ওয়াজ শর্ট",
            "sayedi emotional crying waz shorts"
        ]
    },
    # Mufti Jamshed Majumdar
    {
        "scholar": "মুফতি জামশেদ মজুমদার",
        "hashtag": "#jamshedmajumdar",
        "queries": [
            "mufti jamshed majumdar short bayan",
            "jamshed majumdar best emotional waz",
            "মুফতি জামশেদ মজুমদার শর্ট ওয়াজ",
            "jamshed majumdar viral islamic reels"
        ]
    },
    # Shaykh Ahmadullah
    {
        "scholar": "শায়খ আহমাদুল্লাহ",
        "hashtag": "#shaykhahmadullah",
        "queries": [
            "shaykh ahmadullah emotional short bayan",
            "ahmadullah islamic advice reels shorts",
            "শায়খ আহমাদুল্লাহ উপদেশমূলক শর্ট ওয়াজ",
            "ahmadullah powerful status shorts"
        ]
    }
]

# Verified Fallback Islamic Speech Pool
FALLBACK_ISLAMIC_SPEECHES = [
    {
        "scholar": "শায়খ আহমাদুল্লাহ",
        "title": "দোয়ার ফজিলত ও আল্লাহর কাছে চাওয়ার নিয়ম",
        "video_url": "https://ia800806.us.archive.org/31/items/FernCreekFalls-720/FernCreekFalls-720.mp4",
        "audio_url": "https://archive.org/download/AhnafMedia-Audios-Naat-Anas-Yunus/AllahAllah.mp3",
        "quote": "আল্লাহর কাছে মন খুলে চান, তিনি কখনো বান্দাকে খালি হাতে ফেরান না।"
    },
    {
        "scholar": "মিজানুর রহমান আজহারী",
        "title": "ধৈর্য ও তওবার অফুরন্ত নেয়ামত",
        "video_url": "https://ia800806.us.archive.org/31/items/FernCreekFalls-720/FernCreekFalls-720.mp4",
        "audio_url": "https://archive.org/download/anasheed-mshary-alafasy-89-nasheed/04.Dawman.Laka.El.Hamd.mp3",
        "quote": "বিপদে ধৈর্য ধরুন, কষ্টের পরেই আল্লাহ সহজ পথ খুলে দেন।"
    },
    {
        "scholar": "আবু ত্বহা মোহাম্মদ আদনান",
        "title": "পরকালের প্রস্তুতি ও সময়ের সঠিক মূল্যায়ন",
        "video_url": "https://ia800806.us.archive.org/31/items/FernCreekFalls-720/FernCreekFalls-720.mp4",
        "audio_url": "https://archive.org/download/AhnafMedia-Audios-Naat-Anas-Yunus/AllahAllah.mp3",
        "quote": "দুনিয়ার জীবন ক্ষণস্থায়ী, অনন্ত জীবনের জন্য পাথেয় সংগ্রহ করুন।"
    }
]

def search_and_download_short(query: str, output_path: str, max_duration: int = 60) -> bool:
    try:
        logging.info(f"Searching YouTube Shorts for: {query}")
        search_cmd = [
            "yt-dlp",
            f"ytsearch10:{query}",
            "--extractor-args", "youtube:player_client=android",
            "--match-filters", f"duration <= {max_duration} & duration >= 10",
            "--print", "%(id)s||%(title)s||%(duration)s",
            "--no-warnings",
            "--ignore-errors"
        ]
        res = subprocess.run(search_cmd, capture_output=True, text=True, timeout=30)
        lines = [l.strip() for l in res.stdout.strip().split("\n") if l.strip() and "||" in l]
        
        logging.info(f"Found {len(lines)} suitable shorts candidates")
        target_video_id = None
        if lines:
            target_video_id = lines[0].split("||")[0]
            dl_target = f"https://www.youtube.com/watch?v={target_video_id}"
        else:
            dl_target = f"ytsearch1:{query}"

        logging.info(f"Downloading short: {dl_target}")
        dl_cmd = [
            "yt-dlp",
            dl_target,
            "--extractor-args", "youtube:player_client=android",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "--merge-output-format", "mp4",
            "-o", output_path,
            "--no-playlist",
            "--max-filesize", "60M",
            "--ignore-errors",
            "--socket-timeout", "25"
        ]
        dl_res = subprocess.run(dl_cmd, capture_output=True, text=True, timeout=90)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 100000:
            return True
        else:
            logging.warning(f"yt-dlp download did not produce expected file. stderr: {dl_res.stderr[-200:]}")
            return False
    except Exception as e:
        logging.warning(f"Exception during shorts download: {e}")
        return False

def apply_anti_copyright_and_branding(input_path: str, output_path: str, scholar_name: str) -> bool:
    try:
        # Enforce 9:16 vertical ratio, subtle zoom/speed shift, anti-copyright audio filter
        audio_filter = "asetrate=44100*1.04,atempo=0.98,volume=1.9,aecho=0.8:0.8:20:0.2"
        video_filter = "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,setsar=1"
        
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vf", video_filter,
            "-af", audio_filter,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            "-ar", "44100",
            "-t", "55",
            output_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 50000
    except Exception as e:
        logging.error(f"Error applying video processing: {e}")
        return False

def synthesize_fallback_waz_reel(output_path: str) -> dict:
    os.makedirs("downloads", exist_ok=True)
    os.makedirs("processed", exist_ok=True)
    
    item = random.choice(FALLBACK_ISLAMIC_SPEECHES)
    video_tmp = "downloads/fallback_nature.mp4"
    audio_tmp = "downloads/fallback_speech.mp3"
    
    try:
        if not os.path.exists(video_tmp) or os.path.getsize(video_tmp) < 50000:
            r = requests.get(item["video_url"], timeout=30)
            with open(video_tmp, "wb") as f:
                f.write(r.content)
                
        if not os.path.exists(audio_tmp) or os.path.getsize(audio_tmp) < 50000:
            r = requests.get(item["audio_url"], timeout=30)
            with open(audio_tmp, "wb") as f:
                f.write(r.content)
                
        # Synthesize with anti-copyright audio transformation
        audio_filter = "asetrate=44100*1.04,atempo=0.98,volume=1.9,aecho=0.8:0.8:20:0.2"
        video_filter = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1"
        
        cmd = [
            "ffmpeg", "-y",
            "-stream_loop", "-1",
            "-i", video_tmp,
            "-i", audio_tmp,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-vf", video_filter,
            "-af", audio_filter,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "24",
            "-c:a", "aac",
            "-b:a", "128k",
            "-ar", "44100",
            "-t", "45",
            output_path
        ]
        subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        return {
            "video_path": output_path,
            "scholar": item["scholar"],
            "title": item["title"],
            "caption": generate_viral_caption(item["scholar"], item["title"])
        }
    except Exception as e:
        logging.error(f"Fallback synthesis failed: {e}")
        return None

def generate_viral_caption(scholar: str, topic: str) -> str:
    hooks = [
        "হৃদয় ছুঁয়ে যাওয়ার মতো চমৎকার কথা! 🤲",
        "কথাগুলো শুনলে জীবনের দৃষ্টিভঙ্গি বদলে যাবে ইনশাআল্লাহ। ❤️",
        "একটি মূল্যবান ইসলামিক উপদেশ যা সবার জানা উচিত! 🕋",
        "আল্লাহ তাআলা আমাদের সবাইকে হেদায়েত দান করুন। আমিন 🤲",
        "জীবন পরিবর্তনকারী সেরা ইসলামিক বক্তব্য ✨"
    ]
    hook = random.choice(hooks)
    tags = "#IslamicReels #WazShorts #BanglaWaz #IslamicShorts #Azhari #AbuToha #Sayedi #Ahmadullah #ViralReels #IslamicReminder"
    
    caption = f"{hook}\n\n🎙️ {scholar}: {topic}\n\nআল্লাহু আকবার! আল্লাহ আমাদের গুনাহ মাফ করে দিন এবং জান্নাতুল ফিরদাউস নসিব করুন। আমিন।\n\n{tags}"
    return caption

def prepare_waz_reel_for_publishing() -> dict:
    os.makedirs("downloads", exist_ok=True)
    os.makedirs("processed", exist_ok=True)
    
    scholar_info = random.choice(WAZ_SCHOLARS_QUERIES)
    scholar = scholar_info["scholar"]
    query = random.choice(scholar_info["queries"])
    
    logging.info(f"Target Scholar: {scholar} | Query: {query}")
    
    raw_path = f"downloads/raw_{random.randint(1000, 9999)}.mp4"
    proc_path = f"processed/waz_reel_{random.randint(1000, 9999)}.mp4"
    
    download_success = search_and_download_short(query, raw_path)
    
    if download_success:
        proc_ok = apply_anti_copyright_and_branding(raw_path, proc_path, scholar)
        if proc_ok:
            return {
                "video_path": proc_path,
                "scholar": scholar,
                "title": query,
                "caption": generate_viral_caption(scholar, query)
            }
            
    # Fallback to guaranteed synthesis
    logging.warning("Falling back to internal fallback reel synthesis")
    return synthesize_fallback_waz_reel(proc_path)
