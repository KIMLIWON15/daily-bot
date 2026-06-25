import os
import requests
from bs4 import BeautifulSoup
import datetime
import urllib.parse
import xml.etree.ElementTree as ET

# --- [1. 날씨 정보 (풀옵션)] ---
def get_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=37.2639&longitude=127.0286&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=Asia%2FSeoul"
        res = requests.get(url).json()
        
        current = res["current"]
        daily = res["daily"]
        
        temp = current["temperature_2m"]
        feels_like = current["apparent_temperature"]
        humidity = current["relative_humidity_2m"]
        wind = current["wind_speed_10m"]
        code = current["weather_code"]
        
        temp_max = daily["temperature_2m_max"][0]
        temp_min = daily["temperature_2m_min"][0]
        precip_prob = daily["precipitation_probability_max"][0]
        
        weather = "맑음 ☀️"
        if code in [1, 2, 3]: weather = "구름 ☁️"
        elif code in [45, 48]: weather = "안개 🌫️"
        elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]: weather = "비 🌧️"
        elif code in [71, 73, 75, 77, 85, 86]: weather = "눈 ❄️"
        
        weather_text = (
            f"🌡️ 현재: {temp}°C (체감 {feels_like}°C) / {weather}\n"
            f"📈 최저/최고: {temp_min}°C / {temp_max}°C\n"
            f"☔ 강수 확률: {precip_prob}%\n"
            f"💧 습도: {humidity}% / 💨 풍속: {wind}km/h"
        )
        return weather_text
    except: return "⚠️ 날씨 정보를 불러오지 못했습니다."

# --- [2. 증시 및 매크로 지표 (야후 파이낸스 API)] ---
def fetch_yahoo_data(ticker, is_crypto=False):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers).json()
        meta = res['chart']['result'][0]['meta']
        price = meta['regularMarketPrice']
        prev = meta['chartPreviousClose']
        change = price - prev
        rate = (change / prev) * 100
        sign = "▲" if change > 0 else "▼" if change < 0 else "-"
        
        if is_crypto:
            return f"{price:,.0f} ({sign} {abs(rate):.2f}%)"
        return f"{price:,.2f} ({sign} {abs(rate):.2f}%)"
    except: return "N/A"

def get_market_data():
    dji = fetch_yahoo_data("^DJI")
    spx = fetch_yahoo_data("^GSPC")
    ndx = fetch_yahoo_data("^IXIC")
    sox = fetch_yahoo_data("^SOX")
    
    nvda = fetch_yahoo_data("NVDA")
    tsla = fetch_yahoo_data("TSLA")
    aapl = fetch_yahoo_data("AAPL")
    
    usdkrw = fetch_yahoo_data("KRW=X")
    tnx = fetch_yahoo_data("^TNX")
    wti = fetch_yahoo_data("CL=F")
    vix = fetch_yahoo_data("^VIX")
    btc = fetch_yahoo_data("BTC-USD", is_crypto=True)
    ewy = fetch_yahoo_data("EWY")
    
    macro_text = (
        f"[미국 주요 지수]\n"
        f"• 다우존스: {dji}\n• S&P500: {spx}\n• 나스닥: {ndx}\n• 필라델피아 반도체: {sox}\n\n"
        f"[주요 빅테크]\n"
        f"• 엔비디아: {nvda}\n• 테슬라: {tsla}\n• 애플: {aapl}\n\n"
        f"[글로벌 매크로 & 자금 흐름]\n"
        f"• 원/달러 환율: {usdkrw}\n• 미국채 10년물: {tnx}\n• WTI 국제유가: {wti}\n"
        f"• VIX 공포지수: {vix}\n• 비트코인: {btc}\n• MSCI 한국 ETF: {ewy}"
    )
    return macro_text

# --- [3. 국내 증시 관전 포인트 (네이버 시황 기사)] ---
def get_korea_market_focus():
    try:
        url = "https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        soup = BeautifulSoup(requests.get(url, headers=headers).content.decode('euc-kr', 'replace'), "html.parser")
        
        subjects = soup.select(".articleSubject a")
        results = []
        for a in subjects[:3]:
            title = a.text.strip()
            link = "https://finance.naver.com" + a.get("href")
            results.append(f"• {title}\n🔗 {link}")
        return "\n\n".join(results)
    except: return "⚠️ 국내 증시 관전 포인트를 불러오지 못했습니다."

# --- [4. 맞춤형 뉴스 크롤러 (통합 RSS 및 카테고리)] ---
def search_keyword_news(query, count=2):
    """구글 뉴스 RSS를 XML 파서로 완벽하게 읽어와 네이버/다음 뉴스를 차단 없이 검색합니다."""
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
        
        res = requests.get(url)
        # HTML 파서 대신 파이썬 내장 XML 파서 사용 (링크 실종 버그 완벽 해결)
        root = ET.fromstring(res.text)
        
        items = root.findall('.//item')
        results = []
        for item in items[:count]:
            title = item.find('title').text.strip()
            link = item.find('link').text.strip()
            results.append(f"• {title}\n🔗 {link}")
            
        if not results:
            return f"⚠️ '{query}' 관련 최신 뉴스가 없습니다."
            
        return "\n\n".join(results)
    except Exception as e:
        return f"⚠️ '{query}' 뉴스를 불러오지 못했습니다."

def get_category_news(sid1, count=3):
    """네이버 속보 카테고리(경제/사회)를 가져옵니다."""
    try:
        url = f"https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1={sid1}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        soup = BeautifulSoup(requests.get(url, headers=headers).text, "html.parser")
        
        links = soup.select(".list_body a")
        results = []
        seen = set()
        for link in links:
            title = link.text.strip()
            href = link.get("href")
            if title and len(title) > 10 and title not in seen:
                seen.add(title)
                results.append(f"• {title}\n🔗 {href}")
                if len(results) == count: break
        return "\n\n".join(results)
    except: return "⚠️ 카테고리 뉴스를 불러오지 못했습니다."

def get_boannews(count=3):
    """보안뉴스(boannews.com) 메인 기사를 가져옵니다."""
    try:
        url = "https://www.boannews.com/media/t_list.asp"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        soup = BeautifulSoup(requests.get(url, headers=headers).text, "html.parser")
        
        items = soup.select(".news_list")
        results = []
        for item in items[:count]:
            title = item.select_one(".news_txt").text.strip()
            link = "https://www.boannews.com" + item.select_one("a").get("href")
            results.append(f"• {title}\n🔗 {link}")
        return "\n\n".join(results)
    except: return "⚠️ 보안뉴스 정보를 불러오지 못했습니다."

def get_all_news():
    news_parts = []
    news_parts.append(f"🛡️ [국내 보안이슈 (보안뉴스)]\n{get_boannews(3)}")
    news_parts.append(f"🏢 [보안회사 동향]\n{search_keyword_news('보안회사 OR 정보보안기업', 2)}")
    news_parts.append(f"🔐 [제로트러스트 & N2FS]\n{search_keyword_news('제로트러스트 OR N2FS', 2)}")
    news_parts.append(f"📈 [오늘의 경제]\n{get_category_news('101', 3)}")
    news_parts.append(f"👥 [오늘의 사회]\n{get_category_news('102', 3)}")
    return "\n\n━━━━━━━━━━━━━━━\n\n".join(news_parts)

# --- [5. 텔레그램 전송] ---
def send_telegram_message(text):
    bot_token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("❌ 에러: 깃허브 Secrets 설정 확인 필요")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True # 긴 뉴스 미리보기 방지
    }
    
    requests.post(url, json=payload)

def run():
    now = datetime.datetime.now()
    date_str = now.strftime('%Y년 %m월 %d일 %H:%M')
    
    print("데이터 수집 시작...")
    weather = get_weather()
    market_macro = get_market_data()
    market_focus = get_korea_market_focus()
    news = get_all_news()
    
    message = (
        f"📊 [{date_str}] 인텔리전스 브리핑\n\n"
        f"📍 [오늘의 수원 날씨]\n{weather}\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"🌐 [글로벌 증시 & 매크로]\n{market_macro}\n\n"
        f"🎯 [국내 증시 관전 포인트]\n{market_focus}\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{news}"
    )
    
    print("텔레그램 발송 중...")
    send_telegram_message(message)
    print("브리핑 전송 완료!")

if __name__ == "__main__":
    run()
