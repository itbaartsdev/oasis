import random
import string
import re
import requests

def create_random_device_info():
    """Membuat informasi device yang random dengan lebih banyak variasi"""
    devices = [
        # Windows
        "Windows NT 10.0; Win64; x64",
        "Windows NT 11.0; Win64; x64", 
        "Windows NT 10.0; WOW64",
        "Windows NT 6.3; Win64; x64",
        "Windows NT 6.2; Win64; x64",
        # Mac
        "Macintosh; Intel Mac OS X 10_15_7",
        "Macintosh; Intel Mac OS X 11_6_0",
        "Macintosh; Intel Mac OS X 12_0_1",
        "Macintosh; Intel Mac OS X 13_2_1",
        "Macintosh; Apple M1 Mac OS X 11_6_2",
        "Macintosh; Apple M2 Mac OS X 13_0_1",
        # Linux
        "X11; Linux x86_64",
        "X11; Ubuntu; Linux x86_64",
        "X11; Fedora; Linux x86_64",
        "X11; Debian; Linux x86_64",
        "X11; Linux armv7l",
        "X11; CentOS; Linux x86_64",
        # Mobile
        "iPhone; CPU iPhone OS 15_0 like Mac OS X",
        "iPad; CPU OS 16_0 like Mac OS X", 
        "Linux; Android 12; SM-G991B",
        "Linux; Android 13; Pixel 6"
    ]
    
    browsers = [
        # Chrome
        "Chrome/119.0.0.0",
        "Chrome/120.0.0.0",
        "Chrome/121.0.0.0",
        "Chrome/122.0.6261.69",
        "Chrome/123.0.6312.58",
        # Firefox
        "Firefox/120.0",
        "Firefox/121.0",
        "Firefox/122.0",
        "Firefox/123.0",
        "Firefox/124.0",
        # Safari
        "Safari/537.36",
        "Safari/605.1.15",
        "Safari/602.1",
        "Version/16.0 Safari/605.1.15",
        "Version/17.0 Safari/605.1.15",
        # Edge
        "Edg/120.0.0.0",
        "Edg/121.0.0.0",
        "Edg/122.0.0.0",
        "Edge/120.0.0.0",
        "Edge/121.0.2277.128",
        # Opera
        "Opera/90.0.4480.84",
        "Opera/91.0.4516.20",
        "Opera/92.0.4561.43",
        "OPR/94.0.0.0",
        "OPR/95.0.0.0",
        # Brave
        "Brave Chrome/120.0.0.0",
        "Brave Chrome/121.0.0.0",
        "Brave Chrome/122.0.0.0",
        # Vivaldi
        "Vivaldi/6.1.3035.111",
        "Vivaldi/6.2.3105.48",
        "Vivaldi/6.3.3185.3"
    ]
    
    device = random.choice(devices)
    browser = random.choice(browsers)
    
    if "iPhone" in device or "iPad" in device:
        return f"Mozilla/5.0 ({device}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 {browser}"
    elif "Android" in device:
        return f"Mozilla/5.0 ({device}) AppleWebKit/537.36 (KHTML, like Gecko) {browser} Mobile Safari/537.36"
    else:
        return f"Mozilla/5.0 ({device}) AppleWebKit/537.36 (KHTML, like Gecko) {browser}"

def get_random_headers(proxy_ip=None):
    languages = ['en-US,en;q=0.9', 'en-GB,en;q=0.8']  # Hapus id-ID
    timezones = ['America/New_York', 'Europe/London', 'Asia/Singapore', 'Asia/Tokyo']
    location_info = {
        'timezone': random.choice(timezones),
        'countryCode': 'US'
    }
    
    # Dapatkan informasi lokasi dari IP proxy
    if proxy_ip:
        try:
            response = requests.get(f"http://ip-api.com/json/{proxy_ip}", timeout=5)
            if response.ok:
                location_info = response.json()
        except:
            pass  # Gunakan default jika gagal

    headers = {
        'User-Agent': create_random_device_info(),
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': random.choice(languages),
        'Accept-Encoding': 'gzip, deflate, br',
        'Origin': 'https://dashboard.oasis.ai',
        'Referer': 'https://dashboard.oasis.ai/',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'X-Requested-With': 'XMLHttpRequest',
        'X-Forwarded-For': proxy_ip if proxy_ip else f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
        'X-Real-IP': proxy_ip if proxy_ip else f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
        'CF-IPCountry': location_info.get('countryCode', 'US'),
        'X-Timezone': location_info.get('timezone', random.choice(timezones))
    }
    
    return headers
