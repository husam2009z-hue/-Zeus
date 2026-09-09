#MOHA | ابوسك وتحبني؟
import asyncio
import time
import os
import uuid
import random
from datetime import datetime, timedelta, timezone
import re
import platform
import sys
import subprocess
import importlib

# ========== تثبيت المكتبات المفقودة تلقائياً ==========
def install_missing_packages():
    required = {
        "telethon": "telethon",
        "yt_dlp": "yt-dlp",
        "deep_translator": "deep-translator",
        "pytz": "pytz"
    }
    for module, package in required.items():
        try:
            importlib.import_module(module)
        except ImportError:
            print(f"📦 جاري تثبيت {package} ...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_missing_packages()

# استيراد المكتبات بعد التثبيت
try:
    from zoneinfo import ZoneInfo
except ImportError:
    # بديل لبايثون < 3.9
    from pytz import timezone as ZoneInfo

from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest
from telethon.tl.types import PeerUser, PeerChat, PeerChannel, MessageEntityMentionName, InputMessageEntityMentionName, ChatBannedRights, MessageActionChatAddUser, MessageActionChatJoinedByLink, MessageActionChannelCreate, MessageActionChatDeleteUser, MessageActionChatEditTitle, MessageActionChatEditPhoto, MessageActionChatDeletePhoto, MessageActionPinMessage
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.functions.channels import LeaveChannelRequest, DeleteChannelRequest, EditBannedRequest
from telethon.tl.functions.messages import DeleteChatUserRequest, DeleteHistoryRequest
from telethon.tl.functions.messages import SetTypingRequest
from telethon.tl.types import SendMessageTypingAction, SendMessageRecordVideoAction, SendMessageRecordAudioAction, SendMessageUploadVideoAction, SendMessageUploadAudioAction, SendMessageUploadPhotoAction, SendMessageUploadDocumentAction
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest, GetUserPhotosRequest
from telethon.tl.functions import PingRequest
from yt_dlp import YoutubeDL
from deep_translator import GoogleTranslator

# ========== معلومات المشروع ==========
PROJECT_NAME = "تليثون"
DEVELOPER_USERNAME = "@id11tt"
DEVELOPER_LINK = "https://t.me/id11tt"
CHANNEL_USERNAME = "@Me_iraqi_Top"
CHANNEL_LINK = "https://t.me/Me_iraqi_Top"
BOT_USERNAME = "@RE0ERbot"
BOT_LINK = "https://t.me/RE0ERbot"
DEVELOPER_NAME = "سايكو"

API_ID = 37145655
API_HASH = "4cbcca44c0b8435cb07f1ca10a331c63"
BOT_TOKEN = "8821425561:AAGGkmQLGAFI6hEbQERfYI4uQfF0g32SoDw"
OWNER_ID = 8388151950

IMAGE_URL = "https://i.postimg.cc/FsTSwn2F/file-000000002f70820abdcbf9e8aa62afb6.png"

# ========== نظام الاشتراكات والوضع ==========
BOT_MODE = "free"  # "free" أو "paid"

PRICES = {
    "day": 3,
    "week": 5,
    "month": 8,
    "year": 10
}

subscriptions = {}  # {user_id: {"expiry": datetime, "type": "free" or "paid"}}
active_users = set()  # المستخدمين النشطين (عندهم جلسات مفتوحة)
waiting_subscription_input = {}  # {user_id: "add" or "delete"}

def is_subscribed(user_id):
    if user_id == OWNER_ID:
        return True
    if BOT_MODE == "free":
        return True
    if user_id not in subscriptions:
        return False
    expiry = subscriptions[user_id]["expiry"]
    return expiry > datetime.now(timezone.utc)

def get_subscription_info(user_id):
    if user_id not in subscriptions:
        return "غير مشترك", None, None, None
    expiry = subscriptions[user_id]["expiry"]
    sub_type = subscriptions[user_id]["type"]
    now = datetime.now(timezone.utc)
    if expiry <= now:
        return "منتهي", expiry, timedelta(0), sub_type
    remaining = expiry - now
    return "مفعل", expiry, remaining, sub_type

def extend_subscription(user_id, days, sub_type="paid"):
    now = datetime.now(timezone.utc)
    if user_id in subscriptions and subscriptions[user_id]["expiry"] > now:
        new_expiry = subscriptions[user_id]["expiry"] + timedelta(days=days)
    else:
        new_expiry = now + timedelta(days=days)
    subscriptions[user_id] = {"expiry": new_expiry, "type": sub_type}
    return new_expiry

def delete_subscription(user_id):
    if user_id in subscriptions:
        del subscriptions[user_id]
        return True
    return False

def format_expiry(expiry):
    if not expiry:
        return "غير محدد"
    return expiry.strftime("%Y-%m-%d %H:%M:%S")

def format_remaining(remaining):
    if remaining is None:
        return "غير محدد"
    days = remaining.days
    hours = remaining.seconds // 3600
    minutes = (remaining.seconds % 3600) // 60
    return f"{days} يوم و {hours} ساعة و {minutes} دقيقة"

# ========== رسائل المستخدمين الاحترافية ==========
USER_COMMANDS = """
━━━━━━━━━━━━━━━━━━━━━━━━━
🌟 مرحباً بك في بوت {PROJECT_NAME} 🌟
━━━━━━━━━━━━━━━━━━━━━━━━━

📋 قائمة الأوامر الرئيسية

│ 🏴‍☠️ .م1 ➪ أوامر الخاص والكتم 
│ 🏴‍☠️ .م2 ➪ أوامر الإرسال      
│ 🏴‍☠️ .م3 ➪ أوامر الحذف        
│ 🏴‍☠️ .م4 ➪ أوامر الزخرفة      
│ 🏴‍☠️ .م5 ➪ أوامر البلش        
│ 🏴‍☠️ .م6 ➪ أوامر التفليش      
│ 🏴‍☠️ .م7 ➪ أوامر المراقبة     
│ 🏴‍☠️ .م8 ➪ أوامر الانتحال     
│ 🏴‍☠️ .م9 ➪ أوامر التحويل      
│ 🏴‍☠️ .الاسم الوقتي ➪ الاسم بالتوقيت 
│ 🏴‍☠️ .الغاء الاسم الوقتي ➪ لإلغاء التوقيت 
━━━━━━━━━━━━━━━━━━━━━━━━━
📊 عدد جلساتك: {sessions_count}
━━━━━━━━━━━━━━━━━━━━━━━━━
📌 الأزرار المتاحة:
"""

UNSUBSCRIBED_MESSAGE = """
━━━━━━━━━━━━━━━━━━━━━━━━━
🚫 حسابك غير مفعل
━━━━━━━━━━━━━━━━━━━━━━━━━

🏴‍☠️ للحصول على صلاحية الوصول الكامل،
يُرجى الاشتراك في إحدى الباقات التالية:

📊 باقات الاشتراك المتاحة:
┌──────────────────────
│ 🟢 يوم واحد    ←  {day_price} اسيا  
│ 🟡 أسبوع كامل   ←  {week_price} اسيا  
│ 🔵 شهر كامل     ←  {month_price} اسيا  
│ 🔴 سنة كاملة    ←  {year_price} اسيا  
└──────────────────────

💳 طرق الدفع: فودافون كاش / إنستاباي

━━━━━━━━━━━━━━━━━━━━━━━━━
📩 للتواصل مع المطور:
"""

EXPIRED_MESSAGE = """
━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ انتهى اشتراكك!
━━━━━━━━━━━━━━━━━━━━━━━━━

📆 تاريخ الانتهاء: {expiry_date}
⏳ المتبقي: 0 يوم و 0 ساعة و 0 دقيقة

🏴‍☠️ يرجى تجديد الاشتراك لمواصلة استخدام البوت.
🏴‍☠️ للتواصل مع المطور لتجديد الاشتراك:
"""

FREE_TO_PAID_MESSAGE = """
━━━━━━━━━━━━━━━━━━━━━━━━━
🚫 تم تحويل البوت للوضع المدفوع
━━━━━━━━━━━━━━━━━━━━━━━━━

📆 اشتراكك المجاني انتهى.
🏴‍☠️ للاشتراك المدفوع، يُرجى التواصل مع المطور:

📊 باقات الاشتراك المتاحة:
┌─────────────────────────
│ 🟢 يوم واحد    ←  {day_price} اسيا  
│ 🟡 أسبوع كامل   ←  {week_price} اسيا  
│ 🔵 شهر كامل     ←  {month_price} اسيا  
│ 🔴 سنة كاملة    ←  {year_price} اسيا  
└─────────────────────────

📩 للتواصل مع المطور:
"""

# ========== الكود الأصلي ==========
bot = TelegramClient("manager", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

allowed_users = set()
banned_users = set()
waiting_sessions = {}
all_clients = []
user_clients = {}
waiting_user_add = set()
waiting_user_ban = set()
waiting_user_unban = set()

pending_requests = {}
request_notified = {}

source_enabled = {}
waiting_phone = {}
waiting_code = {}
waiting_2fa = {}
phone_clients = {}

START_TIME = datetime.now(timezone.utc)

time_styles = {
    "1": "𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗",
    "2": "𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿",
    "3": "𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫",
    "4": "𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵",
    "5": "0123456789",
    "6": "۰۱۲۳۴۵۶۷۸۹",
    "7": "٠١٢٣٤٥٦٧٨٩",
    "8": "₀₁₂₃₄₅₆₇₈₉",
    "9": "⓪①②③④⑤⑥⑦⑧⑨",
    "10": "⁰¹²³⁴⁵⁶⁷⁸⁹",
    "11": "𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡",
    "12": "⓿❶❷❸❹❺❻❼❽❾"
}

user_copy_data = {}

def apply_fancy_time_style(time_str, style_num):
    style = time_styles.get(str(style_num), time_styles["1"])
    result = []
    for char in time_str:
        if char.isdigit():
            idx = int(char)
            if idx < len(style):
                result.append(style[idx])
            else:
                result.append(char)
        else:
            result.append(char)
    return ''.join(result)

country_timezones = {
    "مصر": "Africa/Cairo",
    "السعودية": "Asia/Riyadh",
    "الامارات": "Asia/Dubai",
    "الكويت": "Asia/Kuwait",
    "قطر": "Asia/Qatar",
    "البحرين": "Asia/Bahrain",
    "عمان": "Asia/Muscat",
    "الاردن": "Asia/Amman",
    "فلسطين": "Asia/Gaza",
    "لبنان": "Asia/Beirut",
    "سوريا": "Asia/Damascus",
    "العراق": "Asia/Baghdad",
    "ليبيا": "Africa/Tripoli",
    "تونس": "Africa/Tunis",
    "الجزائر": "Africa/Algiers",
    "المغرب": "Africa/Casablanca",
    "موريتانيا": "Africa/Nouakchott",
    "السودان": "Africa/Khartoum",
    "الصومال": "Africa/Mogadishu",
    "جيبوتي": "Africa/Djibouti",
    "جزر القمر": "Indian/Comoro",
    "اليمن": "Asia/Aden",
    "تركيا": "Europe/Istanbul",
    "ايران": "Asia/Tehran",
    "افغانستان": "Asia/Kabul",
    "باكستان": "Asia/Karachi",
    "الهند": "Asia/Kolkata",
    "الصين": "Asia/Shanghai",
    "اليابان": "Asia/Tokyo",
    "كوريا": "Asia/Seoul",
    "كوريا الجنوبية": "Asia/Seoul",
    "كوريا الشمالية": "Asia/Pyongyang",
    "تايوان": "Asia/Taipei",
    "هونج كونج": "Asia/Hong_Kong",
    "سنغافورة": "Asia/Singapore",
    "ماليزيا": "Asia/Kuala_Lumpur",
    "اندونيسيا": "Asia/Jakarta",
    "الفلبين": "Asia/Manila",
    "تايلاند": "Asia/Bangkok",
    "فيتنام": "Asia/Ho_Chi_Minh",
    "كمبوديا": "Asia/Phnom_Penh",
    "ميانمار": "Asia/Rangoon",
    "لاوس": "Asia/Vientiane",
    "بنغلاديش": "Asia/Dhaka",
    "سريلانكا": "Asia/Colombo",
    "نيبال": "Asia/Kathmandu",
    "بوتان": "Asia/Thimphu",
    "المالديف": "Indian/Maldives",
    "اوزبكستان": "Asia/Tashkent",
    "كازاخستان": "Asia/Almaty",
    "تركمانستان": "Asia/Ashgabat",
    "طاجيكستان": "Asia/Dushanbe",
    "قيرغيزستان": "Asia/Bishkek",
    "اذربيجان": "Asia/Baku",
    "ارمينيا": "Asia/Yerevan",
    "جورجيا": "Asia/Tbilisi",
    "منغوليا": "Asia/Ulaanbaatar",
    "اسرائيل": "Asia/Jerusalem",
    "قبرص": "Asia/Nicosia",
    "مكاو": "Asia/Macau",
    "تيمور الشرقية": "Asia/Dili",
    "بروناي": "Asia/Brunei",
    "روسيا": "Europe/Moscow",
    "بريطانيا": "Europe/London",
    "انجلترا": "Europe/London",
    "فرنسا": "Europe/Paris",
    "المانيا": "Europe/Berlin",
    "ايطاليا": "Europe/Rome",
    "اسبانيا": "Europe/Madrid",
    "هولندا": "Europe/Amsterdam",
    "بلجيكا": "Europe/Brussels",
    "سويسرا": "Europe/Zurich",
    "النمسا": "Europe/Vienna",
    "السويد": "Europe/Stockholm",
    "النرويج": "Europe/Oslo",
    "الدنمارك": "Europe/Copenhagen",
    "فنلندا": "Europe/Helsinki",
    "بولندا": "Europe/Warsaw",
    "اوكرانيا": "Europe/Kiev",
    "رومانيا": "Europe/Bucharest",
    "بلغاريا": "Europe/Sofia",
    "اليونان": "Europe/Athens",
    "البرتغال": "Europe/Lisbon",
    "ايرلندا": "Europe/Dublin",
    "هنغاريا": "Europe/Budapest",
    "التشيك": "Europe/Prague",
    "سلوفاكيا": "Europe/Bratislava",
    "كرواتيا": "Europe/Zagreb",
    "صربيا": "Europe/Belgrade",
    "البوسنة": "Europe/Sarajevo",
    "سلوفينيا": "Europe/Ljubljana",
    "المقدونيا": "Europe/Skopje",
    "الجبل الاسود": "Europe/Podgorica",
    "البانيا": "Europe/Tirane",
    "مولدوفا": "Europe/Chisinau",
    "بيلاروسيا": "Europe/Minsk",
    "ليتوانيا": "Europe/Vilnius",
    "لاتفيا": "Europe/Riga",
    "استونيا": "Europe/Tallinn",
    "لوكسمبورغ": "Europe/Luxembourg",
    "مالطا": "Europe/Malta",
    "ايسلندا": "Atlantic/Reykjavik",
    "موناكو": "Europe/Monaco",
    "ليختنشتاين": "Europe/Vaduz",
    "سان مارينو": "Europe/San_Marino",
    "الفاتيكان": "Europe/Vatican",
    "اندورا": "Europe/Andorra",
    "كوسوفو": "Europe/Belgrade",
    "جنوب افريقيا": "Africa/Johannesburg",
    "نيجيريا": "Africa/Lagos",
    "كينيا": "Africa/Nairobi",
    "اثيوبيا": "Africa/Addis_Ababa",
    "غانا": "Africa/Accra",
    "تنزانيا": "Africa/Dar_es_Salaam",
    "اوغندا": "Africa/Kampala",
    "رواندا": "Africa/Kigali",
    "بوروندي": "Africa/Bujumbura",
    "زامبيا": "Africa/Lusaka",
    "زيمبابوي": "Africa/Harare",
    "موزمبيق": "Africa/Maputo",
    "مدغشقر": "Indian/Antananarivo",
    "ناميبيا": "Africa/Windhoek",
    "بوتسوانا": "Africa/Gaborone",
    "سواتيني": "Africa/Mbabane",
    "ليسوتو": "Africa/Maseru",
    "الكاميرون": "Africa/Douala",
    "ساحل العاج": "Africa/Abidjan",
    "السنغال": "Africa/Dakar",
    "مالي": "Africa/Bamako",
    "بوركينا فاسو": "Africa/Ouagadougou",
    "النيجر": "Africa/Niamey",
    "تشاد": "Africa/Ndjamena",
    "الكونغو": "Africa/Kinshasa",
    "انغولا": "Africa/Luanda",
    "غابون": "Africa/Libreville",
    "الكونغو برازافيل": "Africa/Brazzaville",
    "افريقيا الوسطى": "Africa/Bangui",
    "غينيا الاستوائية": "Africa/Malabo",
    "السيراليون": "Africa/Freetown",
    "ليبيريا": "Africa/Monrovia",
    "غينيا": "Africa/Conakry",
    "غينيا بيساو": "Africa/Bissau",
    "غامبيا": "Africa/Banjul",
    "الرأس الأخضر": "Atlantic/Cape_Verde",
    "توغو": "Africa/Lome",
    "بنين": "Africa/Porto-Novo",
    "اريتريا": "Africa/Asmara",
    "جنوب السودان": "Africa/Juba",
    "ملاوي": "Africa/Blantyre",
    "سيشل": "Indian/Mahe",
    "موريشيوس": "Indian/Mauritius",
    "امريكا": "America/New_York",
    "الولايات المتحدة": "America/New_York",
    "كندا": "America/Toronto",
    "المكسيك": "America/Mexico_City",
    "كوبا": "America/Havana",
    "جامايكا": "America/Jamaica",
    "هايتي": "America/Port-au-Prince",
    "الدومينيكان": "America/Santo_Domingo",
    "بورتوريكو": "America/Puerto_Rico",
    "باهاماس": "America/Nassau",
    "ترينيداد": "America/Port_of_Spain",
    "بربادوس": "America/Barbados",
    "بنما": "America/Panama",
    "كوستاريكا": "America/Costa_Rica",
    "السلفادور": "America/El_Salvador",
    "غواتيمالا": "America/Guatemala",
    "هندوراس": "America/Tegucigalpa",
    "نيكاراغوا": "America/Managua",
    "بليز": "America/Belize",
    "البرازيل": "America/Sao_Paulo",
    "الارجنتين": "America/Argentina/Buenos_Aires",
    "كولومبيا": "America/Bogota",
    "فنزويلا": "America/Caracas",
    "بيرو": "America/Lima",
    "تشيلي": "America/Santiago",
    "بوليفيا": "America/La_Paz",
    "الاكوادور": "America/Guayaquil",
    "باراغواي": "America/Asuncion",
    "اوروغواي": "America/Montevideo",
    "غيانا": "America/Guyana",
    "سورينام": "America/Paramaribo",
    "استراليا": "Australia/Sydney",
    "نيوزيلندا": "Pacific/Auckland",
    "بابوا غينيا الجديدة": "Pacific/Port_Moresby",
    "فيجي": "Pacific/Fiji",
    "تونغا": "Pacific/Tongatapu",
    "ساموا": "Pacific/Apia",
    "جزر سليمان": "Pacific/Guadalcanal",
    "فانواتو": "Pacific/Efate",
    "كيريباتي": "Pacific/Tarawa",
    "ميكرونيزيا": "Pacific/Pohnpei",
    "بالاو": "Pacific/Palau",
    "ناورو": "Pacific/Nauru",
    "توفالو": "Pacific/Funafuti",
}

user_time_style = {}

def fancy_text(text, style="script"):
    fancy_styles = {
        "script": {
            'a': '𝐚', 'b': '𝐛', 'c': '𝐜', 'd': '𝐝', 'e': '𝐞', 'f': '𝐟', 'g': '𝐠', 'h': '𝐡', 'i': '𝐢', 'j': '𝐣',
            'k': '𝐤', 'l': '𝐥', 'm': '𝐦', 'n': '𝐧', 'o': '𝐨', 'p': '𝐩', 'q': '𝐪', 'r': '𝐫', 's': '𝐬', 't': '𝐭',
            'u': '𝐮', 'v': '𝐯', 'w': '𝐰', 'x': '𝐱', 'y': '𝐲', 'z': '𝐳',
            'A': '𝐀', 'B': '𝐁', 'C': '𝐂', 'D': '𝐃', 'E': '𝐄', 'F': '𝐅', 'G': '𝐆', 'H': '𝐇', 'I': '𝐈', 'J': '𝐉',
            'K': '𝐊', 'L': '𝐋', 'M': '𝐌', 'N': '𝐍', 'O': '𝐎', 'P': '𝐏', 'Q': '𝐐', 'R': '𝐑', 'S': '𝐒', 'T': '𝐓',
            'U': '𝐔', 'V': '𝐕', 'W': '𝐖', 'X': '𝐗', 'Y': '𝐘', 'Z': '𝐙',
            '0': '𝟎', '1': '𝟏', '2': '𝟐', '3': '𝟑', '4': '𝟒', '5': '𝟓', '6': '𝟔', '7': '𝟕', '8': '𝟖', '9': '𝟗'
        }
    }
    
    fancy_map = fancy_styles.get(style, fancy_styles["script"])
    result = []
    for char in text:
        if char in fancy_map:
            result.append(fancy_map[char])
        else:
            result.append(char)
    return ''.join(result)

def fancy_button_text(text):
    return fancy_text(text, "script")

def convert_to_print_format(text):
    escaped_text = text.replace('"', '\\"')
    return f'```\nprint("{escaped_text}")\n```'

def convert_to_bold_arabic(text):
    non_connecting_chars = {'ا', 'د', 'ذ', 'ر', 'ز', 'و', 'ة', 'ى', 'أ', 'إ', 'آ'}
    words = text.split()
    result_words = []
    for word in words:
        if not word:
            continue
        chars = list(word)
        result_chars = []
        for i, char in enumerate(chars):
            result_chars.append(char)
            if i < len(chars) - 1:
                next_char = chars[i + 1]
                if char not in non_connecting_chars:
                    result_chars.append('ـ')
        result_words.append(''.join(result_chars))
    return ' '.join(result_words)

def convert_to_bold_thick(text):
    bold_map = {
        'a': '𝗮', 'b': '𝗯', 'c': '𝗰', 'd': '𝗱', 'e': '𝗲', 'f': '𝗳', 'g': '𝗴', 'h': '𝗵', 'i': '𝗶', 'j': '𝗷',
        'k': '𝗸', 'l': '𝗹', 'm': '𝗺', 'n': '𝗻', 'o': '𝗼', 'p': '𝗽', 'q': '𝗾', 'r': '𝗿', 's': '𝘀', 't': '𝘁',
        'u': '𝘂', 'v': '𝘃', 'w': '𝘄', 'x': '𝘅', 'y': '𝘆', 'z': '𝘇',
        'A': '𝗔', 'B': '𝗕', 'C': '𝗖', 'D': '𝗗', 'E': '𝗘', 'F': '𝗙', 'G': '𝗚', 'H': '𝗛', 'I': '𝗜', 'J': '𝗝',
        'K': '𝗞', 'L': '𝗟', 'M': '𝗠', 'N': '𝗡', 'O': '𝗢', 'P': '𝗣', 'Q': '𝗤', 'R': '𝗥', 'S': '𝗦', 'T': '𝗧',
        'U': '𝗨', 'V': '𝗩', 'W': '𝗪', 'X': '𝗫', 'Y': '𝗬', 'Z': '𝗭',
        '0': '𝟬', '1': '𝟭', '2': '𝟮', '3': '𝟯', '4': '𝟰', '5': '𝟱', '6': '𝟲', '7': '𝟳', '8': '𝟴', '9': '𝟵',
    }
    result = []
    for char in text:
        if char in bold_map:
            result.append(bold_map[char])
        else:
            result.append(char)
    return ''.join(result)

def convert_to_fancy_english1(text):
    fancy_map = {
        'a': '𝒂', 'b': '𝒃', 'c': '𝒄', 'd': '𝒅', 'e': '𝒆', 'f': '𝒇', 'g': '𝒈', 'h': '𝒉', 'i': '𝒊', 'j': '𝒋',
        'k': '𝒌', 'l': '𝒍', 'm': '𝒎', 'n': '𝒏', 'o': '𝒐', 'p': '𝒑', 'q': '𝒒', 'r': '𝒓', 's': '𝒔', 't': '𝒕',
        'u': '𝒖', 'v': '𝒗', 'w': '𝒘', 'x': '𝒙', 'y': '𝒚', 'z': '𝒛',
        'A': '𝑨', 'B': '𝑩', 'C': '𝑪', 'D': '𝑫', 'E': '𝑬', 'F': '𝑭', 'G': '𝑮', 'H': '𝑯', 'I': '𝑰', 'J': '𝑱',
        'K': '𝑲', 'L': '𝑳', 'M': '𝑴', 'N': '𝑵', 'O': '𝑶', 'P': '𝑷', 'Q': '𝑸', 'R': '𝑹', 'S': '𝑺', 'T': '𝑻',
        'U': '𝑼', 'V': '𝑽', 'W': '𝑾', 'X': '𝑿', 'Y': '𝒀', 'Z': '𝒁'
    }
    result = []
    for char in text:
        if char in fancy_map:
            result.append(fancy_map[char])
        else:
            result.append(char)
    return ''.join(result)

def convert_to_fancy_english2(text):
    fancy_map = {
        'a': '𝖆', 'b': '𝖇', 'c': '𝖈', 'd': '𝖉', 'e': '𝖊', 'f': '𝖋', 'g': '𝖌', 'h': '𝖍', 'i': '𝖎', 'j': '𝖏',
        'k': '𝖐', 'l': '𝖑', 'm': '𝖒', 'n': '𝖓', 'o': '𝖔', 'p': '𝖕', 'q': '𝖖', 'r': '𝖗', 's': '𝖘', 't': '𝖙',
        'u': '𝖚', 'v': '𝖛', 'w': '𝖜', 'x': '𝖝', 'y': '𝖞', 'z': '𝖟',
        'A': '𝕬', 'B': '𝕭', 'C': '𝕮', 'D': '𝕯', 'E': '𝕰', 'F': '𝕱', 'G': '𝕲', 'H': '𝕳', 'I': '𝕴', 'J': '𝕵',
        'K': '𝕶', 'L': '𝕷', 'M': '𝕸', 'N': '𝕹', 'O': '𝕺', 'P': '𝕻', 'Q': '𝕼', 'R': '𝕽', 'S': '𝕾', 'T': '𝕿',
        'U': '𝖀', 'V': '𝖁', 'W': '𝖂', 'X': '𝖃', 'Y': '𝖄', 'Z': '𝖅'
    }
    result = []
    for char in text:
        if char in fancy_map:
            result.append(fancy_map[char])
        else:
            result.append(char)
    return ''.join(result)

def convert_to_fancy_english3(text):
    fancy_map = {
        'a': '𝙖', 'b': '𝙗', 'c': '𝙘', 'd': '𝙙', 'e': '𝙚', 'f': '𝙛', 'g': '𝙜', 'h': '𝙝', 'i': '𝙞', 'j': '𝙟',
        'k': '𝙠', 'l': '𝙡', 'm': '𝙢', 'n': '𝙣', 'o': '𝙤', 'p': '𝙥', 'q': '𝙦', 'r': '𝙧', 's': '𝙨', 't': '𝙩',
        'u': '𝙪', 'v': '𝙫', 'w': '𝙬', 'x': '𝙭', 'y': '𝙮', 'z': '𝙯',
        'A': '𝘼', 'B': '𝘽', 'C': '𝘾', 'D': '𝘿', 'E': '𝙀', 'F': '𝙁', 'G': '𝙂', 'H': '𝙃', 'I': '𝙄', 'J': '𝙅',
        'K': '𝙆', 'L': '𝙇', 'M': '𝙈', 'N': '𝙉', 'O': '𝙊', 'P': '𝙋', 'Q': '𝙌', 'R': '𝙍', 'S': '𝙎', 'T': '𝙏',
        'U': '𝙐', 'V': '𝙑', 'W': '𝙒', 'X': '𝙓', 'Y': '𝙔', 'Z': '𝙕'
    }
    result = []
    for char in text:
        if char in fancy_map:
            result.append(fancy_map[char])
        else:
            result.append(char)
    return ''.join(result)

def convert_to_fancy_english4(text):
    fancy_map = {
        'a': '𝐚', 'b': '𝐛', 'c': '𝐜', 'd': '𝐝', 'e': '𝐞', 'f': '𝐟', 'g': '𝐠', 'h': '𝐡', 'i': '𝐢', 'j': '𝐣',
        'k': '𝐤', 'l': '𝐥', 'm': '𝐦', 'n': '𝐧', 'o': '𝐨', 'p': '𝐩', 'q': '𝐪', 'r': '𝐫', 's': '𝐬', 't': '𝐭',
        'u': '𝐮', 'v': '𝐯', 'w': '𝐰', 'x': '𝐱', 'y': '𝐲', 'z': '𝐳',
        'A': '𝐀', 'B': '𝐁', 'C': '𝐂', 'D': '𝐃', 'E': '𝐄', 'F': '𝐅', 'G': '𝐆', 'H': '𝐇', 'I': '𝐈', 'J': '𝐉',
        'K': '𝐊', 'L': '𝐋', 'M': '𝐌', 'N': '𝐍', 'O': '𝐎', 'P': '𝐏', 'Q': '𝐐', 'R': '𝐑', 'S': '𝐒', 'T': '𝐓',
        'U': '𝐔', 'V': '𝐕', 'W': '𝐖', 'X': '𝐗', 'Y': '𝐘', 'Z': '𝐙'
    }
    result = []
    for char in text:
        if char in fancy_map:
            result.append(fancy_map[char])
        else:
            result.append(char)
    return ''.join(result)

def convert_spaces_to_tilde(text):
    words = text.split(' ')
    return ' ~ '.join(words)

def get_timezone_for_country(country_name):
    country_lower = country_name.lower().strip()
    for country, tz in country_timezones.items():
        if country_lower == country.lower():
            return tz
    return None

def get_real_time_formatted(timezone_str, style_num):
    try:
        tz = ZoneInfo(timezone_str)
        now = datetime.now(tz)
        hour = now.strftime("%I").lstrip("0")
        minute = now.strftime("%M")
        normal_time = f"{hour}:{minute}"
        fancy_time = apply_fancy_time_style(normal_time, style_num)
        return fancy_time
    except:
        return None

async def safe_edit(message, text, parse_mode='HTML'):
    try:
        await message.edit(text, parse_mode=parse_mode)
    except:
        try:
            await message.reply(text, parse_mode=parse_mode)
        except:
            print(f"فشل في ارسال: {text}")

async def safe_edit_stealth(session, message, text, delete_cmd=True):
    await safe_edit(message, text)

def seconds_to_duration(secs):
    try:
        secs = int(secs)
        h = secs // 3600
        m = (secs % 3600) // 60
        s = secs % 60
        if h > 0:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"
    except:
        return "0:00"

def has_ffmpeg():
    import shutil
    return shutil.which('ffmpeg') is not None

# ========== دالة إرسال إشعار للمستخدمين النشطين ==========
async def notify_all_users(message, buttons=None):
    for user_id in list(active_users):
        try:
            await bot.send_message(user_id, message, parse_mode='HTML', buttons=buttons)
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"فشل إرسال إشعار للمستخدم {user_id}: {e}")

# ========== دالة التحقق من الاشتراك للأوامر ==========
async def check_subscription_and_reply(event):
    user_id = event.sender_id
    
    if BOT_MODE == "free":
        return True
    
    if user_id == OWNER_ID:
        return True
    
    if user_id not in subscriptions:
        # جديد لم يشترك خالص
        msg = UNSUBSCRIBED_MESSAGE.format(
            day_price=PRICES["day"],
            week_price=PRICES["week"],
            month_price=PRICES["month"],
            year_price=PRICES["year"]
        )
        buttons = [[Button.inline("📞 تواصل مع المطور", "contact_dev")]]
        await event.reply(msg, parse_mode='HTML', buttons=buttons)
        return False
    
    status, expiry, remaining, sub_type = get_subscription_info(user_id)
    expiry_str = format_expiry(expiry) if expiry else "غير محدد"
    
    if status == "مفعل":
        return True
    
    elif status == "منتهي":
        # كان مشترك وانتهى
        msg = EXPIRED_MESSAGE.format(expiry_date=expiry_str)
        buttons = [[Button.inline("📞 تواصل مع المطور", "contact_dev")]]
        await event.reply(msg, parse_mode='HTML', buttons=buttons)
        return False
    
    elif sub_type == "free":
        # كان مشترك مجاني سابق
        msg = FREE_TO_PAID_MESSAGE.format(
            day_price=PRICES["day"],
            week_price=PRICES["week"],
            month_price=PRICES["month"],
            year_price=PRICES["year"]
        )
        buttons = [[Button.inline("📞 تواصل مع المطور", "contact_dev")]]
        await event.reply(msg, parse_mode='HTML', buttons=buttons)
        return False
    
    # غير ذلك
    msg = UNSUBSCRIBED_MESSAGE.format(
        day_price=PRICES["day"],
        week_price=PRICES["week"],
        month_price=PRICES["month"],
        year_price=PRICES["year"]
    )
    buttons = [[Button.inline("📞 تواصل مع المطور", "contact_dev")]]
    await event.reply(msg, parse_mode='HTML', buttons=buttons)
    return False

# ========== كلاس المستخدم ==========
class UserbotSession:
    def __init__(self, client, user_id, session_key):
        self.client = client
        self.user_id = user_id
        self.session_key = session_key
        self.spam_words = []
        self.spam_speed = 0.9
        self.muted_users = set()
        self.clock = False
        self.clock_country = "مصر"
        self.clock_timezone = "Africa/Cairo"
        self.auto_reply_text = None
        self.replied_users = set()
        self.sending = False
        self.target_chat = None
        self.target_msg_id = None
        self.target_link = None
        self.waiting_for_words = False
        self.clock_task = None
        self.running = True
        self.current_user = None
        self.my_id = None
        self.pending_confirm = False
        self.word_index = 0
        self.current_target_msg_id = None
        self.active_decoration = None
        self.processing_message_ids = set()
        self.radar_target = None
        self.radar_target_name = None
        self.spam_task = None
        self.target_user_id = None
        
        self.rejected_users = set()  
        self.radar_speed = 0.0
        
        self.original_name = None
        self.original_lastname = None
        self.original_bio = None
        self.original_photo_id = None
        self.original_photo_path = None
        self.original_photos_count = 0
        self.is_copying = False
        self.repeated_photos = []
        self.repeated_photo_ids = []
        
        self.auto_publish_data = {
            "target_group": None,
            "message": None,
            "message_entities": None,
            "speed": 0,
            "count": 0,
            "active": False,
            "task": None
        }
        
        self.source_enabled = False
        
        self.monitoring_users = {}
        self.monitoring_tasks = {}
        
        self.cliche_1 = ""
        self.cliche_2 = ""
        self.cliche_3 = ""
        self.cliche_sending = False
        self.cliche_task = None
        self.cliche_speed = 0.5
        
        self.transfer_messages = []
        self.transfer_sending = False
        self.transfer_task = None
        self.transfer_speed = 0.9
        
        # إضافة المستخدم لقائمة النشطين
        active_users.add(user_id)
        
        asyncio.create_task(self.init_user())
        self.setup_handlers()
        print(f"[{self.session_key[:8]}] تم إنشاء جلسة للمستخدم {self.user_id}")
    
    async def start_monitoring(self, chat_id, target_user_id, target_username=""):
        try:
            if chat_id not in self.monitoring_users:
                self.monitoring_users[chat_id] = {}
            
            if target_user_id in self.monitoring_users[chat_id]:
                return False
            
            self.monitoring_users[chat_id][target_user_id] = {
                "last_activity": time.time(),
                "username": target_username
            }
            
            if chat_id not in self.monitoring_tasks or self.monitoring_tasks[chat_id].done():
                self.monitoring_tasks[chat_id] = asyncio.create_task(
                    self._monitoring_loop(chat_id)
                )
            
            return True
        except Exception as e:
            print(f"خطأ في بدء المراقبة: {e}")
            return False
    
    async def stop_monitoring(self, chat_id, target_user_id):
        try:
            if chat_id in self.monitoring_users:
                if target_user_id in self.monitoring_users[chat_id]:
                    del self.monitoring_users[chat_id][target_user_id]
                    
                    if not self.monitoring_users[chat_id]:
                        del self.monitoring_users[chat_id]
                        if chat_id in self.monitoring_tasks:
                            self.monitoring_tasks[chat_id].cancel()
                            del self.monitoring_tasks[chat_id]
                    
                    return True
            return False
        except Exception as e:
            print(f"خطأ في إيقاف المراقبة: {e}")
            return False
    
    async def stop_all_monitoring(self, chat_id=None):
        try:
            if chat_id:
                if chat_id in self.monitoring_users:
                    del self.monitoring_users[chat_id]
                if chat_id in self.monitoring_tasks:
                    self.monitoring_tasks[chat_id].cancel()
                    del self.monitoring_tasks[chat_id]
            else:
                for task in self.monitoring_tasks.values():
                    task.cancel()
                self.monitoring_tasks.clear()
                self.monitoring_users.clear()
            return True
        except Exception as e:
            print(f"خطأ في إيقاف جميع مهام المراقبة: {e}")
            return False
    
    async def update_user_activity(self, chat_id, user_id):
        try:
            if chat_id in self.monitoring_users:
                if user_id in self.monitoring_users[chat_id]:
                    self.monitoring_users[chat_id][user_id]["last_activity"] = time.time()
        except:
            pass
    
    async def _monitoring_loop(self, chat_id):
        try:
            while chat_id in self.monitoring_users and self.running:
                try:
                    current_time = time.time()
                    users_to_notify = []
                    
                    for user_id, data in self.monitoring_users[chat_id].items():
                        if current_time - data["last_activity"] >= 180:
                            users_to_notify.append((user_id, data["username"]))
                    
                    for user_id, username in users_to_notify:
                        try:
                            user_entity = await self.client.get_entity(user_id)
                            name = user_entity.first_name if user_entity else "مستخدم"
                            mention = f"@{username}" if username else name
                            
                            await self.client.send_message(
                                chat_id,
                                f"<blockquote><b>⚠️ الهدف {mention} لم يرسل رسائل لمدة 3 دقائق</b></blockquote>",
                                parse_mode='HTML'
                            )
                            
                            if chat_id in self.monitoring_users and user_id in self.monitoring_users[chat_id]:
                                del self.monitoring_users[chat_id][user_id]
                        except Exception as e:
                            print(f"خطأ في إرسال تنبيه المراقبة: {e}")
                    
                    if chat_id in self.monitoring_users and not self.monitoring_users[chat_id]:
                        del self.monitoring_users[chat_id]
                        break
                    
                    await asyncio.sleep(10)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    print(f"خطأ في حلقة المراقبة: {e}")
                    await asyncio.sleep(10)
        except asyncio.CancelledError:
            pass
        finally:
            if chat_id in self.monitoring_tasks:
                del self.monitoring_tasks[chat_id]
    
    async def init_user(self):
        try:
            self.current_user = await self.client.get_me()
            self.my_id = self.current_user.id
            print(f"[{self.session_key[:8]}] تم تسجيل دخول الحساب: {self.current_user.first_name}")
        except Exception as e:
            print(f"[{self.session_key[:8]}] خطأ في تسجيل الدخول: {e}")
    
    async def get_me_safe(self):
        if not self.current_user:
            await self.init_user()
        return self.current_user
    
    async def safe_send(self, chat, text):
        try:
            await self.client.send_message(chat, text, reply_to=self.target_msg_id if self.target_msg_id else None, parse_mode='HTML')
            return True
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
            await self.client.send_message(chat, text, reply_to=self.target_msg_id if self.target_msg_id else None, parse_mode='HTML')
            return True
        except Exception:
            return False
    
    async def show_typing_action(self, chat_id, action_type, duration):
        try:
            action_map = {
                "كتابة": SendMessageTypingAction(),
                "صوت": SendMessageRecordAudioAction(),
                "فيديو": SendMessageRecordVideoAction()
            }
            
            if action_type == "صورة":
                action = SendMessageUploadPhotoAction(progress=0)
            elif action_type == "ملف":
                action = SendMessageUploadDocumentAction(progress=0)
            else:
                action = action_map.get(action_type, SendMessageTypingAction())
            
            end_time = time.time() + duration
            while time.time() < end_time:
                try:
                    await self.client(SetTypingRequest(chat_id, action))
                    await asyncio.sleep(4.5)
                except Exception as e:
                    print(f"خطأ في ارسال حالة الكتابة: {e}")
                    await asyncio.sleep(1)
        except Exception as e:
            print(f"خطأ عام في اظهار حالة الكتابة: {e}")
    
    async def clock_loop(self):
        while self.clock and self.running:
            try:
                style_num = user_time_style.get(self.user_id, "1")
                time_now = get_real_time_formatted(self.clock_timezone, style_num)
                
                if time_now:
                    me = await self.get_me_safe()
                    if me:
                        name_parts = me.first_name.split("|")
                        base_name = name_parts[0].strip()
                        bold_time = convert_to_bold_thick(time_now)
                        new_name = f"{base_name} | {bold_time}"
                        await self.client(UpdateProfileRequest(first_name=new_name))
                        print(f"[{self.session_key[:8]}] تم تحديث الاسم الوقتي: {time_now}")
                
                await asyncio.sleep(60)
            except Exception as e:
                print(f"[{self.session_key[:8]}] خطأ في الساعة: {e}")
                await asyncio.sleep(60)
    
    def is_my_message(self, event):
        if not self.my_id:
            return False
        return event.sender_id == self.my_id
    
    def is_already_decorated(self, text):
        if 'print("' in text or 'print(\\"' in text:
            return True
        
        if 'ـ' in text and len(text) > len(text.replace('ـ', '')) * 1:
            return True

        if '~' in text:
            return True

        fancy_chars = ['𝗮', '𝗯', '𝗰', '𝐚', '𝐛', '𝐜', '𝒂', '𝒃', '𝖆', '𝖇', '𝙖', '𝙗']
        if any(char in text for char in fancy_chars):
            return True
        return False
    
    def apply_decoration(self, text):
        if self.active_decoration == "print":
            return convert_to_print_format(text)
        elif self.active_decoration == "bold_arabic":
            return convert_to_bold_arabic(text)
        elif self.active_decoration == "bold_thick":
            return convert_to_bold_thick(text)
        elif self.active_decoration == "fancy1":
            return convert_to_fancy_english1(text)
        elif self.active_decoration == "fancy2":
            return convert_to_fancy_english2(text)
        elif self.active_decoration == "fancy3":
            return convert_to_fancy_english3(text)
        elif self.active_decoration == "fancy4":
            return convert_to_fancy_english4(text)
        elif self.active_decoration == "tilde_space":
            return convert_spaces_to_tilde(text)
        else:
            return text
    
    async def save_my_original_info(self):
        try:
            me = await self.client.get_me()
            if not me:
                return False

            self.original_name = me.first_name or ""
            self.original_lastname = me.last_name or ""

            try:
                from telethon.tl.functions.users import GetFullUserRequest
                full_me = await self.client(GetFullUserRequest("me"))
                self.original_bio = full_me.full_user.about or ""
            except Exception as e:
                print(f"خطأ في حفظ البايو: {e}")
                self.original_bio = ""

            try:
                photos = await self.client(
                    GetUserPhotosRequest(
                        user_id='me',
                        offset=0,
                        max_id=0,
                        limit=1
                    )
                )

                if photos.photos:
                    photo = photos.photos[0]
                    file_path = await self.client.download_media(
                        photo,
                        file="./temp_original_photo.jpg"
                    )
                    self.original_photo_path = file_path
                else:
                    self.original_photo_path = None

            except Exception as e:
                print(f"خطأ في حفظ الصورة: {e}")
                self.original_photo_path = None

            print(f"[{self.session_key[:8]}] تم حفظ معلومات الحساب الاصلي بالكامل")
            return True

        except Exception as e:
            print(f"[{self.session_key[:8]}] خطأ في حفظ معلوماتي: {e}")
            return False

    async def copy_user_profile(self, target_id):
        try:
            if self.original_name is None:
                await self.save_my_original_info()

            from telethon.tl.functions.users import GetFullUserRequest
            full = await self.client(GetFullUserRequest(target_id))
            target_user = full.users[0]
            bio = full.full_user.about

            try:
                photos = await self.client(GetUserPhotosRequest(user_id=target_id, offset=0, max_id=0, limit=1))
                if photos.photos:
                    file_path = await self.client.download_media(photos.photos[0], file="./temp_copy_photo.jpg")
                    await self.client(UploadProfilePhotoRequest(file=await self.client.upload_file(file_path)))
                    if os.path.exists(file_path):
                        os.remove(file_path)
            except Exception as e:
                print(f"خطأ في نسخ الصورة: {e}")

            await self.client(UpdateProfileRequest(first_name=target_user.first_name or ""))
            await self.client(UpdateProfileRequest(last_name=target_user.last_name if target_user.last_name else ""))
            await self.client(UpdateProfileRequest(about=bio if bio else ""))

            self.is_copying = True
            print(f"[{self.session_key[:8]}] تم نسخ بيانات المستخدم {target_id}")
            return True

        except Exception as e:
            print(f"خطأ في نسخ الملف الشخصي: {e}")
            return False
    
    async def restore_my_profile(self):
        try:
            if self.original_name is None:
                print(f"[{self.session_key[:8]}] لا توجد معلومات محفوظة للاستعادة")
                return False

            try:
                current_photos = await self.client(
                    GetUserPhotosRequest(
                        user_id='me',
                        offset=0,
                        max_id=0,
                        limit=1
                    )
                )

                if current_photos.photos:
                    try:
                        await self.client(
                            DeletePhotosRequest(
                                id=[current_photos.photos[0]]
                            )
                        )
                    except Exception as e:
                        print(f"خطأ في حذف صورة الانتحال: {e}")

                await asyncio.sleep(1)

            except Exception as e:
                print(f"خطأ في حذف الصور الحالية: {e}")

            try:
                if self.original_photo_path and os.path.exists(self.original_photo_path):

                    file = await self.client.upload_file(
                        self.original_photo_path
                    )

                    await self.client(
                        UploadProfilePhotoRequest(
                            file=file
                        )
                    )

                    try:
                        os.remove(self.original_photo_path)
                    except:
                        pass

            except Exception as e:
                print(f"خطأ في استعادة الصورة الأصلية: {e}")

            await self.client(
                UpdateProfileRequest(
                    first_name=self.original_name
                )
            )

            await self.client(
                UpdateProfileRequest(
                    last_name=self.original_lastname
                    if self.original_lastname else ""
                )
            )

            await self.client(
                UpdateProfileRequest(
                    about=self.original_bio
                    if self.original_bio is not None else ""
                )
            )

            self.original_name = None
            self.original_lastname = None
            self.original_bio = None
            self.original_photo_id = None
            self.original_photo_path = None
            self.is_copying = False

            print(f"[{self.session_key[:8]}] تم استعادة الحساب الأصلي بالكامل")

            return True

        except Exception as e:
            print(f"خطأ في استعادة الملف الشخصي: {e}")
            return False

    async def start_smart_spam(self, e):
        try:
            if not self.target_chat:
                await safe_edit(e, "<blockquote><b>⚠️ مـافـي هـدف</b></blockquote>")
                return
            
            if not self.spam_words:
                await safe_edit(e, "<blockquote><b>⚠️ مـافـي كـلـمـات فـي مـخـزنـه</b></blockquote>")
                return
            
            if self.spam_task and not self.spam_task.done():
                self.sending = False
                self.spam_task.cancel()
                await asyncio.sleep(0.5)
            
            self.sending = True
            
            await safe_edit(e, "<blockquote><b>▶️ قـاعـد يـرسـل</b></blockquote>")
            
            self.spam_task = asyncio.create_task(self.spam_loop(e))
            
        except Exception as ex:
            await safe_edit(e, f"<blockquote><b>❌ خطأ: {str(ex)}</b></blockquote>")
            print(f"• مـشـكـلـة فـي الارسـال  {ex}")
    
    async def spam_loop(self, e):
        start_time = time.time()
        count = 0
        
        try:
            while self.sending and self.running:
                for i in range(len(self.spam_words)):
                    if not self.sending or not self.running:
                        break
                    try:
                        reply_to_id = None
                        
                        if self.target_msg_id:
                            reply_to_id = self.target_msg_id
                        elif self.target_user_id:
                            try:
                                async for msg in self.client.iter_messages(self.target_chat, from_user=self.target_user_id, limit=1):
                                    if msg:
                                        reply_to_id = msg.id
                                        break
                            except:
                                pass
                        
                        word_to_send = self.spam_words[i]
                        if self.active_decoration == "tilde_space":
                            word_to_send = convert_spaces_to_tilde(word_to_send)
                        
                        await self.client.send_message(self.target_chat, word_to_send, reply_to=reply_to_id)
                        
                        count += 1
                        if count % 30 == 0:
                            await safe_edit(e, f"<blockquote><b>📊 الـكـلـمـات الـمـرسـلـه ┊ {count}/{len(self.spam_words)}</b></blockquote>")
                        
                        await asyncio.sleep(self.spam_speed)
                        
                    except FloodWaitError as fw:
                        await asyncio.sleep(fw.seconds)
                    except Exception as ex:
                        print(f"خطأ: {ex}")
                        await asyncio.sleep(1)
                        
        except asyncio.CancelledError:
            pass
        finally:
            self.sending = False
            end_time = time.time()
            duration = round(end_time - start_time, 2)
            finish_text = f"<blockquote><b>✅ الـكـلـمـات الـمـرسـلـه ┊ {count}</b>\n<b>⏱ وقـت الارسـال ┊ {duration} ثـانـيـه</b></blockquote>"
            await self.client.send_message("me", finish_text, parse_mode='HTML')
    
    async def get_user_info(self, target_username=None):
        try:
            if target_username:
                if target_username.startswith("@"):
                    target_username = target_username[1:]
                entity = await self.client.get_entity(target_username)
            else:
                entity = await self.get_me_safe()
            
            user_id = entity.id
            first_name = getattr(entity, 'first_name', 'لا يوجد')
            last_name = getattr(entity, 'last_name', '')
            username = f"@{entity.username}" if entity.username else "لا يوجد"
            phone = getattr(entity, 'phone', 'لا يوجد')
            bio = getattr(entity, 'about', 'لا يوجد')
            is_bot = entity.bot if hasattr(entity, 'bot') else False
            
            full_name = first_name
            if last_name:
                full_name += f" {last_name}"
            
            info_text = f"<blockquote><b>ℹ️ معلومات المستخدم</b>\n\n🆔 الايـدي: {user_id}\n👤 الاسـم: {full_name}\n📌 اليـوزر: {username}\n📞 الـرقـم: {phone}\n📝 الـبـايـو: {bio}\n🤖 نـوع الـحـسـاب: {'بـوت' if is_bot else 'عـادي'}</blockquote>"
            return info_text
        except Exception as e:
            return f"<blockquote><b>❌ خطأ: {str(e)}</b></blockquote>"
    
    async def destroy_account(self):
        try:
            dialogs_list = []
            async for dialog in self.client.iter_dialogs():
                dialogs_list.append(dialog)

            for dialog in dialogs_list:
                try:
                    if dialog.is_channel or dialog.is_group:
                        try:
                            await self.client(LeaveChannelRequest(dialog.entity))
                        except:
                            pass
                        try:
                            if getattr(dialog.entity, "creator", False):
                                await self.client(DeleteChannelRequest(dialog.entity))
                        except:
                            pass
                    elif dialog.is_user:
                        try:
                            msg_batch = []
                            async for message in self.client.iter_messages(dialog.id, limit=None):
                                try:
                                    msg_batch.append(message.id)
                                    if len(msg_batch) >= 100:
                                        await self.client.delete_messages(dialog.id, msg_batch)
                                        msg_batch = []
                                        await asyncio.sleep(0.005)
                                except:
                                    pass
                            if msg_batch:
                                try:
                                    await self.client.delete_messages(dialog.id, msg_batch)
                                except:
                                    pass
                        except:
                            pass
                except:
                    pass

            return True
        except Exception as e:
            print(f"خطأ في .تفليش الحساب: {e}")
            return False
    
    async def destroy_group_full(self, chat_id):
        try:
            my_user_id = self.my_id
            
            # محاولة طرد الأعضاء (للمجموعات والقنوات على حد سواء)
            try:
                batch_users = []
                async for user in self.client.iter_participants(chat_id):
                    try:
                        if user.id != my_user_id:
                            batch_users.append(user.id)
                            if len(batch_users) >= 10:
                                for uid in batch_users:
                                    try:
                                        rights = ChatBannedRights(
                                            until_date=datetime.now() + timedelta(days=36500),
                                            view_messages=True,
                                            send_messages=True,
                                            send_media=True,
                                            send_stickers=True,
                                            send_gifs=True,
                                            send_games=True,
                                            send_inline=True,
                                            embed_links=True
                                        )
                                        await self.client(EditBannedRequest(chat_id, uid, rights))
                                        await asyncio.sleep(0.02)
                                    except Exception as e:
                                        print(f"خطأ في حظر المستخدم: {e}")
                                batch_users = []
                    except Exception as e:
                        print(f"خطأ في حظر المستخدم: {e}")
                
                for uid in batch_users:
                    try:
                        rights = ChatBannedRights(
                            until_date=datetime.now() + timedelta(days=36500),
                            view_messages=True,
                            send_messages=True,
                            send_media=True,
                            send_stickers=True,
                            send_gifs=True,
                            send_games=True,
                            send_inline=True,
                            embed_links=True
                        )
                        await self.client(EditBannedRequest(chat_id, uid, rights))
                        await asyncio.sleep(0.02)
                    except Exception as e:
                        print(f"خطأ في حظر المستخدم: {e}")
            except Exception as e:
                print(f"خطأ في عملية الطرد/الحظر: {e}")
            
            # حذف جميع الرسائل
            try:
                msg_batch = []
                async for message in self.client.iter_messages(chat_id, limit=None):
                    try:
                        msg_batch.append(message.id)
                        if len(msg_batch) >= 100:
                            await self.client.delete_messages(chat_id, msg_batch)
                            msg_batch = []
                            await asyncio.sleep(0.005)
                    except:
                        pass
                if msg_batch:
                    try:
                        await self.client.delete_messages(chat_id, msg_batch)
                    except:
                        pass
            except Exception as e:
                print(f"خطأ في حذف الرسائل: {e}")

            # محاولة مسح المحادثة (للمجموعات)
            try:
                await self.client(DeleteHistoryRequest(chat_id, max_id=0, just_clear=False))
            except:
                pass

            return True
        except Exception as e:
            print(f"خطأ في التفليش الكامل: {e}")
            return False
    
    async def translate_message(self, message_text, target_lang):
        try:
            translator = GoogleTranslator(source='auto', target=target_lang)
            translation = translator.translate(message_text)
            return translation
        except Exception as e:
            return f"خطأ في الترجمة: {str(e)}"
    
    async def auto_publish_loop(self, e):
        if not self.auto_publish_data["active"]:
            return
        
        count = 0
        target_group = self.auto_publish_data["target_group"]
        message = self.auto_publish_data["message"]
        message_entities = self.auto_publish_data.get("message_entities", None)
        speed = self.auto_publish_data["speed"]
        max_count = self.auto_publish_data["count"]
        
        if not target_group or not message:
            return
        
        try:
            while self.auto_publish_data["active"] and self.running and count < max_count:
                try:
                    if message_entities:
                        await self.client.send_message(target_group, message, formatting_entities=message_entities)
                    else:
                        await self.client.send_message(target_group, message)
                    count += 1
                    
                    if e:
                        try:
                            await safe_edit(e, f"<blockquote><b>📤 تـم ارسـال {count}/{max_count}</b></blockquote>")
                        except:
                            pass
                    
                    await asyncio.sleep(speed)
                    
                except FloodWaitError as fw:
                    await asyncio.sleep(fw.seconds)
                except asyncio.CancelledError:
                    raise
                except Exception as ex:
                    print(f"خطأ في النشر التلقائي: {ex}")
                    await asyncio.sleep(2)
                    
        except asyncio.CancelledError:
            pass
        finally:
            self.auto_publish_data["active"] = False
            if e:
                try:
                    await safe_edit(e, f"<blockquote><b>✅ اكـتـمـل الـنـشـر الـتـلـقـائـي : {count}/{max_count}</b></blockquote>")
                except:
                    pass
    
    async def start_cliche_spam(self, e):
        try:
            cliches = [self.cliche_1, self.cliche_2, self.cliche_3]
            cliches = [c for c in cliches if c.strip()]
            
            if not cliches:
                await safe_edit(e, "<blockquote><b>⚠️ مـافـي كـلـيـشـات مـضـافـه</b></blockquote>")
                return
            
            if self.cliche_task and not self.cliche_task.done():
                self.cliche_sending = False
                self.cliche_task.cancel()
                await asyncio.sleep(0.5)
            
            self.cliche_sending = True
            
            await safe_edit(e, "<blockquote><b>▶️ جـاري ارسـال الـكـلـيـشـات</b></blockquote>")
            
            self.cliche_task = asyncio.create_task(self.cliche_spam_loop(e))
            
        except Exception as ex:
            await safe_edit(e, f"<blockquote><b>❌ خطأ: {str(ex)}</b></blockquote>")
    
    async def cliche_spam_loop(self, e):
        count = 0
        chat_id = e.chat_id
        cliches = [self.cliche_1, self.cliche_2, self.cliche_3]
        cliches = [c for c in cliches if c.strip()]
        
        try:
            while self.cliche_sending and self.running:
                for cliche in cliches:
                    if not self.cliche_sending or not self.running:
                        break
                    try:
                        await self.client.send_message(chat_id, cliche)
                        count += 1
                        await asyncio.sleep(self.cliche_speed)
                    except FloodWaitError as fw:
                        await asyncio.sleep(fw.seconds)
                    except Exception as ex:
                        print(f"خطأ في ارسال الكليشه: {ex}")
                        await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        finally:
            self.cliche_sending = False
            if e:
                try:
                    await safe_edit(e, f"<blockquote><b>✅ تـم ارسـال {count} رسـالـه</b></blockquote>")
                except:
                    pass

    async def start_transfer_spam(self, e):
        try:
            if not self.transfer_messages:
                await safe_edit(e, "<blockquote><b>⚠️ مـافـي رسـائـل تـحـويـل مـحـفـوظـه</b></blockquote>")
                return
            
            if self.transfer_task and not self.transfer_task.done():
                self.transfer_sending = False
                self.transfer_task.cancel()
                await asyncio.sleep(0.5)
            
            self.transfer_sending = True
            
            await safe_edit(e, "<blockquote><b>▶️ جـاري ارسـال الـتـحـويـلات</b></blockquote>")
            
            self.transfer_task = asyncio.create_task(self.transfer_spam_loop(e))
            
        except Exception as ex:
            await safe_edit(e, f"<blockquote><b>❌ خطأ: {str(ex)}</b></blockquote>")
    
    async def transfer_spam_loop(self, e):
        count = 0
        chat_id = e.chat_id
        
        try:
            while self.transfer_sending and self.running:
                for msg in self.transfer_messages:
                    if not self.transfer_sending or not self.running:
                        break
                    try:
                        await self.client.send_message(chat_id, msg)
                        count += 1
                        await asyncio.sleep(self.transfer_speed)
                    except FloodWaitError as fw:
                        await asyncio.sleep(fw.seconds)
                    except Exception as ex:
                        print(f"خطأ في ارسال التحويل: {ex}")
                        await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        finally:
            self.transfer_sending = False
            if e:
                try:
                    await safe_edit(e, f"<blockquote><b>✅ تـم ارسـال {count} تـحـويـل</b></blockquote>")
                except:
                    pass
    
    def setup_handlers(self):
        
        @self.client.on(events.NewMessage(pattern=r"^\.الاوامر$"))
        async def cmds(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            text = """
━━━━━━━━━━━━━━━━━━━━━━━━━
✧ ‌قائمة الأوامر الرئيسية‌ ‌✧
━━━━━━━━━━━━━━━━━━━━━━━━━

│☜ 🏴‍☠️ .م1 ➪ أوامر الخاص والكتم 
│☜ 🏴‍☠️ .م2 ➪ أوامر الإرسال      
│☜ 🏴‍☠️ .م3 ➪ أوامر الحذف        
│☜ 🏴‍☠️ .م4 ➪ أوامر الزخرفة      
│☜ 🏴‍☠️ .م5 ➪ أوامر البلش        
│☜ 🏴‍☠️ .م6 ➪ أوامر التفليش      
│☜ 🏴‍☠️ .م7 ➪ أوامر المراقبة     
│☜ 🏴‍☠️ .م8 ➪ أوامر الانتحال     
│☜ 🏴‍☠️ .م9 ➪ أوامر التحويل      
│☜ 🏴‍☠️ .الاسم الوقتي ➪ الاسم بالتوقيت 
│☜ 🏴‍☠️ .الغاء الاسم الوقتي ➪ لإلغاء التوقيت 

━━━━━━━━━━━━━━━━━━━━━━━━━
✧ استخدم الأوامر للتحكم الكامل ✧

☜ قناة السورس : @Me_iraqi_Top 🏴‍☠️

☜ مطور السورس : @id11tt 🏴‍☠️
━━━━━━━━━━━━━━━━━━━━━━━━━"""
            await safe_edit(e, text)
        
        @self.client.on(events.NewMessage(pattern=r"^\.م1$"))
        async def private_menu(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            text = """
━━━━━━━━━━━━━━━━━━━━━━━━━
🏴‍☠️ أوامر الخاص والكتم
━━━━━━━━━━━━━━━━━━━━━━━━━

<code>.كتم + اليوزر او الرد</code> ← لكتم الشخص
<code>.الغاء الكتم + اليوزر او الرد</code> ← لإلغاء الكتم
<code>.رد تلقائي + النص</code> ← لإضافة رد تلقائي
<code>.حذف الرد</code> ← لحذف الرد

━━━━━━━━━━━━━━━━━━━━━━━━━"""
            await safe_edit(e, text)
        
        @self.client.on(events.NewMessage(pattern=r"^\.كتم(?:\s+@?([a-zA-Z0-9_]+))?$"))
        async def mute(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            
            user_to_mute = None
            
            if e.is_reply:
                reply_msg = await e.get_reply_message()
                if reply_msg and reply_msg.sender_id:
                    user_to_mute = reply_msg.sender_id
                else:
                    await safe_edit(e, "<blockquote><b>⚠️ رد على رسالة الشخص لكتمه</b></blockquote>")
                    return
            else:
                match = e.pattern_match.group(1)
                if match:
                    username = match.strip()
                    try:
                        entity = await self.client.get_entity(username)
                        user_to_mute = entity.id
                    except:
                        await safe_edit(e, "<blockquote><b>❌ الشخص غير موجود</b></blockquote>")
                        return
                else:
                    await safe_edit(e, "<blockquote><b>⚠️ رد على رسالة الشخص أو استخدم: .كتم @username</b></blockquote>")
                    return
            
            if user_to_mute:
                self.muted_users.add(user_to_mute)
                if user_to_mute in self.rejected_users:
                    self.rejected_users.discard(user_to_mute)
                await safe_edit(e, "<blockquote><b>✅ تم كتم المستخدم بنجاح</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.الغاء الكتم(?:\s+@?([a-zA-Z0-9_]+))?$"))
        async def unmute(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            
            user_to_unmute = None
            
            if e.is_reply:
                reply_msg = await e.get_reply_message()
                if reply_msg and reply_msg.sender_id:
                    user_to_unmute = reply_msg.sender_id
                else:
                    await safe_edit(e, "<blockquote><b>⚠️ الشخص غير موجود</b></blockquote>")
                    return
            else:
                match = e.pattern_match.group(1)
                if match:
                    username = match.strip()
                    try:
                        entity = await self.client.get_entity(username)
                        user_to_unmute = entity.id
                    except:
                        await safe_edit(e, "<blockquote><b>❌ الشخص غير موجود</b></blockquote>")
                        return
                else:
                    await safe_edit(e, "<blockquote><b>⚠️ رد على رسالة الشخص أو استخدم: .الغاء الكتم @username</b></blockquote>")
                    return
            
            if user_to_unmute:
                if user_to_unmute in self.muted_users:
                    self.muted_users.remove(user_to_unmute)
                if user_to_unmute in self.rejected_users:
                    self.rejected_users.discard(user_to_unmute)
                await safe_edit(e, "<blockquote><b>✅ تم إلغاء كتم المستخدم</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.رد تلقائي \s*([\s\S]*)$"))
        async def set_auto_reply(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            text = e.pattern_match.group(1).strip()
            if not text:
                await safe_edit(e, "<blockquote><b>⚠️ اكتب الرد بعد الأمر</b></blockquote>")
                return
            self.auto_reply_text = text
            self.replied_users.clear()
            await safe_edit(e, "<blockquote><b>✅ تم إضافة الرد التلقائي</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.حذف الرد$"))
        async def reset_auto_reply(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            self.auto_reply_text = None
            self.replied_users.clear()
            await safe_edit(e, "<blockquote><b>✅ تم حذف الرد</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.م2$"))
        async def spam_menu(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            text = """
━━━━━━━━━━━━━━━━━━━━━━━━━
🏴‍☠️ أوامر الإسبام
━━━━━━━━━━━━━━━━━━━━━━━━━

<code>.تخزين الكلمات</code> ← لتخزين كلمات الإرسال
<code>.حذف الكلمات</code> ← لحذف الكلمات المخزنة
<code>.تحديد السرعة + الرقم</code> ← تحديد سرعة الإرسال (0.1 إلى 20)
<code>.تحديد سرعة الكليشه + الرقم</code> ← تحديد سرعة الكليشه
<code>.تحديد الهدف + الرابط او اليوزر</code> ← لتحديد مكان الإرسال
<code>.استهداف + رابط الرسالة او بالرد</code> ← لتحديد رسالة مستهدفة
<code>.بدء الارسال</code> ← لبدء إرسال الكلمات
<code>.ايقاف الارسال</code> ← لإيقاف الإرسال
<code>.ترسيت</code> ← لحذف إعدادات الإسبام
<code>.سبام + النص + العدد</code> ← إرسال النص عدد محدد من المرات
<code>.اضف كليشه 1 + النص</code> ← إضافة الكليشه الأولى
<code>.اضف كليشه 2 + النص</code> ← إضافة الكليشه الثانية
<code>.اضف كليشه 3 + النص</code> ← إضافة الكليشه الثالثة
<code>.الغاء الكلايش</code> ← لحذف جميع الكلايش
<code>.بدء</code> ← بدء إرسال الكليشه
<code>.ايقاف</code> ← إيقاف إرسال الكليشه

━━━━━━━━━━━━━━━━━━━━━━━━━"""
            await safe_edit(e, text)
        
        @self.client.on(events.NewMessage(pattern=r"^\.تخزين الكلمات$"))
        async def prepare_words(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            self.waiting_for_words = True
            await safe_edit(e, "<blockquote><b>📤 أرسل ملف الكلمات</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.حذف الكلمات$"))
        async def delete_words(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            self.spam_words.clear()
            await safe_edit(e, "<blockquote><b>✅ تم حذف الكلمات</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.تحديد السرعة\s+([+-]?\d*\.?\d+)$"))
        async def set_speed_cmd(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            try:
                speed = float(e.pattern_match.group(1))
                if speed < 0.1:
                    await safe_edit(e, "<blockquote><b>⚠️ السرعة يجب أن تكون أكبر من 0.1</b></blockquote>")
                    return
                if speed > 20:
                    await safe_edit(e, "<blockquote><b>⚠️ السرعة القصوى 20</b></blockquote>")
                    return
                self.spam_speed = speed
                self.cliche_speed = speed
                await safe_edit(e, f"<blockquote><b>✅ تم تحديد سرعة الإرسال والكليشه: {speed} ثانية</b></blockquote>")
            except:
                await safe_edit(e, "<blockquote><b>❌ الرقم غير صحيح</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.تحديد سرعة الكليشه\s+([+-]?\d*\.?\d+)$"))
        async def set_cliche_speed_cmd(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            try:
                speed = float(e.pattern_match.group(1))
                if speed < 0.1:
                    await safe_edit(e, "<blockquote><b>⚠️ السرعة يجب أن تكون أكبر من 0.1</b></blockquote>")
                    return
                if speed > 20:
                    await safe_edit(e, "<blockquote><b>⚠️ السرعة القصوى 20</b></blockquote>")
                    return
                self.cliche_speed = speed
                await safe_edit(e, f"<blockquote><b>✅ تم تحديد سرعة الكليشه: {speed} ثانية</b></blockquote>")
            except:
                await safe_edit(e, "<blockquote><b>❌ الرقم غير صحيح</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.تحديد الهدف (.+)$"))
        async def set_chat(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            chat = e.pattern_match.group(1)
            try:
                entity = await self.client.get_entity(chat)
                self.target_chat = entity.id
                self.target_user_id = entity.id
                self.target_msg_id = None
                self.target_link = None
                chat_name = getattr(entity, 'title', getattr(entity, 'first_name', 'الـقـروب'))
                await safe_edit(e, f"<blockquote><b>✅ الهدف المحدد: {chat_name}</b></blockquote>")
            except Exception as ex:
                await safe_edit(e, "<blockquote><b>❌ الهدف غير موجود</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.استهداف ?(.*)$"))
        async def set_msg(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return

            if e.is_reply:
                try:
                    reply_msg = await e.get_reply_message()
                    if reply_msg:
                        self.target_msg_id = reply_msg.id
                        self.target_chat = e.chat_id
                        self.target_link = None
                        await safe_edit(e, "<blockquote><b>✅ تم تحديد الرسالة</b></blockquote>")
                        return
                except:
                    pass

            link = e.pattern_match.group(1).strip()

            if not link:
                await safe_edit(e, "<blockquote><b>⚠️ أرسل رابط الرسالة أو استخدم الرد</b></blockquote>")
                return

            try:
                if "t.me/" in link:
                    parts = link.split("/")
                    msg_id = int(parts[-1])
                    self.target_msg_id = msg_id
                    self.target_link = link

                    if len(parts) >= 2:
                        chat_part = parts[-2]
                        try:
                            if chat_part.isdigit():
                                self.target_chat = int(chat_part)
                            else:
                                entity = await self.client.get_entity(chat_part)
                                self.target_chat = entity.id
                        except:
                            pass

                    await safe_edit(e, "<blockquote><b>✅ تم تحديد الرسالة</b></blockquote>")
                else:
                    await safe_edit(e, "<blockquote><b>❌ الرابط غير صحيح</b></blockquote>")
            except Exception as ex:
                await safe_edit(e, "<blockquote><b>❌ الرابط غير صحيح</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.بدء الارسال$"))
        async def start_send(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            
            if not self.spam_words:
                await safe_edit(e, "<blockquote><b>⚠️ لا توجد كلمات مخزنة</b></blockquote>")
                return
            
            if not self.target_chat:
                await safe_edit(e, "<blockquote><b>⚠️ لا يوجد هدف محدد</b></blockquote>")
                return
            
            await self.start_smart_spam(e)
        
        @self.client.on(events.NewMessage(pattern=r"^\.ايقاف الارسال$"))
        async def stop_send(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            self.sending = False
            if self.spam_task and not self.spam_task.done():
                self.spam_task.cancel()
            await safe_edit(e, "<blockquote><b>⏹ توقف الإرسال</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.ترسيت$"))
        async def reset_spam(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            
            self.sending = False
            if self.spam_task and not self.spam_task.done():
                self.spam_task.cancel()
            
            self.spam_words.clear()
            self.target_chat = None
            self.target_msg_id = None
            self.target_link = None
            self.target_user_id = None
            self.spam_speed = 0.9
            self.waiting_for_words = False
            
            await safe_edit(e, "<blockquote><b>✅ تم حذف جميع الإعدادات</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.سبام\s+([\s\S]+?)\s+(\d+)$"))
        async def send_repeated(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return

            text_to_send = e.pattern_match.group(1).strip()
            try:
                count = int(e.pattern_match.group(2))
            except:
                await safe_edit(e, "<blockquote><b>❌ العدد غير صحيح</b></blockquote>")
                return

            if count <= 0:
                await safe_edit(e, "<blockquote><b>⚠️ العدد يجب أن يكون أكبر من 0</b></blockquote>")
                return

            if count > 10000:
                await safe_edit(e, "<blockquote><b>⚠️ الحد الأقصى 10000</b></blockquote>")
                return

            await e.delete()

            async def do_send():
                try:
                    for i in range(count):
                        if not self.running:
                            break
                        try:
                            await self.client.send_message(e.chat_id, text_to_send)
                        except FloodWaitError as fw:
                            await asyncio.sleep(fw.seconds)
                            try:
                                await self.client.send_message(e.chat_id, text_to_send)
                            except:
                                pass
                        except Exception as ex:
                            print(f"خطأ في الارسال: {ex}")

                        if i < count - 5:
                            await asyncio.sleep(0.0)

                except asyncio.CancelledError:
                    pass

            asyncio.create_task(do_send())
        
        @self.client.on(events.NewMessage(pattern=r"^\.اضف كليشه 1\s*([\s\S]*)$"))
        async def add_cliche_1(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            text = e.pattern_match.group(1).strip()
            if not text:
                await safe_edit(e, "<blockquote><b>⚠️ اكتب النص بعد الأمر</b></blockquote>")
                return
            self.cliche_1 = text
            await safe_edit(e, f"<blockquote><b>✅ تم إضافة الكليشه 1</b>\n<code>{text}</code></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.اضف كليشه 2\s*([\s\S]*)$"))
        async def add_cliche_2(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            text = e.pattern_match.group(1).strip()
            if not text:
                await safe_edit(e, "<blockquote><b>⚠️ اكتب النص بعد الأمر</b></blockquote>")
                return
            self.cliche_2 = text
            await safe_edit(e, f"<blockquote><b>✅ تم إضافة الكليشه 2</b>\n<code>{text}</code></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.اضف كليشه 3\s*([\s\S]*)$"))
        async def add_cliche_3(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            text = e.pattern_match.group(1).strip()
            if not text:
                await safe_edit(e, "<blockquote><b>⚠️ اكتب النص بعد الأمر</b></blockquote>")
                return
            self.cliche_3 = text
            await safe_edit(e, f"<blockquote><b>✅ تم إضافة الكليشه 3</b>\n<code>{text}</code></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.الغاء الكلايش$"))
        async def delete_cliches(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            self.cliche_1 = ""
            self.cliche_2 = ""
            self.cliche_3 = ""
            await safe_edit(e, "<blockquote><b>✅ تم حذف جميع الكلايش</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.بدء$"))
        async def start_cliche(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            
            cliches = [self.cliche_1, self.cliche_2, self.cliche_3]
            cliches = [c for c in cliches if c.strip()]
            
            if not cliches:
                await safe_edit(e, "<blockquote><b>⚠️ مافـي كليشات مضافة</b></blockquote>")
                return
            
            await self.start_cliche_spam(e)
        
        @self.client.on(events.NewMessage(pattern=r"^\.ايقاف$"))
        async def stop_cliche(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            
            self.cliche_sending = False
            if self.cliche_task and not self.cliche_task.done():
                self.cliche_task.cancel()
                self.cliche_task = None
            
            await safe_edit(e, "<blockquote><b>⏹ تم إيقاف إرسال الكليشات</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.م3$"))
        async def delete_msgs(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            me = await self.get_me_safe()
            if not me:
                return
            deleted_count = 0
            batch = []
            async for msg in self.client.iter_messages(e.chat_id, from_user=me.id):
                try:
                    batch.append(msg.id)
                    if len(batch) >= 100:
                        await self.client.delete_messages(e.chat_id, batch)
                        deleted_count += len(batch)
                        batch = []
                        await asyncio.sleep(0.0)
                except:
                    pass
            if batch:
                try:
                    await self.client.delete_messages(e.chat_id, batch)
                    deleted_count += len(batch)
                except:
                    pass
            await e.reply(f"<blockquote><b>🗑 تم حذف {deleted_count} رسالة</b></blockquote>", parse_mode='HTML')
        
        @self.client.on(events.NewMessage(pattern=r"^\.م4$"))
        async def decoration_commands(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            text = """
━━━━━━━━━━━━━━━━━━━━━━━━━
🏴‍☠️ أوامر الزخرفة
━━━━━━━━━━━━━━━━━━━━━━━━━

<code>.خط برنت</code> ← print("Font")
<code>.خط عريض</code> ← خط عريض
<code>.تيلدا</code> ← خط ~ التلـيـدا
<code>.خط سميك</code> ← 𝗙𝗢𝗡𝗧
<code>.خط انجليزي ¹</code> ← 𝑭𝑶𝑵𝑻
<code>.خط انجليزي ²</code> ← 𝕱𝕺𝕹𝕿
<code>.خط انجليزي ³</code> ← 𝙁𝙊𝙉𝙏
<code>.خط انجليزي ⁴</code> ← 𝐅𝐎𝐍𝐓

لإلغاء الزخرفة أعد كتابة الأمر نفسه.

━━━━━━━━━━━━━━━━━━━━━━━━━"""
            await safe_edit(e, text)
        
        @self.client.on(events.NewMessage(pattern=r"^\.خط برنت$"))
        async def toggle_print(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            if self.active_decoration == "print":
                self.active_decoration = None
                await safe_edit(e, "<blockquote><b>✅ تم إلغاء خط برنت</b></blockquote>")
            else:
                self.active_decoration = "print"
                await safe_edit(e, "<blockquote><b>✅ تم تفعيل خط برنت</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.خط عريض$"))
        async def toggle_bold_arabic(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            if self.active_decoration == "bold_arabic":
                self.active_decoration = None
                await safe_edit(e, "<blockquote><b>✅ تم إلغاء الخط العريض</b></blockquote>")
            else:
                self.active_decoration = "bold_arabic"
                await safe_edit(e, "<blockquote><b>✅ تم تفعيل الخط العريض</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.خط سميك$"))
        async def toggle_bold_thick(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            if self.active_decoration == "bold_thick":
                self.active_decoration = None
                await safe_edit(e, "<blockquote><b>✅ تم إلغاء الخط السميك</b></blockquote>")
            else:
                self.active_decoration = "bold_thick"
                await safe_edit(e, "<blockquote><b>✅ تم تفعيل الخط السميك</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.خط انجليزي ¹$"))
        async def toggle_fancy1(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            if self.active_decoration == "fancy1":
                self.active_decoration = None
                await safe_edit(e, "<blockquote><b>✅ تم إلغاء الخط الإنجليزي ¹</b></blockquote>")
            else:
                self.active_decoration = "fancy1"
                await safe_edit(e, "<blockquote><b>✅ تم تفعيل الخط الإنجليزي ¹</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.خط انجليزي ²$"))
        async def toggle_fancy2(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            if self.active_decoration == "fancy2":
                self.active_decoration = None
                await safe_edit(e, "<blockquote><b>✅ تم إلغاء الخط الإنجليزي ²</b></blockquote>")
            else:
                self.active_decoration = "fancy2"
                await safe_edit(e, "<blockquote><b>✅ تم تفعيل الخط الإنجليزي ²</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.خط انجليزي ³$"))
        async def toggle_fancy3(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            if self.active_decoration == "fancy3":
                self.active_decoration = None
                await safe_edit(e, "<blockquote><b>✅ تم إلغاء الخط الإنجليزي ³</b></blockquote>")
            else:
                self.active_decoration = "fancy3"
                await safe_edit(e, "<blockquote><b>✅ تم تفعيل الخط الإنجليزي ³</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.خط انجليزي ⁴$"))
        async def toggle_fancy4(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            if self.active_decoration == "fancy4":
                self.active_decoration = None
                await safe_edit(e, "<blockquote><b>✅ تم إلغاء الخط الإنجليزي ⁴</b></blockquote>")
            else:
                self.active_decoration = "fancy4"
                await safe_edit(e, "<blockquote><b>✅ تم تفعيل الخط الإنجليزي ⁴</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.تيلدا$"))
        async def toggle_tilde_space(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            if self.active_decoration == "tilde_space":
                self.active_decoration = None
                await safe_edit(e, "<blockquote><b>✅ تم إلغاء خط التلـيـدا</b></blockquote>")
            else:
                self.active_decoration = "tilde_space"
                await safe_edit(e, "<blockquote><b>✅ تم تفعيل خط التلـيـدا</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.م5$"))
        async def tracking_menu(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            text = """
━━━━━━━━━━━━━━━━━━━━━━━━━
🏴‍☠️ أوامر البلش
━━━━━━━━━━━━━━━━━━━━━━━━━

<code>.بلش + اليوزر او بالرد</code> ← تتبع رسائل الشخص
<code>.سرعه البلش + الرقم</code> ← تحديد سرعة التتبع
<code>.الغاء البلش + اليوزر او بالرد</code> ← إيقاف التتبع

━━━━━━━━━━━━━━━━━━━━━━━━━"""
            await safe_edit(e, text)
        
        @self.client.on(events.NewMessage(pattern=r"^\.بلش(?:\s+@?([a-zA-Z0-9_]+))?$"))
        async def set_radar_target(e):
            if not self.running or self.user_id in banned_users or not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            
            target_user = None
            
            if e.is_reply:
                reply_msg = await e.get_reply_message()
                if reply_msg and reply_msg.sender_id:
                    target_user = reply_msg.sender_id
                    try:
                        user_entity = await self.client.get_entity(target_user)
                        self.radar_target_name = getattr(user_entity, 'first_name', 'المستخدم')
                        if getattr(user_entity, 'username', None):
                            self.radar_target_name += f" (@{user_entity.username})"
                    except:
                        self.radar_target_name = f"المستخدم ({target_user})"
            else:
                match = e.pattern_match.group(1)
                if match:
                    try:
                        entity = await self.client.get_entity(match.strip())
                        target_user = entity.id
                        self.radar_target_name = getattr(entity, 'first_name', match.strip())
                        if getattr(entity, 'username', None):
                            self.radar_target_name += f" (@{entity.username})"
                    except:
                        await safe_edit(e, "<blockquote><b>❌ اليوزر غير صحيح</b></blockquote>")
                        return
                else:
                    await safe_edit(e, "<blockquote><b>⚠️ رد على رسالة الشخص أو استخدم: .بلش @username</b></blockquote>")
                    return
            
            if target_user:
                self.radar_target = target_user
                await safe_edit(e, "<blockquote><b>✅ تم تتبع المستخدم</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.سرعه البلش\s+([+-]?\d*\.?\d+)$"))
        async def set_radar_speed(e):
            if not self.running or self.user_id in banned_users or not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            
            try:
                speed = float(e.pattern_match.group(1))
                if speed < 0:
                    await safe_edit(e, "<blockquote><b>❌ رقم السرعة غير صحيح</b></blockquote>")
                    return
                self.radar_speed = speed
                await safe_edit(e, f"<blockquote><b>✅ تم تحديد سرعة البلش: {speed} ثانية</b></blockquote>")
            except:
                await safe_edit(e, "<blockquote><b>❌ رقم غير صحيح</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.الغاء البلش(?:\s+@?([a-zA-Z0-9_]+))?$"))
        async def stop_radar(e):
            if not self.running or self.user_id in banned_users or not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            
            target_user = None
            
            if e.is_reply:
                reply_msg = await e.get_reply_message()
                if reply_msg and reply_msg.sender_id:
                    target_user = reply_msg.sender_id
            else:
                match = e.pattern_match.group(1)
                if match:
                    try:
                        entity = await self.client.get_entity(match.strip())
                        target_user = entity.id
                    except:
                        await safe_edit(e, "<blockquote><b>❌ اليوزر غير صحيح</b></blockquote>")
                        return
            
            if target_user and self.radar_target == target_user:
                self.radar_target = None
                self.radar_target_name = None
                await safe_edit(e, "<blockquote><b>✅ تم إلغاء تتبع المستخدم</b></blockquote>")
            elif not target_user:
                self.radar_target = None
                self.radar_target_name = None
                await safe_edit(e, "<blockquote><b>✅ تم إلغاء التتبع</b></blockquote>")
            else:
                await safe_edit(e, "<blockquote><b>⚠️ المستخدم غير متتبع</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.م6$"))
        async def destroy_menu(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            text = """
━━━━━━━━━━━━━━━━━━━━━━━━━
🏴‍☠️ أوامر التفليش
━━━━━━━━━━━━━━━━━━━━━━━━━

<code>.تفليش كامل</code> ← طرد جميع الأعضاء وحذف الرسائل (يعمل في المجموعات والقنوات)
<code>.تفليش الحساب</code> ← مغادرة جميع القنوات وحذف القنوات التي أنشأتها

━━━━━━━━━━━━━━━━━━━━━━━━━"""
            await safe_edit(e, text)
        
        @self.client.on(events.NewMessage(pattern=r"^\.تفليش كامل$"))
        async def full_destroy(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            
            # يعمل في المجموعات والقنوات على حد سواء
            try:
                await safe_edit(e, "<blockquote><b>⚠️ جاري تفليش المحادثة...</b></blockquote>")
                
                await self.destroy_group_full(e.chat_id)
                
                # محاولة مسح المحادثة (للمجموعات فقط، لكن لا بأس بتجربتها)
                try:
                    await self.client(DeleteHistoryRequest(e.chat_id, max_id=0, just_clear=False))
                except:
                    pass
                
                await safe_edit(e, "<blockquote><b>✅ تم تفليش المحادثة بنجاح</b></blockquote>")
            except Exception as ex:
                await safe_edit(e, f"<blockquote><b>❌ خطأ: {str(ex)}</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.تفليش الحساب$"))
        async def account_destroy(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            
            if e.chat_id == self.my_id or str(e.chat_id) == "me":
                await safe_edit(e, "<blockquote><b>⚠️ جاري تفليش الحساب</b></blockquote>")
                
                try:
                    result = await self.destroy_account()
                    
                    if result:
                        await safe_edit(e, "<blockquote><b>✅ تم تفليش الحساب</b></blockquote>")
                    else:
                        await safe_edit(e, "<blockquote><b>❌ حدث خطأ أثناء تفليش الحساب</b></blockquote>")
                except Exception as ex:
                    await safe_edit(e, f"<blockquote><b>❌ خطأ: {str(ex)}</b></blockquote>")
            else:
                await safe_edit(e, "<blockquote><b>⚠️ هذا الأمر يكتب في الرسائل المحفوظة</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.م7$"))
        async def monitoring_menu(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            text = """
━━━━━━━━━━━━━━━━━━━━━━━━━
🏴‍☠️ أوامر المراقبة
━━━━━━━━━━━━━━━━━━━━━━━━━

<code>.مراقبه + الرد على رسالة الهدف</code> ← بدء مراقبة المستخدم
<code>.الغاء المراقبه + الرد على رسالة الهدف</code> ← إيقاف مراقبة مستخدم
<code>.الغاء المراقبه</code> ← إيقاف مراقبة جميع المستخدمين في المحادثة

━━━━━━━━━━━━━━━━━━━━━━━━━"""
            await safe_edit(e, text)
        
        @self.client.on(events.NewMessage(pattern=r"^\.مراقبه$"))
        async def start_monitoring_cmd(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            
            target_user_id = None
            target_username = ""
            
            if e.is_reply:
                reply_msg = await e.get_reply_message()
                if reply_msg and reply_msg.sender_id:
                    target_user_id = reply_msg.sender_id
                    try:
                        user = await self.client.get_entity(target_user_id)
                        target_username = user.username if user.username else ""
                    except:
                        pass
            else:
                text = e.raw_text
                match = re.search(r'@([a-zA-Z0-9_]+)', text)
                if match:
                    username = match.group(1)
                    try:
                        user = await self.client.get_entity(username)
                        target_user_id = user.id
                        target_username = username
                    except:
                        await safe_edit(e, "<blockquote><b>⚠️ المستخدم غير موجود</b></blockquote>")
                        return
                else:
                    await safe_edit(e, "<blockquote><b>⚠️ يرجى الرد على رسالة الشخص أو كتابة @username</b></blockquote>")
                    return
            
            if not target_user_id:
                await safe_edit(e, "<blockquote><b>⚠️ لا يمكن تحديد المستخدم</b></blockquote>")
                return
            
            chat_id = e.chat_id
            
            success = await self.start_monitoring(chat_id, target_user_id, target_username)
            
            if success:
                mention = f"@{target_username}" if target_username else f"المستخدم {target_user_id}"
                await safe_edit(e, f"<blockquote><b>✅ بدأت مراقبة {mention} في هذه المحادثة.</b>\nسيتم تنبيهك إذا لم يرسل رسالة لمدة 3 دقائق.</blockquote>")
            else:
                await safe_edit(e, "<blockquote><b>⚠️ هذا المستخدم قيد المراقبة بالفعل في هذه المحادثة</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.(إلغاء_المراقبه|الغاء_المراقبه)$"))
        async def stop_monitoring_cmd(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            
            target_user_id = None
            chat_id = e.chat_id
            
            if e.is_reply:
                reply_msg = await e.get_reply_message()
                if reply_msg and reply_msg.sender_id:
                    target_user_id = reply_msg.sender_id
            else:
                text = e.raw_text
                match = re.search(r'@([a-zA-Z0-9_]+)', text)
                if match:
                    username = match.group(1)
                    try:
                        user = await self.client.get_entity(username)
                        target_user_id = user.id
                    except:
                        await safe_edit(e, "<blockquote><b>⚠️ المستخدم غير موجود</b></blockquote>")
                        return

            if target_user_id:
                success = await self.stop_monitoring(chat_id, target_user_id)
                if success:
                    await safe_edit(e, "<blockquote><b>✅ تم إلغاء مراقبة هذا المستخدم</b></blockquote>")
                else:
                    await safe_edit(e, "<blockquote><b>⚠️ هذا المستخدم غير مراقب في هذه المحادثة</b></blockquote>")
            else:
                await self.stop_all_monitoring(chat_id)
                await safe_edit(e, "<blockquote><b>✅ تم إلغاء مراقبة جميع المستخدمين في هذه المحادثة</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.م8$"))
        async def impersonation_menu(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            text = """
━━━━━━━━━━━━━━━━━━━━━━━━━
🏴‍☠️ أوامر الانتحال
━━━━━━━━━━━━━━━━━━━━━━━━━

<code>.انتحال + بالرد على رسالة الهدف</code> ← ينتحل الصورة والاسم والبايو
<code>.استعاده</code> ← يعيد صورتك الأصلية واسمك الأصلي
<code>.فحص</code> ← يعرض معلومات حسابك وحالة الأوامر المفعلة

━━━━━━━━━━━━━━━━━━━━━━━━━"""
            await safe_edit(e, text)
        
        @self.client.on(events.NewMessage(pattern=r"^\.انتحال$"))
        async def impersonate_cmd(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            
            if e.is_reply:
                reply_msg = await e.get_reply_message()
                if reply_msg and reply_msg.sender_id:
                    target_id = reply_msg.sender_id
                    result = await self.copy_user_profile(target_id)
                    if result:
                        await safe_edit(e, "<blockquote><b>✅ تم الانتحال بنجاح</b></blockquote>")
                    else:
                        await safe_edit(e, "<blockquote><b>❌ فشل الانتحال</b></blockquote>")
                else:
                    await safe_edit(e, "<blockquote><b>⚠️ رد على رسالة الشخص</b></blockquote>")
            else:
                await safe_edit(e, "<blockquote><b>⚠️ رد على رسالة الشخص</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.استعاده$"))
        async def restore_cmd(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            
            result = await self.restore_my_profile()
            if result:
                await safe_edit(e, "<blockquote><b>✅ تم استعادة الحساب الأصلي</b></blockquote>")
            else:
                await safe_edit(e, "<blockquote><b>❌ لا توجد معلومات محفوظة للاستعادة</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.فحص$"))
        async def check_cmd(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            
            me = await self.get_me_safe()
            user_id = self.user_id
            username = f"@{me.username}" if me.username else "لا يوجد"
            
            radar_status = "✅ مفعل" if self.radar_target else "❌ غير مفعل"
            if self.radar_target:
                radar_status += f"\n   الهدف: {self.radar_target_name}"
            
            target_status = "✅ مفعل" if self.target_user_id else "❌ غير مفعل"
            if self.target_user_id:
                try:
                    entity = await self.client.get_entity(self.target_user_id)
                    target_status += f"\n   الهدف: {entity.first_name if entity else self.target_user_id}"
                except:
                    target_status += f"\n   الهدف: {self.target_user_id}"
            
            cliches = [self.cliche_1, self.cliche_2, self.cliche_3]
            cliches = [c for c in cliches if c.strip()]
            cliche_status = f"✅ مفعل ({len(cliches)} كليشات)" if cliches else "❌ غير مفعل"
            if cliches:
                for i, c in enumerate(cliches, 1):
                    cliche_status += f"\n   كليشه {i}: {c[:30]}..."
            
            transfer_status = f"✅ مفعل ({len(self.transfer_messages)} رسائل)" if self.transfer_messages else "❌ غير مفعل"
            
            clock_status = "✅ مفعل" if self.clock else "❌ غير مفعل"
            
            deco_status = "❌ غير مفعل"
            if self.active_decoration:
                deco_names = {
                    "print": "خط برنت",
                    "bold_arabic": "خط عريض",
                    "bold_thick": "خط سميك",
                    "fancy1": "خط انجليزي ¹",
                    "fancy2": "خط انجليزي ²",
                    "fancy3": "خط انجليزي ³",
                    "fancy4": "خط انجليزي ⁴",
                    "tilde_space": "تيلدا"
                }
                deco_status = f"✅ {deco_names.get(self.active_decoration, self.active_decoration)}"
            
            text = f"""
<blockquote><b>📊 معلومات الحساب</b>

👤 اليوزر: {username}
🆔 الايدي: {user_id}

<b>📌 حالة الأوامر:</b>

🎯 <b>تتبع شخص (بلش):</b> {radar_status}
📍 <b>استهداف شخص:</b> {target_status}
📦 <b>الكليشه:</b> {cliche_status}
🔄 <b>التحويل:</b> {transfer_status}
🕐 <b>الاسم الوقتي:</b> {clock_status}
🎨 <b>الزخرفة:</b> {deco_status}

📢 السورس: {CHANNEL_USERNAME}
👨‍💻 المطور: {DEVELOPER_USERNAME}</blockquote>"""
            await safe_edit(e, text)
        
        @self.client.on(events.NewMessage(pattern=r"^\.م9$"))
        async def transfer_menu(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            text = """
━━━━━━━━━━━━━━━━━━━━━━━━━
🏴‍☠️ أوامر التحويل
━━━━━━━━━━━━━━━━━━━━━━━━━

<code>.حفظ التحويل + بالرد على رسالة التحويل</code> ← للحفظ
<code>.الغاء التحويلات</code> ← يلغي جميع التحويلات المحفوظة
<code>.ارسال</code> ← يبدأ إرسال التحويلات
<code>.انهاء</code> ← ينهي إرسال التحويلات
<code>.سرعة التحويل + الرقم</code> ← لتغيير سرعة التحويل (0.1 إلى 20)

━━━━━━━━━━━━━━━━━━━━━━━━━"""
            await safe_edit(e, text)
        
        @self.client.on(events.NewMessage(pattern=r"^\.حفظ التحويل$"))
        async def save_transfer(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            
            if e.is_reply:
                reply_msg = await e.get_reply_message()
                if reply_msg and reply_msg.text:
                    self.transfer_messages.append(reply_msg.text)
                    await safe_edit(e, f"<blockquote><b>✅ تم حفظ التحويل</b>\n<code>{reply_msg.text[:50]}...</code></blockquote>")
                else:
                    await safe_edit(e, "<blockquote><b>⚠️ الرسالة لا تحتوي على نص</b></blockquote>")
            else:
                await safe_edit(e, "<blockquote><b>⚠️ رد على رسالة التحويل</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.الغاء التحويلات$"))
        async def clear_transfers(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            self.transfer_messages.clear()
            await safe_edit(e, "<blockquote><b>✅ تم حذف جميع التحويلات</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.ارسال$"))
        async def start_transfer(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            
            if not self.transfer_messages:
                await safe_edit(e, "<blockquote><b>⚠️ لا توجد تحويلات محفوظة</b></blockquote>")
                return
            
            await self.start_transfer_spam(e)
        
        @self.client.on(events.NewMessage(pattern=r"^\.انهاء$"))
        async def stop_transfer(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            
            self.transfer_sending = False
            if self.transfer_task and not self.transfer_task.done():
                self.transfer_task.cancel()
                self.transfer_task = None
            
            await safe_edit(e, "<blockquote><b>⏹ تم إيقاف إرسال التحويلات</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.سرعة التحويل\s+([+-]?\d*\.?\d+)$"))
        async def set_transfer_speed(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            try:
                speed = float(e.pattern_match.group(1))
                if speed < 0.1:
                    await safe_edit(e, "<blockquote><b>⚠️ السرعة يجب أن تكون أكبر من 0.1</b></blockquote>")
                    return
                if speed > 20:
                    await safe_edit(e, "<blockquote><b>⚠️ السرعة القصوى 20</b></blockquote>")
                    return
                self.transfer_speed = speed
                await safe_edit(e, f"<blockquote><b>✅ تم تحديد سرعة التحويل: {speed} ثانية</b></blockquote>")
            except:
                await safe_edit(e, "<blockquote><b>❌ الرقم غير صحيح</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.الاسم الوقتي$"))
        async def enable_clock(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            
            if self.clock:
                await safe_edit(e, "<blockquote><b>✅ الاسم الوقتي مفعل بالفعل</b></blockquote>")
                return
            
            self.clock = True
            self.clock_timezone = "Africa/Cairo"
            
            if self.clock_task and not self.clock_task.done():
                self.clock_task.cancel()
            
            self.clock_task = asyncio.create_task(self.clock_loop())
            
            try:
                style_num = user_time_style.get(self.user_id, "1")
                time_now = get_real_time_formatted(self.clock_timezone, style_num)
                if time_now:
                    me = await self.get_me_safe()
                    if me:
                        base_name = me.first_name.split("|")[0].strip()
                        bold_time = convert_to_bold_thick(time_now)
                        await self.client(UpdateProfileRequest(first_name=f"{base_name} | {bold_time}"))
            except:
                pass
            
            await safe_edit(e, "<blockquote><b>✅ تم تفعيل الاسم الوقتي في البروفايل</b></blockquote>")
        
        @self.client.on(events.NewMessage(pattern=r"^\.الغاء الاسم الوقتي$"))
        async def disable_clock(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            if not self.is_my_message(e):
                return
            if not await check_subscription_and_reply(e):
                return
            
            if not self.clock:
                await safe_edit(e, "<blockquote><b>❌ الاسم الوقتي غير مفعل</b></blockquote>")
                return
            
            self.clock = False
            if self.clock_task and not self.clock_task.done():
                self.clock_task.cancel()
                self.clock_task = None
            
            try:
                me = await self.get_me_safe()
                if me:
                    base_name = me.first_name.split("|")[0].strip()
                    await self.client(UpdateProfileRequest(first_name=base_name))
            except:
                pass
            
            await safe_edit(e, "<blockquote><b>✅ تم إلغاء الاسم الوقتي من البروفايل</b></blockquote>")
        
        @self.client.on(events.NewMessage)
        async def activity_tracker(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            
            if e.sender_id:
                await self.update_user_activity(e.chat_id, e.sender_id)

        @self.client.on(events.ChatAction)
        async def chat_action_handler(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            
            if e.user_left or e.user_kicked:
                user_id = e.user_id
                chat_id = e.chat_id
                await self.stop_monitoring(chat_id, user_id)

        @self.client.on(events.NewMessage)
        async def auto_reply_handler(e):
            if not self.running:
                return
            
            if self.user_id in banned_users:
                return
            
            if e.sender and hasattr(e.sender, 'bot') and e.sender.bot:
                return
            
            if e.sender_id in self.muted_users:
                try:
                    await e.delete()
                except:
                    pass
                return
            
            if self.auto_reply_text and e.is_private and not e.out:
                if e.sender_id not in self.replied_users:
                    await e.reply(self.auto_reply_text)
                    self.replied_users.add(e.sender_id)
        
        @self.client.on(events.NewMessage)
        async def radar_reply_handler(e):
            if not self.running or self.user_id in banned_users:
                return
            
            if e.out or e.sender_id == self.my_id:
                return
            
            if not self.radar_target:
                return
            
            if e.sender_id == self.radar_target:
                if self.spam_words:
                    reply_text = random.choice(self.spam_words)
                    if self.active_decoration == "tilde_space":
                        reply_text = convert_spaces_to_tilde(reply_text)
                    try:
                        if self.radar_speed > 0:
                            await asyncio.sleep(self.radar_speed)
                        await e.reply(reply_text)
                    except:
                        pass
        
        @self.client.on(events.NewMessage)
        async def decoration_handler(e):
            if not self.running:
                return
            if self.user_id in banned_users:
                return
            
            if e.sender_id != self.my_id:
                return
            
            if e.id in self.processing_message_ids:
                return
            self.processing_message_ids.add(e.id)
            
            try:
                raw_text = e.raw_text
                
                if not raw_text:
                    return
                
                is_command = raw_text.startswith(".") and len(raw_text) > 1
                
                if len(raw_text.strip()) < 1:
                    return
                
                if self.is_already_decorated(raw_text):
                    return
                
                if self.active_decoration and not is_command:
                    decorated_text = self.apply_decoration(raw_text)
                    if decorated_text != raw_text:
                        await e.delete()
                        await self.client.send_message(e.chat_id, decorated_text, reply_to=e.reply_to_msg_id if e.is_reply else None)
                
            except Exception as ex:
                print(f"خطأ في معالج الزخرفة: {ex}")
            finally:
                await asyncio.sleep(0.5)
                self.processing_message_ids.discard(e.id)
        
        @self.client.on(events.NewMessage)
        async def handle_file_messages(e):
            if not self.running:
                return
            
            if self.user_id in banned_users:
                return
            
            if not self.is_my_message(e):
                return
            
            if self.waiting_for_words and e.file:
                path = await e.download_media()
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        self.spam_words.clear()
                        for line in f:
                            if line.strip():
                                self.spam_words.append(line.strip())
                    self.waiting_for_words = False
                    await e.reply(f"<blockquote><b>✅ تم تخزين {len(self.spam_words)} كلمة</b></blockquote>", parse_mode='HTML')
                except Exception as ex:
                    await e.reply("<blockquote><b>❌ خطأ في قراءة الملف</b></blockquote>", parse_mode='HTML')
                finally:
                    if os.path.exists(path):
                        os.remove(path)
    
    async def stop(self):
        self.running = False
        self.sending = False
        if self.spam_task and not self.spam_task.done():
            self.spam_task.cancel()
        if self.clock_task:
            self.clock_task.cancel()
        if self.auto_publish_data["task"] and not self.auto_publish_data["task"].done():
            self.auto_publish_data["task"].cancel()
        self.auto_publish_data["active"] = False
        
        self.cliche_sending = False
        if self.cliche_task and not self.cliche_task.done():
            self.cliche_task.cancel()
        
        self.transfer_sending = False
        if self.transfer_task and not self.transfer_task.done():
            self.transfer_task.cancel()
        
        await self.stop_all_monitoring()
        
        # إزالة المستخدم من قائمة النشطين
        if self.user_id in active_users:
            active_users.discard(self.user_id)
        
        try:
            await self.client.disconnect()
        except:
            pass
        print(f"[{self.session_key[:8]}] تـم ايـقـاف جـلـسـه الـمـسـتـخـدم {self.user_id}")

# ========== دوال البوت الرئيسية ==========
@bot.on(events.NewMessage(pattern="/start"))
async def start(e):
    user_id = e.sender_id
    
    if user_id in banned_users:
        await bot.send_file(
            user_id,
            file=IMAGE_URL,
            caption=f"<blockquote><b>🚫 تم حظرك من البوت.</b>\nللتواصل مع المطور: {DEVELOPER_USERNAME}</blockquote>",
            parse_mode='HTML'
        )
        return
    
    # ===== للمطور =====
    if user_id == OWNER_ID:
        total_users = len(allowed_users)
        user_sessions_count = len(user_clients.get(user_id, []))
        mode_text = "🟢 مجاني" if BOT_MODE == "free" else "🔴 مدفوع"
        caption = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━
👑 لوحة تحكم المطور
━━━━━━━━━━━━━━━━━━━━━━━━━

👥 عدد المستخدمين: {total_users}
📊 عدد جلساتك: {user_sessions_count}
🔧 الوضع الحالي: {mode_text}

━━━━━━━━━━━━━━━━━━━━━━━━━
📌 الأزرار الإدارية:
"""
        buttons = [
            [Button.inline("➕ إضافة جلسة", "addsession")],
            [Button.inline("🔄 تبديل الوضع", "toggle_mode")],
            [
                Button.inline("➕ إضافة اشتراك", "add_subscription"),
                Button.inline("🗑 حذف اشتراك", "delete_subscription")
            ],
            [
                Button.inline("🚫 حظر مستخدم", "banuser"),
                Button.inline("👤 إضافة مستخدم", "adduser")
            ],
            [Button.inline("🔓 فك حظر مستخدم", "unbanuser")],
            [
                Button.inline("✅ تفعيل السورس", "enable_source"),
                Button.inline("❌ تعطيل السورس", "disable_source")
            ],
            [Button.inline("📱 تفعيل بالرقم", "login_phone")],
            [
                Button.inline("📋 جلساتي", "my_sessions"),
                Button.inline("🗑 حذف جلسة", "delete_session")
            ],
            [Button.inline("📢 السورس", "source")]
        ]
        await bot.send_file(
            user_id,
            file=IMAGE_URL,
            caption=caption,
            parse_mode='HTML',
            buttons=buttons
        )
        return
    
    # ===== للمستخدمين العاديين =====
    # التحقق من الاشتراك (إذا كان الوضع مدفوع)
    if not is_subscribed(user_id):
        status, expiry, remaining, sub_type = get_subscription_info(user_id)
        expiry_str = format_expiry(expiry) if expiry else "غير محدد"
        
        if sub_type == "free":
            msg = FREE_TO_PAID_MESSAGE.format(
                day_price=PRICES["day"],
                week_price=PRICES["week"],
                month_price=PRICES["month"],
                year_price=PRICES["year"]
            )
        elif status == "منتهي":
            msg = EXPIRED_MESSAGE.format(expiry_date=expiry_str)
        else:
            msg = UNSUBSCRIBED_MESSAGE.format(
                day_price=PRICES["day"],
                week_price=PRICES["week"],
                month_price=PRICES["month"],
                year_price=PRICES["year"]
            )
        
        buttons = [[Button.inline("📞 تواصل مع المطور", "contact_dev")]]
        await bot.send_file(
            user_id,
            file=IMAGE_URL,
            caption=msg,
            parse_mode='HTML',
            buttons=buttons
        )
        return
    
    # مشترك أو الوضع مجاني
    user_sessions_count = len(user_clients.get(user_id, []))
    caption = USER_COMMANDS.format(
        PROJECT_NAME=PROJECT_NAME,
        sessions_count=user_sessions_count
    )
    buttons = [
        [Button.inline("➕ إضافة جلسة", "addsession")],
        [
            Button.inline("✅ تفعيل السورس", "enable_source"),
            Button.inline("❌ تعطيل السورس", "disable_source")
        ],
        [Button.inline("📱 تفعيل بالرقم", "login_phone")],
        [
            Button.inline("📋 جلساتي", "my_sessions"),
            Button.inline("🗑 حذف جلسة", "delete_session")
        ],
        [Button.inline("📢 السورس", "source")]
    ]
    await bot.send_file(
        user_id,
        file=IMAGE_URL,
        caption=caption,
        parse_mode='HTML',
        buttons=buttons
    )

@bot.on(events.NewMessage(pattern="/request"))
async def request(e):
    user_id = e.sender_id
    
    if user_id in banned_users:
        await e.reply("<blockquote><b>🚫 تم حظرك من البوت.</b></blockquote>", parse_mode='HTML')
        return
    
    buttons = [
        [Button.inline("📞 تواصل مع المطور", "contact_dev")]
    ]
    await e.reply(
        f"<blockquote><b>📩 للتواصل مع المطور والاشتراك:</b>\n\n<b>👨‍💻 المطور: {DEVELOPER_USERNAME}</b>\n<b>📌 اضغط على الزر أدناه للتواصل.</b></blockquote>",
        parse_mode='HTML',
        buttons=buttons
    )

@bot.on(events.NewMessage(pattern="/source"))
async def source(e):
    user_id = e.sender_id
    
    if user_id in banned_users:
        await e.reply("<blockquote><b>🚫 تم حظرك من البوت</b></blockquote>", parse_mode='HTML')
        return
    
    # متاح للجميع (حتى غير المشتركين)
    source_text = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━
📢 معلومات السورس
━━━━━━━━━━━━━━━━━━━━━━━━━

📢 قناة السورس: {CHANNEL_USERNAME}
👨‍💻 المطور: {DEVELOPER_USERNAME}
🤖 البوت: {BOT_USERNAME}

━━━━━━━━━━━━━━━━━━━━━━━━━
📌 اضغط على الأزرار للدخول مباشرة:
"""
    
    buttons = [
        [Button.url("📢 قناة السورس", CHANNEL_LINK)],
        [Button.url("🤖 بوت السورس", BOT_LINK)],
        [Button.url("👨‍💻 المطور", DEVELOPER_LINK)]
    ]
    
    await bot.send_file(
        user_id,
        file=IMAGE_URL,
        caption=source_text,
        parse_mode='HTML',
        buttons=buttons
    )

@bot.on(events.NewMessage(pattern="/sessions"))
async def list_sessions(e):
    user_id = e.sender_id
    
    if user_id in banned_users:
        await e.reply("<blockquote><b>🚫 تم حظرك من البوت</b></blockquote>", parse_mode='HTML')
        return
    
    if user_id not in allowed_users and user_id != OWNER_ID:
        return
    
    sessions = user_clients.get(user_id, [])
    if not sessions:
        await e.reply("<blockquote><b>📭 لا توجد جلسات نشطة.</b></blockquote>", parse_mode='HTML')
        return
    
    session_list = []
    for i, session in enumerate(sessions):
        try:
            me = await session.get_me_safe()
            if me:
                name = me.first_name
            else:
                name = "الحساب"
        except:
            name = "الحساب"
        session_list.append(f"• الجلسة {i+1} ↤ {name} (أرسل /stop_session {i+1} لإيقافها)")
    
    text = f"<blockquote><b>📊 جلساتي النشطة</b>\n\n{chr(10).join(session_list)}\n\n<b>عدد الجلسات: {len(sessions)}</b></blockquote>"
    await e.reply(text, parse_mode='HTML')

@bot.on(events.NewMessage(pattern="/stop_session (\\d+)"))
async def stop_session(e):
    user_id = e.sender_id
    
    if user_id in banned_users:
        await e.reply("<blockquote><b>🚫 تم حظرك من البوت</b></blockquote>", parse_mode='HTML')
        return
    
    if user_id not in allowed_users and user_id != OWNER_ID:
        return
    
    try:
        session_index = int(e.pattern_match.group(1)) - 1
        sessions = user_clients.get(user_id, [])
        
        if 0 <= session_index < len(sessions):
            session = sessions[session_index]
            await session.stop()
            sessions.pop(session_index)
            await e.reply("<blockquote><b>✅ تم إيقاف الجلسة بنجاح.</b></blockquote>", parse_mode='HTML')
        else:
            await e.reply("<blockquote><b>❌ رقم الجلسة غير صحيح.</b></blockquote>", parse_mode='HTML')
    except:
        await e.reply("<blockquote><b>⚠️ حدث خطأ أثناء إيقاف الجلسة.</b></blockquote>", parse_mode='HTML')

async def delete_session_completely(session, user_id):
    try:
        session.clock = False
        if session.clock_task and not session.clock_task.done():
            session.clock_task.cancel()
            try:
                await session.clock_task
            except asyncio.CancelledError:
                pass
        
        session.sending = False
        if session.spam_task and not session.spam_task.done():
            session.spam_task.cancel()
            try:
                await session.spam_task
            except asyncio.CancelledError:
                pass
        
        if session.auto_publish_data.get("task") and not session.auto_publish_data["task"].done():
            session.auto_publish_data["task"].cancel()
            try:
                await session.auto_publish_data["task"]
            except asyncio.CancelledError:
                pass
        session.auto_publish_data["active"] = False
        
        session.cliche_sending = False
        if session.cliche_task and not session.cliche_task.done():
            session.cliche_task.cancel()
            try:
                await session.cliche_task
            except asyncio.CancelledError:
                pass
        
        session.transfer_sending = False
        if session.transfer_task and not session.transfer_task.done():
            session.transfer_task.cancel()
            try:
                await session.transfer_task
            except asyncio.CancelledError:
                pass
        
        await session.stop_all_monitoring()

        session.running = False
        
        # إزالة من active_users
        if session.user_id in active_users:
            active_users.discard(session.user_id)
        
        try:
            await session.client.disconnect()
        except Exception:
            pass
        
        if session in all_clients:
            all_clients.remove(session)
        
        if user_id in user_clients:
            if session in user_clients[user_id]:
                user_clients[user_id].remove(session)
            if not user_clients[user_id]:
                del user_clients[user_id]
        
        return True
    except Exception as ex:
        print(f"خطأ في حذف الجلسة: {ex}")
        return False

@bot.on(events.NewMessage(pattern="/delsession"))
async def delsession_command(e):
    user_id = e.sender_id
    
    if user_id in banned_users:
        await e.reply("<blockquote><b>🚫 تم حظرك من البوت</b></blockquote>", parse_mode='HTML')
        return
    
    if user_id not in allowed_users and user_id != OWNER_ID:
        return
    
    sessions = user_clients.get(user_id, [])
    if not sessions:
        await e.reply("<blockquote><b>📭 لا توجد جلسات لحذفها.</b></blockquote>", parse_mode='HTML')
        return
    
    buttons = []
    for i, session in enumerate(sessions):
        try:
            me = await session.get_me_safe()
            name = me.first_name if me else f"جلسة {i+1}"
        except:
            name = f"جلسة {i+1}"
        buttons.append([Button.inline(
            f"🗑 حذف {name}",
            f"del_session_{i}"
        )])
    
    buttons.append([Button.inline("❌ إلغاء", "cancel_del")])
    
    await e.reply(
        "<blockquote><b>🗑 اختر الجلسة التي تريد حذفها نهائياً.</b>\n<b>⚠️ سيتم إيقاف جميع مهامها وقطع الاتصال.</b></blockquote>",
        parse_mode='HTML',
        buttons=buttons
    )

@bot.on(events.NewMessage)
async def handle_session_messages(e):
    user_id = e.sender_id
    
    if user_id in waiting_sessions:
        session_string = e.raw_text.strip()
        waiting_sessions.pop(user_id)
        
        try:
            client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
            await client.connect()
            me = await client.get_me()
            
            session_key = str(uuid.uuid4())
            user_session = UserbotSession(client, user_id, session_key)
            
            all_clients.append(user_session)
            if user_id not in user_clients:
                user_clients[user_id] = []
            user_clients[user_id].append(user_session)
            
            await e.reply(f"<blockquote><b>✅ تمت الإضافة</b>\n👤 الحساب: {me.first_name}\n📊 عدد جلساتك: {len(user_clients.get(user_id, []))}\n📌 استخدم /sessions لعرض الجلسات.</blockquote>", parse_mode='HTML')
            
        except Exception as ex:
            await e.reply(f"<blockquote><b>⚠️ حدث خطأ: {str(ex)}</b></blockquote>", parse_mode='HTML')

@bot.on(events.NewMessage)
async def handle_phone_login(e):
    user_id = e.sender_id
    text = e.raw_text.strip()
    
    if user_id in waiting_phone:
        phone = text
        waiting_phone.pop(user_id)
        
        try:
            client = TelegramClient(StringSession(), API_ID, API_HASH)
            await client.connect()
            
            sent = await client.send_code_request(phone)
            phone_clients[user_id] = {
                "client": client,
                "phone": phone,
                "phone_code_hash": sent.phone_code_hash
            }
            waiting_code[user_id] = True
            
            await e.reply("<blockquote><b>📱 تم إرسال كود التحقق.</b>\n<b>📲 أرسل الكود الذي وصل إليك.</b></blockquote>", parse_mode='HTML')
        except Exception as ex:
            await e.reply(f"<blockquote><b>⚠️ خطأ: {str(ex)}</b></blockquote>", parse_mode='HTML')
    
    elif user_id in waiting_code:
        code = text
        waiting_code.pop(user_id)
        
        client_data = phone_clients.get(user_id)
        if not client_data:
            await e.reply("<blockquote><b>⚠️ حدث خطأ، حاول مرة أخرى.</b></blockquote>", parse_mode='HTML')
            return
        
        client = client_data["client"]
        phone = client_data["phone"]
        phone_code_hash = client_data["phone_code_hash"]
        
        try:
            await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
            me = await client.get_me()
            
            session_key = str(uuid.uuid4())
            user_session = UserbotSession(client, user_id, session_key)
            user_session.source_enabled = True
            
            all_clients.append(user_session)
            if user_id not in user_clients:
                user_clients[user_id] = []
            user_clients[user_id].append(user_session)
            
            if user_id in phone_clients:
                del phone_clients[user_id]
            
            await e.reply(f"<blockquote><b>✅ تمت الإضافة</b>\n👤 الحساب: {me.first_name}\n📊 عدد جلساتك: {len(user_clients.get(user_id, []))}\n📌 استخدم /sessions لعرض الجلسات.</blockquote>", parse_mode='HTML')
        
        except Exception as ex:
            err_str = str(ex)
            if "SessionPasswordNeededError" in err_str or "password" in err_str.lower():
                waiting_2fa[user_id] = True
                await e.reply("<blockquote><b>🔐 يتطلب حسابك كلمة مرور التحقق الثنائي.</b>\n<b>📝 أرسل كلمة المرور.</b></blockquote>", parse_mode='HTML')
            else:
                if user_id in phone_clients:
                    del phone_clients[user_id]
                await e.reply(f"<blockquote><b>⚠️ خطأ: {err_str}</b></blockquote>", parse_mode='HTML')
    
    elif user_id in waiting_2fa:
        password = text
        waiting_2fa.pop(user_id)
        
        client_data = phone_clients.get(user_id)
        if not client_data:
            await e.reply("<blockquote><b>⚠️ حدث خطأ، حاول مرة أخرى.</b></blockquote>", parse_mode='HTML')
            return
        
        client = client_data["client"]
        
        try:
            from telethon.errors import PasswordHashInvalidError
            await client.sign_in(password=password)
            me = await client.get_me()
            
            session_key = str(uuid.uuid4())
            user_session = UserbotSession(client, user_id, session_key)
            user_session.source_enabled = True
            
            all_clients.append(user_session)
            if user_id not in user_clients:
                user_clients[user_id] = []
            user_clients[user_id].append(user_session)
            
            if user_id in phone_clients:
                del phone_clients[user_id]
            
            await e.reply(f"<blockquote><b>✅ تمت الإضافة</b>\n👤 الحساب: {me.first_name}\n📊 عدد جلساتك: {len(user_clients.get(user_id, []))}\n📌 استخدم /sessions لعرض الجلسات.</blockquote>", parse_mode='HTML')
        
        except Exception as ex:
            if user_id in phone_clients:
                del phone_clients[user_id]
            await e.reply(f"<blockquote><b>⚠️ كلمة المرور غير صحيحة: {str(ex)}</b></blockquote>", parse_mode='HTML')

@bot.on(events.NewMessage)
async def handle_admin_requests(e):
    user_id = e.sender_id
    
    if user_id in waiting_user_add:
        try:
            target_user_id = int(e.raw_text.strip())
            allowed_users.add(target_user_id)
            waiting_user_add.remove(user_id)
            await e.reply(f"<blockquote><b>✅ تمت الإضافة</b>\n👤 تم إضافة المستخدم {target_user_id} بنجاح.</blockquote>", parse_mode='HTML')
        except:
            await e.reply("<blockquote><b>⚠️ معرف غير صحيح.</b></blockquote>", parse_mode='HTML')
    
    elif user_id in waiting_user_ban:
        try:
            target_user_id = int(e.raw_text.strip())
            banned_users.add(target_user_id)
            waiting_user_ban.remove(user_id)
            await e.reply(f"<blockquote><b>🚫 تم الحظر</b>\n👤 تم حظر المستخدم {target_user_id} بنجاح.</blockquote>", parse_mode='HTML')
        except:
            await e.reply("<blockquote><b>⚠️ معرف غير صحيح.</b></blockquote>", parse_mode='HTML')
    
    elif user_id in waiting_user_unban:
        try:
            target_user_id = int(e.raw_text.strip())
            if target_user_id in banned_users:
                banned_users.remove(target_user_id)
            waiting_user_unban.remove(user_id)
            await e.reply(f"<blockquote><b>🔓 تم فك الحظر</b>\n👤 تم فك حظر المستخدم {target_user_id} بنجاح.</blockquote>", parse_mode='HTML')
        except:
            await e.reply("<blockquote><b>⚠️ معرف غير صحيح.</b></blockquote>", parse_mode='HTML')

@bot.on(events.CallbackQuery)
async def callback_handler(e):
    user_id = e.sender_id
    data = e.data.decode('utf-8')
    
    # ===== تبديل الوضع (للمطور فقط) =====
    if data == "toggle_mode":
        if user_id != OWNER_ID:
            await e.answer("متاح فقط للمطور", alert=True)
            return
        
        global BOT_MODE
        if BOT_MODE == "free":
            BOT_MODE = "paid"
            await e.answer("تم التحويل للوضع المدفوع 🔴", alert=True)
            
            # إرسال إشعار للمستخدمين النشطين
            msg = FREE_TO_PAID_MESSAGE.format(
                day_price=PRICES["day"],
                week_price=PRICES["week"],
                month_price=PRICES["month"],
                year_price=PRICES["year"]
            )
            buttons = [[Button.inline("📞 تواصل مع المطور", "contact_dev")]]
            await notify_all_users(msg, buttons)
        else:
            BOT_MODE = "free"
            await e.answer("تم التحويل للوضع المجاني 🟢", alert=True)
        
        # إعادة تحميل لوحة المطور
        await bot.send_message(user_id, "/start")
        await e.answer()
        return
    
    # ===== إضافة اشتراك (للمطور فقط) =====
    if data == "add_subscription":
        if user_id != OWNER_ID:
            await e.answer("متاح فقط للمطور", alert=True)
            return
        
        waiting_subscription_input[user_id] = "add"
        await e.edit(
            "<blockquote><b>📤 أرسل معرف المستخدم وعدد الأيام مفصولين بمسافة.</b>\n<b>مثال: 8484588712 30</b></blockquote>",
            parse_mode='HTML'
        )
        await e.answer()
        return
    
    # ===== حذف اشتراك (للمطور فقط) =====
    if data == "delete_subscription":
        if user_id != OWNER_ID:
            await e.answer("متاح فقط للمطور", alert=True)
            return
        
        waiting_subscription_input[user_id] = "delete"
        await e.edit(
            "<blockquote><b>📤 أرسل معرف المستخدم لحذف اشتراكه.</b>\n<b>مثال: 8484588712</b></blockquote>",
            parse_mode='HTML'
        )
        await e.answer()
        return
    
    # ===== زر تواصل مع المطور (متاح للجميع) =====
    if data == "contact_dev":
        await e.answer("جاري فتح المطور...", alert=True)
        await bot.send_message(
            user_id,
            f"<blockquote><b>📞 تواصل مع المطور:</b>\n\n👨‍💻 {DEVELOPER_USERNAME}\n🔗 {DEVELOPER_LINK}</blockquote>",
            parse_mode='HTML',
            buttons=[[Button.url("📩 اضغط للتواصل", DEVELOPER_LINK)]]
        )
        await e.answer()
        return
    
    # ===== الأزرار العامة (متاحة للمشتركين أو الوضع المجاني) =====
    # التحقق من الصلاحية: إذا لم يكن المطور وليس مشتركاً والوضع مدفوع، نمنع
    if user_id != OWNER_ID and not is_subscribed(user_id):
        await e.answer("غير مشترك، يرجى الاشتراك أولاً", alert=True)
        return
    
    # الآن الأزرار العامة
    if data == "addsession":
        waiting_sessions[user_id] = True
        await e.edit("<blockquote><b>📤 أرسل سترينج الجلسة.</b></blockquote>", parse_mode='HTML')
    
    elif data == "enable_source":
        sessions = user_clients.get(user_id, [])
        if not sessions:
            await e.answer("لا توجد جلسات مضافه", alert=True)
            return
        
        for session in sessions:
            session.source_enabled = True
        
        await e.edit("<blockquote><b>✅ تم التفعيل</b>\n<b>🔧 تم تفعيل السورس.</b>\n<b>📌 جميع الأوامر تعمل الآن.</b></blockquote>", parse_mode='HTML')
    
    elif data == "disable_source":
        sessions = user_clients.get(user_id, [])
        if not sessions:
            await e.answer("لا توجد جلسات مضافه", alert=True)
            return
        
        for session in sessions:
            session.source_enabled = False
        
        await e.edit("<blockquote><b>❌ تم التعطيل</b>\n<b>🔧 تم تعطيل السورس.</b>\n<b>📌 الأوامر موقوفة مؤقتاً.</b>\n<b>📌 استخدم 'تفعيل السورس' لإعادة التشغيل.</b></blockquote>", parse_mode='HTML')
    
    elif data == "login_phone":
        waiting_phone[user_id] = True
        await e.edit("<blockquote><b>📲 أرسل رقم الهاتف مع الكود الدولي.</b>\n<b>مثال: +9665xxxxxxxx</b></blockquote>", parse_mode='HTML')
    
    elif data.startswith("del_session_"):
        try:
            session_index = int(data.split("del_session_")[1])
            sessions = user_clients.get(user_id, [])
            
            if 0 <= session_index < len(sessions):
                session = sessions[session_index]
                try:
                    me = await session.get_me_safe()
                    acc_name = me.first_name if me else "الحساب"
                except:
                    acc_name = "الحساب"
                
                success = await delete_session_completely(session, user_id)
                
                if success:
                    await e.edit(f"<blockquote><b>🗑 تم الحذف</b>\n<b>✅ تم حذف جلسة {acc_name} نهائياً.</b>\n<b>🔄 تم إيقاف جميع مهامها وقطع الاتصال.</b></blockquote>", parse_mode='HTML')
                else:
                    await e.answer("حدث خطأ أثناء الحذف", alert=True)
            else:
                await e.answer("رقم الجلسة غير صحيح", alert=True)
        except Exception as ex:
            await e.answer(f"خطأ: {str(ex)}", alert=True)
    
    elif data == "cancel_del":
        await e.edit("<blockquote><b>❌ تم الإلغاء</b>\n<b>✅ تم إلغاء عملية الحذف.</b></blockquote>", parse_mode='HTML')
    
    elif data == "my_sessions":
        sessions = user_clients.get(user_id, [])
        if not sessions:
            await e.edit("<blockquote><b>📭 لا توجد جلسات نشطة.</b></blockquote>", parse_mode='HTML')
            return
        
        session_list = []
        for i, session in enumerate(sessions):
            try:
                me = await session.get_me_safe()
                if me:
                    name = me.first_name
                else:
                    name = "الحساب"
            except:
                name = "الحساب"
            session_list.append(f"• الجلسة {i+1} ↤ {name} (أرسل /stop_session {i+1} لإيقافها)")
        
        text = f"<blockquote><b>📊 جلساتي النشطة</b>\n\n{chr(10).join(session_list)}\n\n<b>عدد الجلسات: {len(sessions)}</b></blockquote>"
        await e.edit(text, parse_mode='HTML')
    
    elif data == "source":
        source_text = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━
📢 معلومات السورس
━━━━━━━━━━━━━━━━━━━━━━━━━

📢 قناة السورس: {CHANNEL_USERNAME}
👨‍💻 المطور: {DEVELOPER_USERNAME}
🤖 البوت: {BOT_USERNAME}

━━━━━━━━━━━━━━━━━━━━━━━━━
📌 اضغط على الأزرار للدخول مباشرة:
"""
        buttons = [
            [Button.url("📢 قناة السورس", CHANNEL_LINK)],
            [Button.url("🤖 بوت السورس", BOT_LINK)],
            [Button.url("👨‍💻 المطور", DEVELOPER_LINK)]
        ]
        await e.edit(source_text, parse_mode='HTML', buttons=buttons)
    
    elif data == "delete_session":
        sessions = user_clients.get(user_id, [])
        if not sessions:
            await e.edit("<blockquote><b>📭 لا توجد جلسات لحذفها.</b></blockquote>", parse_mode='HTML')
            return
        
        buttons = []
        for i, session in enumerate(sessions):
            try:
                me = await session.get_me_safe()
                name = me.first_name if me else f"جلسة {i+1}"
            except:
                name = f"جلسة {i+1}"
            buttons.append([Button.inline(
                f"🗑 حذف {name}",
                f"del_session_{i}"
            )])
        
        buttons.append([Button.inline("❌ إلغاء", "cancel_del")])
        
        await e.edit(
            "<blockquote><b>🗑 اختر الجلسة التي تريد حذفها نهائياً.</b>\n<b>⚠️ سيتم إيقاف جميع مهامها وقطع الاتصال.</b></blockquote>",
            parse_mode='HTML',
            buttons=buttons
        )
    
    # ===== الأزرار الإدارية (للمطور فقط) =====
    elif data == "adduser":
        if user_id != OWNER_ID:
            await e.answer("متاح فقط للمطور", alert=True)
            return
        waiting_user_add.add(user_id)
        await e.edit("<blockquote><b>📤 أرسل معرف المستخدم لتفعيله.</b></blockquote>", parse_mode='HTML')
    
    elif data == "banuser":
        if user_id != OWNER_ID:
            await e.answer("متاح فقط للمطور", alert=True)
            return
        waiting_user_ban.add(user_id)
        await e.edit("<blockquote><b>📤 أرسل معرف المستخدم لحظره.</b></blockquote>", parse_mode='HTML')
    
    elif data == "unbanuser":
        if user_id != OWNER_ID:
            await e.answer("متاح فقط للمطور", alert=True)
            return
        waiting_user_unban.add(user_id)
        await e.edit("<blockquote><b>📤 أرسل معرف المستخدم لفك حظره.</b></blockquote>", parse_mode='HTML')
    
    elif data.startswith("acc_"):
        if user_id != OWNER_ID:
            await e.answer("متاح فقط للمطور", alert=True)
            return
        target_user = int(data.split("_")[1])
        allowed_users.add(target_user)
        if target_user in pending_requests:
            del pending_requests[target_user]
        
        await e.edit(f"<blockquote><b>✅ تم القبول</b>\n👤 تم تفعيل المستخدم {target_user}.</blockquote>", parse_mode='HTML')
        
        try:
            await bot.send_message(target_user, "<blockquote><b>✅ تم تفعيل حسابك.</b>\n<b>📌 استخدم /start لتشغيل البوت.</b></blockquote>", parse_mode='HTML')
        except:
            pass
    
    elif data.startswith("rej_"):
        if user_id != OWNER_ID:
            await e.answer("متاح فقط للمطور", alert=True)
            return
        target_user = int(data.split("_")[1])
        if target_user in pending_requests:
            del pending_requests[target_user]
        
        await e.edit(f"<blockquote><b>❌ تم الرفض</b>\n👤 تم رفض المستخدم {target_user}.</blockquote>", parse_mode='HTML')
        
        try:
            await bot.send_message(target_user, f"<blockquote><b>❌ تم رفض طلبك.</b>\n<b>للتواصل مع المطور: {DEVELOPER_USERNAME}</b></blockquote>", parse_mode='HTML')
        except:
            pass

# ===== معالج استقبال بيانات الاشتراكات من المطور =====
@bot.on(events.NewMessage)
async def handle_subscription_input(e):
    user_id = e.sender_id
    
    if user_id in waiting_subscription_input:
        action = waiting_subscription_input.pop(user_id)
        text = e.raw_text.strip()
        
        if action == "add":
            parts = text.split()
            if len(parts) != 2:
                await e.reply("<blockquote><b>⚠️ الصيغة غير صحيحة.\n📌 استخدم: معرف المستخدم عدد الأيام</b></blockquote>", parse_mode='HTML')
                return
            
            try:
                target_user = int(parts[0])
                days = int(parts[1])
                if days <= 0:
                    await e.reply("<blockquote><b>⚠️ عدد الأيام يجب أن يكون أكبر من 0</b></blockquote>", parse_mode='HTML')
                    return
                
                new_expiry = extend_subscription(target_user, days, "paid")
                expiry_str = format_expiry(new_expiry)
                
                # إشعار للمطور
                await e.reply(
                    f"<blockquote><b>✅ تم إضافة اشتراك للمستخدم {target_user}</b>\n"
                    f"📦 المدة: {days} يوم\n"
                    f"📆 تاريخ الانتهاء: {expiry_str}</blockquote>",
                    parse_mode='HTML'
                )
                
                # إرسال إشعار للمستخدم المستهدف
                try:
                    notify_msg = f"""<blockquote><b>🎉 تم تفعيل اشتراكك في البوت!</b>

📦 المدة: {days} يوم
📆 ينتهي في: {expiry_str}

🏴‍☠️ يمكنك الآن استخدام جميع أوامر البوت.
🏴‍☠️ للاستعلام عن اشتراكك استخدم /start.

شكراً لاشتراكك! ❤️</blockquote>"""
                    await bot.send_message(target_user, notify_msg, parse_mode='HTML')
                except Exception as ex:
                    print(f"فشل إرسال إشعار للمستخدم {target_user}: {ex}")
                
            except ValueError:
                await e.reply("<blockquote><b>⚠️ المعرف أو عدد الأيام غير صحيح</b></blockquote>", parse_mode='HTML')
        
        elif action == "delete":
            try:
                target_user = int(text)
                if delete_subscription(target_user):
                    await e.reply(f"<blockquote><b>✅ تم حذف اشتراك المستخدم {target_user}</b></blockquote>", parse_mode='HTML')
                else:
                    await e.reply(f"<blockquote><b>⚠️ المستخدم {target_user} ليس لديه اشتراك</b></blockquote>", parse_mode='HTML')
            except ValueError:
                await e.reply("<blockquote><b>⚠️ المعرف غير صحيح</b></blockquote>", parse_mode='HTML')

print(f"تم تشغيل {PROJECT_NAME} بنجاح")
print(f"المطور: {DEVELOPER_USERNAME}")
print(f"الوضع الحالي: {BOT_MODE}")
print("البوت يعمل الآن...")
bot.run_until_disconnected()