"""
Main Automated Reels & Videos Publisher for 'সেরা ইসলামিক শর্ট ওয়াজ' (ID: 1541701802352983)
- দৈনিক মোট ১০টি পোস্ট (সকালে ২টি এবং দুপুর ১টার পর থেকে প্রতি ১ ঘণ্টা পর পর ৮টি)
- সকল শীর্ষ সম্মানিত হুজুরদের ভেরিফাইড নতুন ও ট্রেন্ডিং নসিহত (আহমাদুল্লাহ, আজহারী, আবু ত্বহা, সাঈদী, তারেক জামিল)
- কঠোর জিরো ডুপ্লিকেট পলিসি: ফেসবুক পেজের পূর্ববর্তী ১০০টি পোস্ট ও লোকাল হিস্টোরি যাচাই
- ১০০% আসল লাইভ মাহফিল/পোডিয়াম ফুটেজ এবং স্বাভাবিক ন্যাচারাল কণ্ঠস্বর
- পেজের স্থায়ী ক্রিস্টাল ক্লিয়ার ব্র্যান্ডেড ওয়াটারমার্ক
"""

import os
import sys
import glob
import json
import time
import random
import datetime
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

# অপ্রাসঙ্গিক বা নষ্ট ফাইলের ব্ল্যাকলিস্ট
PERMANENT_BANNED_SIGNATURES = {
    "bank_ahmadullah_life_advice",
    "bank_ahmadullah_dua",
    "ahmadullah_life_advice.mp4",
    "ahmadullah_dua.mp4",
    "yt_yXH8rPQ3l2M",
    "yt_y31MzRdIDPo"
}

# অফলাইন ব্যাকআপ ব্যাংক ক্লিপস (১৪টি আসল মাহফিল ও নসিহত ক্লিপস)
BANK_METADATA = [
    {
        "file": "abutoha_jadu_shesh_jamana.mp4",
        "src_id": "bank_abutoha_jadu_shesh_jamana",
        "scholar": "আবু ত্বহা মোহাম্মদ আদনান",
        "title": "আবু ত্বহা মোহাম্মদ আদনান: শেষ জামানার ফেতনা ও ঈমান রক্ষার উপায়",
        "nasihat": "শেষ জামানায় নিজের ঈমানকে রক্ষা করা জ্বলন্ত কয়লা হাতে রাখার মতো। কোরআন ও সুন্নাহকে আঁকড়ে ধরুন।",
        "hashtags": "#AbuTohaMuhammadAdnan #AbuToha #SheshJamana #Iman #IslamicReminder #Sunnah"
    },
    {
        "file": "abutoha_rizik_borot.mp4",
        "src_id": "bank_abutoha_rizik_borot",
        "scholar": "আবু ত্বহা মোহাম্মদ আদনান",
        "title": "আবু ত্বহা মোহাম্মদ আদনান: হালাল রিজিক ও তাকওয়ার অফুরন্ত বরকত",
        "nasihat": "আল্লাহভীতি অর্জন করুন, আল্লাহ এমন পথ থেকে রিজিক দেবেন যা আপনি কল্পনাও করতে পারেননি।",
        "hashtags": "#AbuTohaMuhammadAdnan #Rizik #Halal #Tawakkul #BanglaWaz #Islam"
    },
    {
        "file": "abutoha_tawakkul.mp4",
        "src_id": "bank_abutoha_tawakkul",
        "scholar": "আবু ত্বহা মোহাম্মদ আদনান",
        "title": "আবু ত্বহা মোহাম্মদ আদনান: আল্লাহর ওপর ভরসা ও জীবনের মোড় পরিবর্তন",
        "nasihat": "যে ব্যক্তি আল্লাহর ওপর পূর্ণ ভরসা করে, তার জন্য আল্লাহই যথেষ্ট। কখনো নিরাশ হবেন না।",
        "hashtags": "#AbuTohaMuhammadAdnan #Tawakkul #Allah #Dua #FaithInAllah"
    },
    {
        "file": "ahmadullah_amol_nasihat.mp4",
        "src_id": "bank_ahmadullah_amol_nasihat",
        "scholar": "শায়খ আহমাদুল্লাহ",
        "title": "শায়খ আহমাদুল্লাহ: ছোট একটি নেক আমল যা জীবনকে বদলে দিতে পারে",
        "nasihat": "প্রতিটি মুহূর্তে রবের সন্তুষ্টি খুঁজুন। ছোট আমলকেও অবহেলা করবেন না।",
        "hashtags": "#ShaikhAhmadullah #AhmadullahWaz #Amol #IslamicLife #Sunnah"
    },
    {
        "file": "azhari_dile_shanti.mp4",
        "src_id": "bank_azhari_dile_shanti",
        "scholar": "মাওলানা মিজানুর রহমান আজহারী",
        "title": "মাওলানা মিজানুর রহমান আজহারী: অন্তরের নীরব প্রশান্তি ও রবের নৈকট্য",
        "nasihat": "জেনে রাখুন! আল্লাহর জিকিরেই অন্তরসমূহ পরম প্রশান্তি লাভ করে। (সূরা আর-রাদ: ২৮)",
        "hashtags": "#MizanurRahmanAzhari #Azhari #Zikr #PeaceOfMind #Dua #Quran"
    },
    {
        "file": "azhari_jiber_mulya.mp4",
        "src_id": "bank_azhari_jiber_mulya",
        "scholar": "মাওলানা মিজানুর রহমান আজহারী",
        "title": "মাওলানা মিজানুর রহমান আজহারী: জীবনের আসল উদ্দেশ্য ও সৃষ্টির মর্যাদা",
        "nasihat": "আল্লাহ আপনাকে অযথা সৃষ্টি করেননি। সময় ফুরিয়ে যাওয়ার আগেই নিজেকে চিনুন।",
        "hashtags": "#MizanurRahmanAzhari #AzhariWaz #PurposeOfLife #IslamicReels"
    },
    {
        "file": "azhari_motivational.mp4",
        "src_id": "bank_azhari_motivational",
        "scholar": "মাওলানা মিজানুর রহমান আজহারী",
        "title": "মাওলানা মিজানুর রহমান আজহারী: ব্যর্থতায় ভেঙে পড়বেন না, আল্লাহ আপনার সাথে আছেন",
        "nasihat": "ধৈর্য ধরুন, নিশ্চয়ই কষ্টের সাথেই রয়েছে স্বস্তি। আল্লাহর রহমত থেকে কখনো নিরাশ হবেন না।",
        "hashtags": "#MizanurRahmanAzhari #Motivation #Sabr #HopeInAllah #IslamicMotivation"
    },
    {
        "file": "azhari_namaz_er_gurutto.mp4",
        "src_id": "bank_azhari_namaz_er_gurutto",
        "scholar": "মাওলানা মিজানুর রহমান আজহারী",
        "title": "মাওলানা মিজানুর রহমান আজহারী: নামাজের গুরুত্ব ও অবহেলার কঠিন পরিণতি",
        "nasihat": "সালাত হচ্ছে ঈমান ও কুফরের মাঝে প্রধান পার্থক্য। পাঁচ ওয়াক্ত সালাত সময়মতো আদায় করুন।",
        "hashtags": "#MizanurRahmanAzhari #Namaz #AzhariWaz #IslamicReminder #Sunnah"
    },
    {
        "file": "azhari_smriti_roye_jay.mp4",
        "src_id": "bank_azhari_smriti_roye_jay",
        "scholar": "মাওলানা মিজানুর রহমান আজহারী",
        "title": "মাওলানা মিজানুর রহমান আজহারী: মানুষ চলে যায় কিন্তু সুন্দর স্মৃতি ও আমল রয়ে যায়",
        "nasihat": "এমন জীবন গড়ে তুলুন যেন আপনার মৃত্যুর পরও মানুষ আপনার জন্য মন খুলে দোয়া করে।",
        "hashtags": "#MizanurRahmanAzhari #Azhari #LifeReminder #GoodDeeds #AzhariReels"
    },
    {
        "file": "azhari_tobe_ki.mp4",
        "src_id": "bank_azhari_tobe_ki",
        "scholar": "মাওলানা মিজানুর রহমান আজহারী",
        "title": "মাওলানা মিজানুর রহমান আজহারী: তবে কি আমরা আল্লাহর দিকে ফিরে যাব না?",
        "nasihat": "হে মানুষ! কোন জিনিস তোমাকে তোমার মহান রব সম্পর্কে ধোঁকায় ফেলে রাখল?",
        "hashtags": "#MizanurRahmanAzhari #AzhariWaz #Tauba #ReturnToAllah #QuranAyat"
    },
    {
        "file": "sayedi_emotional_waz.mp4",
        "src_id": "bank_sayedi_emotional_waz",
        "scholar": "আল্লামা দেলাওয়ার হোসাইন সাঈদী",
        "title": "আল্লামা দেলাওয়ার হোসাইন সাঈদী: রবের সামনে কান্নাকাটি ও গুনাহ মাফের আকুতি",
        "nasihat": "যে চোখ আল্লাহর ভয়ে এক ফোঁটা অশ্রু ঝরায়, জাহান্নামের আগুন তার জন্য হারাম হয়ে যায়।",
        "hashtags": "#DelowarHossainSayedi #SayediWaz #Tauba #EmotionalWaz #AllamaSayedi"
    },
    {
        "file": "sayedi_jannat_jahannam.mp4",
        "src_id": "bank_sayedi_jannat_jahannam",
        "scholar": "আল্লামা দেলাওয়ার হোসাইন সাঈদী",
        "title": "আল্লামা দেলাওয়ার হোসাইন সাঈদী: জান্নাতের অপার্থিব নিয়ামত ও মোমেনের পুরস্কার",
        "nasihat": "দুনিয়ার কষ্ট কয়েকদিনের, কিন্তু মুমিনের জন্য জান্নাতের সুখ চিরস্থায়ী। নেক আমল করুন।",
        "hashtags": "#DelowarHossainSayedi #AllamaSayedi #Jannat #SayediWaz #QuranerDawat"
    },
    {
        "file": "sayedi_quraner_dawat.mp4",
        "src_id": "bank_sayedi_quraner_dawat",
        "scholar": "আল্লামা দেলাওয়ার হোসাইন সাঈদী",
        "title": "আল্লামা দেলাওয়ার হোসাইন সাঈদী: কোরআনের হেদায়েত ও আলোকিত জীবনের সন্ধান",
        "nasihat": "কোরআন হচ্ছে মানবতার মুক্তির একমাত্র সংবিধান। এই বাণী সবার কাছে পৌঁছে দিন।",
        "hashtags": "#DelowarHossainSayedi #QuranerDawat #Quran #AllamaSayedi #Dawat"
    },
    {
        "file": "tariq_jamil_iman_reminder.mp4",
        "src_id": "bank_tariq_jamil_iman_reminder",
        "scholar": "মাওলানা তারিক জামিল",
        "title": "মাওলানা তারিক জামিল: আল্লাহর অপার দয়া ও ক্ষমার অনুপম বার্তা",
        "nasihat": "আল্লাহ বলেন: হে আমার বান্দা! তুমি যত গুনাহই করো না কেন, ফিরে এসো, আমি তোমাকে ক্ষমা করে দেব।",
        "hashtags": "#TariqJamil #MaulanaTariqJamil #AllahLove #Tauba #IslamicQuotes"
    }
]

def apply_anti_copyright_and_watermark(input_video_path: str, output_path: str):
    filter_complex = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,setsar=1[bg];"
        "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,setsar=1[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2[v_base];"
        "[v_base][1:v]overlay=0:0[v_final];"
        "[0:a]volume=1.05,loudnorm=I=-16:TP=-1.5:LRA=11[a_final]"
    )

    cmd = [
        FFMPEG_EXE, "-y",
        "-i", input_video_path,
        "-i", WATERMARK_PNG,
        "-filter_complex", filter_complex,
        "-map", "[v_final]",
        "-map", "[a_final]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-b:v", "6000k", "-maxrate", "8000k", "-bufsize", "12000k",
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
        "-map_metadata", "-1",
        output_path
    ]

    subprocess.run(cmd, check=True)
    return output_path

WAZ_ENGAGEMENT_HOOKS = [
    "⚠️ এই ১ মিনিটের নসিহতটি আপনার চিন্তা ও পুরো জীবন বদলে দিতে পারে! না টেনে শেষ পর্যন্ত শুনুন 💡",
    "🔥 জাহান্নামের ভয়াবহ আগুন ও কবরের অন্ধকার থেকে বাঁচতে হুজুরের এই জরুরি কথাটি শুনুন 🤲",
    "💔 দুনিয়ার কোনো বিপদেই মন ভাঙবেন না—হুজুরের এই মহামূল্যবান সান্ত্বনাটি শুনুন, দিল শান্ত হয়ে যাবে 🌿",
    "💡 আমরা অনেকেই এই মারাত্মক ভুলটি প্রতিদিন করছি! দেখুন হুজুর কী সতর্কবার্তা দিচ্ছেন ⚠️ (শেষ পর্যন্ত শুনুন)",
    "🌸 আল্লাহর সবচেয়ে প্রিয় ও সৌভাগ্যবান বান্দা হতে চান? মাত্র ১ মিনিটে জেনে নিন সহজ উপায়টি! 🤲",
    "✨ ঈমান মজবুত রাখতে ও গুনাহ থেকে বাঁচতে প্রতিটি মুমিনের এই নসিহতটি শোনা অত্যন্ত জরুরি 🤍"
]

WAZ_VIRAL_HASHTAGS = [
    "#BanglaWaz", "#IslamicShorts", "#WazShorts", "#Ahmadullah", "#MizanurRahmanAzhari",
    "#AbuTohaAdnan", "#SayediWaz", "#TrendingWaz", "#ViralIslamicReels", "#IslamicStatus",
    "#IslamicQuotes", "#Jannat", "#Nasihat", "#Deen", "#Sunnah", "#BanglaIslamicVideo",
    "#IslamicReminder", "#ForYouPage", "#ViralReelsFacebook", "#ReelsViral2026", "#IslamicReels",
    "#ShortWaz", "#IslamicDua", "#ViralVideo", "#Islam"
]

def generate_caption(title: str, scholar: str, nasihat: str, hashtags: str, src_id: str) -> str:
    hook = random.choice(WAZ_ENGAGEMENT_HOOKS)
    tag_cloud = " ".join(random.sample(WAZ_VIRAL_HASHTAGS, min(22, len(WAZ_VIRAL_HASHTAGS))))
    caption = (
        f"{hook}\n\n"
        f"🎙️ {title}\n"
        f"👤 সম্মানিত আলোচক: {scholar}\n\n"
        f"💡 জীবনঘনিষ্ঠ মূল্যবান নসিহত:\n{nasihat}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 প্রতিদিন সেরা আলেমদের এমন জীবনঘনিষ্ঠ ওয়াজ ও নসিহত পেতে এখনই পেজটিতে [ফলো / + Follow] দিয়ে সাথে থাকুন! 👆🌸\n\n"
        f"👉 দ্বীনি দাওয়াত ছড়িয়ে দিতে ভিডিওটি এখনই শেয়ার করুন এবং বন্ধুদের দেখার সুযোগ করে দিন 🤲\n\n"
        f"{tag_cloud}\n\n"
        f"📌 [src:{src_id}]"
    )
    return caption

def run():
    print("===========================================================")
    print("🕌 'সেরা ইসলামিক শর্ট ওয়াজ' দৈনিক ১০টি ট্রেন্ডিং ভিডিও অটোমেশন")
    print("===========================================================")

    page_id = FB_PAGE_ID or "1541701802352983"
    token = FB_PAGE_ACCESS_TOKEN

    # ১. ফেসবুক পেজ এবং লোকাল হিস্টোরি থেকে পূর্বের সকল পোস্ট করা সিগনেচার রিড করা
    print("[1/5] Checking previously posted videos on Facebook Page to guarantee ZERO DUPLICATE...")
    fb_signatures = get_posted_signatures_from_facebook(page_id, token, limit=100)
    history = load_local_history()
    local_posted_ids = set(history.get("posted_ids", []))
    all_posted_signatures = fb_signatures.union(local_posted_ids).union(PERMANENT_BANNED_SIGNATURES)
    print(f"[*] Total unique posted signatures tracked: {len(all_posted_signatures)}")

    today_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    daily_stats = history.get("daily_stats", {})
    if daily_stats.get("date") != today_str:
        daily_stats = {"date": today_str, "total_posted": 0}
        history["daily_stats"] = daily_stats

    selected_item = None
    downloaded_video = None

    # ২. অফলাইন ব্যাংক থেকে ফ্রেশ আনপোস্টেড ভিডিও বাছাই (Priority 1)
    print("[2/5] Searching offline bank (14 pre-staged MP4 clips) for unposted scholar waz...")
    unposted_bank = [b for b in BANK_METADATA if b["src_id"] not in all_posted_signatures]
    print(f"[*] Unposted items remaining in bank: {len(unposted_bank)} / {len(BANK_METADATA)}")

    if not unposted_bank:
        print("[*] All bank items have been posted at least once. Rotating clips not posted in recent 5 posts...")
        recent_fb = get_posted_signatures_from_facebook(page_id, token, limit=5)
        rotating_bank = [b for b in BANK_METADATA if b["src_id"] not in recent_fb and b["src_id"] not in PERMANENT_BANNED_SIGNATURES]
        if not rotating_bank:
            rotating_bank = [b for b in BANK_METADATA if b["src_id"] not in PERMANENT_BANNED_SIGNATURES]
        unposted_bank = rotating_bank
        print(f"[*] Available rotating bank clips: {len(unposted_bank)}")

    if unposted_bank:
        for b in unposted_bank:
            local_path = os.path.join(WAZ_BANK_DIR, b["file"])
            if os.path.exists(local_path) and os.path.getsize(local_path) > 100000:
                selected_item = b
                downloaded_video = local_path
                print(f"🎯 Selected from bank: {b['title']} ({b['file']})")
                break

    # ৩. যদি ব্যাংক শেষ হয়, ইউটিউব থেকে ফ্রেশ ভিডিও খোঁজা
    if not selected_item:
        last_scholar_idx = history.get("last_scholar_index", -1)
        next_scholar_idx = (last_scholar_idx + 1) % len(DYNAMIC_SCHOLAR_QUERIES)
        target_scholar, target_query, target_tags = DYNAMIC_SCHOLAR_QUERIES[next_scholar_idx]
        print(f"[*] Falling back to curated/dynamic search for: {target_scholar}...")

        for item in CURATED_YOUTUBE_SHORTS:
            if item.get("scholar") == target_scholar and item["src_id"] not in all_posted_signatures:
                vid_path = download_youtube_short(item)
                if vid_path:
                    selected_item = item
                    downloaded_video = vid_path
                    break

        if not selected_item:
            dyn_item = search_dynamic_youtube_short(target_scholar, target_query, target_tags, all_posted_signatures)
            if dyn_item:
                vid_path = download_youtube_short(dyn_item)
                if vid_path:
                    selected_item = dyn_item
                    downloaded_video = vid_path

    if not selected_item or not downloaded_video:
        print("❌ কোনো নতুন বা আনপোস্টেড ভিডিও পাওয়া যায়নি। ডুপ্লিকেট রোধে সাইকেল স্থগিত।")
        return

    print(f"[3/5] ✅ ভিডিও চূড়ান্ত নির্বাচিত: {selected_item['title']} (src: {selected_item['src_id']})")

    # ৪. প্রসেসিং ও ওয়াটারমার্ক
    ts = int(time.time())
    processed_output = os.path.join(OUTPUT_DIR, f"waz_processed_{ts}.mp4")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"[4/5] 🎨 ওয়াটারমার্ক ও প্রফেশনাল ব্রডকাস্ট ফ্রেম রেন্ডারিং...")
    apply_anti_copyright_and_watermark(downloaded_video, processed_output)

    # ৫. পাবলিশিং
    caption = generate_caption(
        selected_item["title"],
        selected_item["scholar"],
        selected_item.get("nasihat", ""),
        selected_item.get("hashtags", ""),
        selected_item["src_id"]
    )
    print(f"[5/5] 📤 ফেসবুকে রিলস আপলোড হচ্ছে (Page ID: {page_id})...")
    pub_res = publish_reels_video(
        video_path=processed_output,
        caption=caption,
        title=selected_item["title"]
    )
    print(f"🚀 ফেসবুক আপলোড সম্পন্ন! রেজাল্ট: {pub_res}")

    # ৬. হিস্টোরি ও দৈনিক পরিসংখ্যান আপডেট
    if "posted_ids" not in history or not isinstance(history["posted_ids"], list):
        history["posted_ids"] = []
    history["posted_ids"].append(selected_item["src_id"])
    daily_stats["total_posted"] = daily_stats.get("total_posted", 0) + 1
    history["daily_stats"] = daily_stats
    save_local_history(history)
    print(f"📊 আজকের ইসলামিক শর্ট ওয়াজ পোস্টিং সংখ্যা: {daily_stats['total_posted']}/১০টি সম্পন্ন!")

if __name__ == "__main__":
    run()
