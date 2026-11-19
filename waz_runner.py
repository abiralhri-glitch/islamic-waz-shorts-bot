"""
Main Automated Reels & Videos Publisher for 'সেরা ইসলামিক শর্ট ওয়াজ'
- দৈনিক মোট ১০টি পোস্ট (সকালে ২টি এবং দুপুর ১টার পর থেকে প্রতি ১ ঘণ্টা পর পর ৮টি)
- সকল শীর্ষ সম্মানিত হুজুরদের ভেরিফাইড নতুন ও ট্রেন্ডিং নসিহত (আহমাদুল্লাহ, আজহারী, আবু ত্বহা, সাঈদী, আমির হামজা, তারেক জামিল, আব্দুল্লাহ জাহাঙ্গীর প্রমুখ)
- কঠোর জিরো ডুপ্লিকেট পলিসি: ফেসবুক পেজের পূর্ববর্তী ১০০টি পোস্ট ও লোকাল হিস্টোরি যাচাই
- ১০০% আসল লাইভ পোডিয়াম/স্টেজ ফুটেজ এবং স্বাভাবিক ন্যাচারাল কণ্ঠস্বর
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

# অপরিবর্তনযোগ্য স্থায়ী ব্ল্যাকলিস্ট
PERMANENT_BANNED_SIGNATURES = {
    "bank_ahmadullah_life_advice",
    "bank_ahmadullah_dua",
    "ahmadullah_life_advice.mp4",
    "ahmadullah_dua.mp4",
    "yt_yXH8rPQ3l2M",
    "yt_y31MzRdIDPo",
    "জীনরা খাবার কোথায় পায়",
    "দোয়ার ফজিলত ও রবকে ডাকার গোপন রহস্য",
    "উত্তম চরিত্র ও সুন্দর পারিবারিক জীবনের শিক্ষা"
}

# অফলাইন ব্যাকআপ ব্যাংক ক্লিপস (আজহারী, আবু ত্বহা, সাঈদী ও আমির হামজার ফ্রেশ ক্লিপস)
BANK_METADATA = [
    {
        "file": "azhari_namaz_er_gurutto.mp4",
        "src_id": "bank_azhari_namaz_er_gurutto",
        "scholar": "মাওলানা মিজানুর রহমান আজহারী",
        "title": "মাওলানা মিজানুর রহমান আজহারী: নামাজের গুরুত্ব ও অবহেলার কঠিন পরিণতি",
        "nasihat": "সালাত হচ্ছে ঈমান ও কুফরের মাঝে প্রধান পার্থক্য। পাঁচ ওয়াক্ত সালাত সময়মতো আদায় করুন।",
        "hashtags": "#MizanurRahmanAzhari #Namaz #AzhariWaz #IslamicReminder #Sunnah"
    },
    {
        "file": "azhari_dile_shanti.mp4",
        "src_id": "bank_azhari_dile_shanti",
        "scholar": "মাওলানা মিজানুর রহমান আজহারী",
        "title": "মাওলানা মিজানুর রহমান আজহারী: অন্তরের নীরব শান্তি ও রবের জিকির",
        "nasihat": "জেনে রাখুন, একমাত্র আল্লাহর জিকিরেই রয়েছে অন্তরের প্রকৃত পরম শান্তি।",
        "hashtags": "#MizanurRahmanAzhari #Zikr #PeaceOfMind #AzhariShorts #ViralWaz"
    },
    {
        "file": "abutoha_rizik_borot.mp4",
        "src_id": "bank_abutoha_rizik_borot",
        "scholar": "আবু ত্বহা মোহাম্মদ আদনান",
        "title": "আবু ত্বহা মোহাম্মদ আদনান: রিজিকের অফুরন্ত বরকত ও হালাল উপার্জন",
        "nasihat": "হারাম থেকে নিজেকে বাঁচিয়ে রাখুন, অল্প হলেও হালাল রিজিকের মধ্যে আল্লাহ বরকত দেন।",
        "hashtags": "#AbuTohaAdnan #Rizik #HalalEarning #AbuTohaWaz #Tawakkul"
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
        "file": "amir_hamza_pother_alo.mp4",
        "src_id": "bank_amir_hamza_pother_alo",
        "scholar": "মুফতি আমির হামজা",
        "title": "মুফতি আমির হামজা: জীবনের বাঁকে বাঁকে হেদায়েত ও পথের আলো",
        "nasihat": "আল্লাহর দিকে এক কদম বাড়ালে তিনি আপনার দিকে দশ কদম এগিয়ে আসবেন।",
        "hashtags": "#AmirHamza #AmirHamzaWaz #Hedayet #BanglaWaz #Sunnah"
    },
    {
        "file": "ahmadullah_amol_nasihat.mp4",
        "src_id": "bank_ahmadullah_amol_nasihat",
        "scholar": "শায়খ আহমাদুল্লাহ",
        "title": "শায়খ আহমাদুল্লাহ: প্রতিদিন করার মত ছোট ছোট কিছু আমল ও ফজিলত",
        "nasihat": "দৈনন্দিন ছোট ছোট নেক আমলই আখিরাতে আপনার মিজান ভারী করে দিবে। নিয়মিত আমল করুন।",
        "hashtags": "#ShaykhAhmadullah #AhmadullahWaz #IslamicReminder #Sunnah #DailyAmol"
    },
    {
        "file": "azhari_jiber_mulya.mp4",
        "src_id": "bank_azhari_jiber_mulya",
        "scholar": "মাওলানা মিজানুর রহমান আজহারী",
        "title": "মাওলানা মিজানুর রহমান আজহারী: জীবনের শ্রেষ্ঠ মূল্যায়ন ও সময় সচেতনতা",
        "nasihat": "প্রতিটি নিঃশ্বাস এক একটি মূল্যবান নেয়ামত। দুনিয়ার মোহে পড়ে আখিরাত ভুলে যাবেন না।",
        "hashtags": "#MizanurRahmanAzhari #AzhariWaz #IslamicReminder #WazShorts #BanglaWaz"
    },
    {
        "file": "azhari_smriti_roye_jay.mp4",
        "src_id": "bank_azhari_smriti_roye_jay",
        "scholar": "মাওলানা মিজানুর রহমান আজহারী",
        "title": "মাওলানা মিজানুর রহমান আজহারী: মানুষ চলে যায় কিন্তু নেক আমল রয়ে যায়",
        "nasihat": "এমন কিছু নেক আমল রেখে যান যা কবরে আপনার আলোর কারণ হবে।",
        "hashtags": "#MizanurRahmanAzhari #AzhariShorts #IslamicBayan #HeartTouching"
    },
    {
        "file": "azhari_motivational.mp4",
        "src_id": "bank_azhari_motivational",
        "scholar": "মাওলানা মিজানুর রহমান আজহারী",
        "title": "মাওলানা মিজানুর রহমান আজহারী: হতাশ হবেন না, মহান রব আপনার সাথে আছেন",
        "nasihat": "সব দরজা বন্ধ হয়ে গেলেও রবের রহমতের দরজা সর্বদা উন্মুক্ত।",
        "hashtags": "#MizanurRahmanAzhari #MotivationalWaz #IslamicReminder #Tawakkul"
    },
    {
        "file": "azhari_tobe_ki.mp4",
        "src_id": "bank_azhari_tobe_ki",
        "scholar": "মাওলানা মিজানুর রহমান আজহারী",
        "title": "মাওলানা মিজানুর রহমান আজহারী: পিতামাতার মর্যাদা ও তাদের প্রতি কর্তব্য",
        "nasihat": "পিতামাতার সন্তুষ্টিতেই মহান আল্লাহর সন্তুষ্টি। তাদের সেবা করুন।",
        "hashtags": "#ParentsInIslam #AzhariWaz #IslamicFamily #MizanurRahmanAzhari"
    },
    {
        "file": "abutoha_jadu_shesh_jamana.mp4",
        "src_id": "bank_abutoha_jadu_shesh_jamana",
        "scholar": "আবু ত্বহা মোহাম্মদ আদনান",
        "title": "আবু ত্বহা মোহাম্মদ আদনান: শেষ জামানায় ঈমান রক্ষা ও আত্মরক্ষা",
        "nasihat": "সকাল ও সন্ধ্যার মাসনুন দোয়া এবং সূরা আল-কাহাফ নিয়মিত তিলাওয়াত করুন।",
        "hashtags": "#AbuTohaAdnan #AbuTohaWaz #SheshJamana #Eman #IslamicReels"
    },
    {
        "file": "abutoha_tawakkul.mp4",
        "src_id": "bank_abutoha_tawakkul",
        "scholar": "আবু ত্বহা মোহাম্মদ আদনান",
        "title": "আবু ত্বহা মোহাম্মদ আদনান: টেনশন করো না, আল্লাহ অবশ্যই সাথে আছেন",
        "nasihat": "বিপদাপদে আল্লাহর ওপর পূর্ণ তাওয়াক্কুল রাখুন, নিশ্চয়ই তিনি ধৈর্যশীলদের সাহায্য করেন।",
        "hashtags": "#AbuTohaAdnan #AbuTohaWaz #Tawakkul #PeaceOfMind #Eman"
    },
    {
        "file": "sayedi_emotional_waz.mp4",
        "src_id": "bank_sayedi_emotional_waz",
        "scholar": "আল্লামা দেলাওয়ার হোসাইন সাঈদী",
        "title": "আল্লামা দেলাওয়ার হোসাইন সাঈদী: কালজয়ী আবেগঘন নসিহত ও তওবার আহ্বান",
        "nasihat": "নিশ্চয়ই মহান আল্লাহ তওবাকারীদের অত্যন্ত ভালোবাসেন।",
        "hashtags": "#DelowarHossainSayedi #AllamaSayedi #SayediWaz #QuranerDawat"
    },
    {
        "file": "sayedi_quraner_dawat.mp4",
        "src_id": "bank_sayedi_quraner_dawat",
        "scholar": "আল্লামা দেলাওয়ার হোসাইন সাঈদী",
        "title": "আল্লামা দেলাওয়ার হোসাইন সাঈদী: কোরআনের আলো ও হেদায়েতের ডাক",
        "nasihat": "কোরআনের ছায়াতলে ফিরে আসুন, সেখানেই রয়েছে দুনিয়া ও আখিরাতের চূড়ান্ত মুক্তি।",
        "hashtags": "#AllamaSayedi #SayediShorts #HeartTouching #Tawbah #Sunnah"
    },
    {
        "file": "tariq_jamil_iman_reminder.mp4",
        "src_id": "bank_tariq_jamil_iman_reminder",
        "scholar": "মাওলানা তারেক জামিল",
        "title": "মাওলানা তারেক জামিল: অন্তরের প্রশান্তি ও আল্লাহর অসীম রহমত",
        "nasihat": "কঠিন বিপদেও হতাশ হবেন না, আল্লাহ তার বান্দার অতি নিকটে।",
        "hashtags": "#MaulanaTariqJamil #TariqJamilBangla #HeartTouchingWaz #PeaceOfMind"
    }
]

def apply_anti_copyright_and_watermark(input_video_path: str, output_path: str):
    """
    ফুল ভিডিও ক্লিয়ার ও সম্পূর্ণ দৃশ্যমান রাখার জন্য ১০৮০p ডুয়াল-লেয়ার স্মার্ট ফ্রেইমিং:
    - নো ক্রপিং: হুজুরের মুখ, হাত, অঙ্গভঙ্গি ও সাবটাইটেল ১০০% সম্পূর্ণ দৃশ্যমান থাকবে
    - ব্যাকগ্রাউন্ডে মসৃণ সিনেমাটিক ব্লার এবং মাঝখানে ফুল অরজিনাল ফ্রেম
    - ক্রিস্টাল ক্লিয়ার ১০৮০x১৯২০ আল্ট্রা-এইচডি কোয়ালিটি (CRF 18, 6000k Bitrate)
    - ১০০% স্বাভাবিক ন্যাচারাল ক্রিস্টাল ক্লিয়ার লাউডনরম অডিও সাউন্ড
    """
    filter_complex = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,setsar=1[bg];"
        "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,setsar=1[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2[v_base];"
        "[v_base][1:v]overlay=0:0[v_final];"
        "[0:a]volume=1.1,loudnorm=I=-16:TP=-1.5:LRA=11[a_final]"
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

    # দৈনিক পরিসংখ্যান ট্র্যাকিং
    today_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    daily_stats = history.get("daily_stats", {})
    if daily_stats.get("date") != today_str:
        daily_stats = {"date": today_str, "total_posted": 0}
        history["daily_stats"] = daily_stats

    # ২. পরবর্তী হুজুর/স্কলার রোটেশন নির্বাচন (সকল হুজুরদের সমান অনুপাত নিশ্চিত করতে)
    last_scholar_idx = history.get("last_scholar_index", -1)
    next_scholar_idx = (last_scholar_idx + 1) % len(DYNAMIC_SCHOLAR_QUERIES)
    target_scholar, target_query, target_tags = DYNAMIC_SCHOLAR_QUERIES[next_scholar_idx]
    print(f"[2/5] 🎯 বর্তমান স্লটের নির্বাচিত সম্মানিত স্কলার: {target_scholar} (#{next_scholar_idx+1}/{len(DYNAMIC_SCHOLAR_QUERIES)})")

    selected_item = None
    downloaded_video = None

    # ৩. সোর্স নির্বাচন: প্রথমে কিউরেটেড ইউটিউব শর্টস থেকে ওই স্কলারের নতুন আনপোস্টেড ভিডিও খোঁজা
    for item in CURATED_YOUTUBE_SHORTS:
        if item.get("scholar") == target_scholar and item["src_id"] not in all_posted_signatures:
            vid_path = download_youtube_short(item)
            if vid_path:
                selected_item = item
                downloaded_video = vid_path
                break

    # ৪. কিউরেটেড শেষ হলে ডায়নামিক ইউটিউব শর্টস সার্চ (সর্বাধিক নতুন ও ট্রেন্ডিং)
    if not selected_item:
        dyn_item = search_dynamic_youtube_short(target_scholar, target_query, target_tags, all_posted_signatures)
        if dyn_item:
            vid_path = download_youtube_short(dyn_item)
            if vid_path:
                selected_item = dyn_item
                downloaded_video = vid_path

    # ৫. ইউটিউব ডাউনলোডে ব্যর্থ হলে সংরক্ষিত ব্যাংক থেকে বাছাই
    if not selected_item:
        print(f"⚠️ {target_scholar}-এর কোনো নতুন ইউটিউব ভিডিও পাওয়া যায়নি। অফলাইন ব্যাংক অনুসন্ধান...")
        for b in BANK_METADATA:
            if b.get("scholar") == target_scholar and b["src_id"] not in all_posted_signatures:
                local_path = os.path.join(WAZ_BANK_DIR, b["file"])
                if os.path.exists(local_path) and os.path.getsize(local_path) > 100000:
                    selected_item = b
                    downloaded_video = local_path
                    break

    # ফলব্যাক: ব্যাংকের যেকোনো অবশিষ্ট আনপোস্টেড ভিডিও
    if not selected_item:
        for b in BANK_METADATA:
            if b["src_id"] not in all_posted_signatures:
                local_path = os.path.join(WAZ_BANK_DIR, b["file"])
                if os.path.exists(local_path) and os.path.getsize(local_path) > 100000:
                    selected_item = b
                    downloaded_video = local_path
                    break

    if not selected_item or not downloaded_video:
        print("❌ কোনো নতুন বা আনপোস্টেড ভিডিও পাওয়া যায়নি। ডুপ্লিকেট রোধে সাইকেল স্থগিত।")
        return

    print(f"[3/5] ✅ ভিডিও চূড়ান্ত নির্বাচিত: {selected_item['title']} (src: {selected_item['src_id']})")

    # ৬. প্রসেসিং ও ওয়াটারমার্ক
    ts = int(time.time())
    processed_output = os.path.join(OUTPUT_DIR, f"waz_processed_{ts}.mp4")
    print(f"[4/5] 🎨 ওয়াটারমার্ক ও প্রফেশনাল ব্রডকাস্ট ফ্রেম রেন্ডারিং...")
    apply_anti_copyright_and_watermark(downloaded_video, processed_output)

    # ৭. পাবলিশিং
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

    # ৮. হিস্টোরি ও দৈনিক পরিসংখ্যান আপডেট
    history["last_scholar_index"] = next_scholar_idx
    if "posted_ids" not in history or not isinstance(history["posted_ids"], list):
        history["posted_ids"] = []
    history["posted_ids"].append(selected_item["src_id"])
    daily_stats["total_posted"] = daily_stats.get("total_posted", 0) + 1
    history["daily_stats"] = daily_stats
    save_local_history(history)
    print(f"📊 আজকের ইসলামিক শর্ট ওয়াজ পোস্টিং সংখ্যা: {daily_stats['total_posted']}/১০টি সম্পন্ন!")

    # ৯. টেম্প ক্লিনআপ
    try:
        if os.path.exists(processed_output): os.remove(processed_output)
        if "downloads" in downloaded_video and os.path.exists(downloaded_video): os.remove(downloaded_video)
    except Exception:
        pass

if __name__ == "__main__":
    run()
