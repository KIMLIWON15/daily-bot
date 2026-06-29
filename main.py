import os
import requests
from bs4 import BeautifulSoup
import datetime
import urllib.parse
import xml.etree.ElementTree as ET
import html
import random  # 랜덤 로테이션을 위해 추가

# --- [1. 날씨 정보 (수원 기준)] ---
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
    except Exception as e: 
        return f"⚠️ 날씨 정보를 불러오지 못했습니다. ({e})"

# --- [2. 증시 및 매크로 지표] ---
def get_korea_index(ticker_code, is_stock=False):
    try:
        if is_stock: url = f"https://m.stock.naver.com/api/stock/{ticker_code}/basic"
        else: url = f"https://m.stock.naver.com/api/index/{ticker_code}/basic"
            
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        res = requests.get(url, headers=headers).json()
        
        num = res['closePrice']
        change = res['compareToPreviousClosePrice']
        rate = res['fluctuationsRatio']
        code = res['compareToPreviousPrice']['code']
        sign = "▲" if code == "2" else "▼" if code == "5" else "-"
        return f"{num} ({sign} {change} / {rate}%)"
    except: return "확인 불가"

def fetch_yahoo_data(ticker, is_crypto=False):
    try:
        url = f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers).json()
        meta = res['chart']['result'][0]['meta']
        price = meta['regularMarketPrice']
        prev = meta['chartPreviousClose']
        change = price - prev
        rate = (change / prev) * 100
        sign = "▲" if change > 0 else "▼" if change < 0 else "-"
        
        if is_crypto: return f"{price:,.0f} ({sign} {abs(rate):.2f}%)"
        return f"{price:,.2f} ({sign} {abs(rate):.2f}%)"
    except: return "확인 불가"

def get_market_data():
    kospi = get_korea_index("KOSPI")
    kosdaq = get_korea_index("KOSDAQ")
    samsung = get_korea_index("005930", is_stock=True)
    hynix = get_korea_index("000660", is_stock=True)
    lgensol = get_korea_index("373220", is_stock=True)
    hyundai = get_korea_index("005380", is_stock=True)
    kia = get_korea_index("000270", is_stock=True)
    
    dji = fetch_yahoo_data("^DJI")
    ndx = fetch_yahoo_data("^IXIC")
    sox = fetch_yahoo_data("^SOX")
    usdkrw = fetch_yahoo_data("KRW=X")
    tnx = fetch_yahoo_data("^TNX")
    btc = fetch_yahoo_data("BTC-USD", is_crypto=True)
    
    macro_text = (
        f"<b>[국내 주요 지수 및 톱픽]</b>\n"
        f"• 코스피: {kospi}\n• 코스닥: {kosdaq}\n"
        f"• 삼성전자: {samsung}\n• SK하이닉스: {hynix}\n• 현대차: {hyundai}\n\n"
        f"<b>[미국 지수 & 글로벌 매크로]</b>\n"
        f"• 나스닥: {ndx}\n• 필라델피아 반도체: {sox}\n"
        f"• 원/달러 환율: {usdkrw}\n• 미국채 10년물: {tnx}\n• 비트코인: {btc}"
    )
    return macro_text

# --- [3. 통합 뉴스 크롤러 모음] ---
def get_korea_market_focus(count=5):
    try:
        url = "https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258"
        headers = {"User-Agent": "Mozilla/5.0"}
        soup = BeautifulSoup(requests.get(url, headers=headers).content.decode('euc-kr', 'replace'), "html.parser")
        
        subjects = soup.select(".articleSubject a")
        results = []
        for a in subjects[:count]:
            title = html.escape(a.text.strip())
            link = "https://finance.naver.com" + a.get("href")
            results.append(f"• <a href='{link}'>{title}</a>")
        return "\n".join(results)
    except: return "⚠️ 국내 증시 포인트를 불러오지 못했습니다."

def search_keyword_news(query, count=5):
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
        res = requests.get(url)
        root = ET.fromstring(res.text)
        
        items = root.findall('.//item')
        results = []
        for item in items[:count]:
            title = html.escape(item.find('title').text.strip())
            link = item.find('link').text.strip()
            results.append(f"• <a href='{link}'>{title}</a>")
            
        if not results: return f"⚠️ '{query}' 관련 최신 뉴스가 없습니다."
        return "\n".join(results)
    except: return f"⚠️ '{query}' 뉴스를 불러오지 못했습니다."

def get_boannews(count=5):
    try:
        url = "https://www.boannews.com/media/news_rss.xml"
        res = requests.get(url)
        res.encoding = res.apparent_encoding
        root = ET.fromstring(res.text)
        
        items = root.findall('.//item')
        results = []
        target_keywords = ['제로트러스트', 'N2SF', '망분리', '다중계층', '서버보안', 'AI보안'] 
        
        for item in items:
            title = item.find('title').text
            link = item.find('link').text
            if any(kw.lower() in title.lower() for kw in target_keywords):
                safe_title = html.escape(title.strip())
                results.append(f"• 🚨 <a href='{link}'>{safe_title}</a>")
                if len(results) >= count: break
                
        if len(results) < count:
            for item in items:
                title = item.find('title').text
                link = item.find('link').text
                safe_title = html.escape(title.strip())
                formatted_link = f"• <a href='{link}'>{safe_title}</a>"
                if formatted_link not in results and not formatted_link.startswith("• 🚨"):
                    results.append(formatted_link)
                if len(results) >= count: break
        return "\n".join(results)
    except: return "⚠️ 보안 속보를 불러오지 못했습니다."

# --- [4. 통합 뉴스 구성 (메가 트렌드 & 20대 기업 로테이션)] ---
def get_all_news():
    news_parts = []
    
    # 1. 보안뉴스 속보 (RSS 직접 크롤링)
    news_parts.append(f"<b>⚡ [보안 전문매체 속보]</b>\n{get_boannews(4)}")
    
    # 2. 5대 메가 트렌드 통합 검색
    mega_trends_query = "제로트러스트 OR N2SF OR 망분리 OR 클라우드보안 OR 통합보안"
    news_parts.append(f"<b>🛡️ [보안업계 메가 트렌드 동향]</b>\n{search_keyword_news(mega_trends_query, 5)}")
    
    # 3. 20대 보안 기업 로테이션 검색 (가장 중요한 SGA솔루션즈는 고정, 나머지는 2곳 랜덤 추첨)
    k_security_20 = [
        "안랩", "SK쉴더스", "이글루코퍼레이션", "시큐아이", 
        "휴네시온", "피앤피시큐어", "넷앤드", "윈스", "파이오링크",
        "모니터랩", "프라이빗테크놀로지", "파수", "지니언스", "소만사",
        "지란지교시큐리티", "라온시큐어", "케이사인", "드림시큐리티", "펜타시큐리티"
    ]
    random_picks = random.sample(k_security_20, 2)
    spotlight_companies = ["SGA솔루션즈"] + random_picks
    company_query = " OR ".join(spotlight_companies)
    
    news_parts.append(f"<b>🏢 [오늘의 보안기업 Spotlight: {', '.join(spotlight_companies)}]</b>\n{search_keyword_news(company_query, 5)}")
    
    # 4. 오늘의 경제/사회 포인트 (구글 뉴스 기반 검색으로 대체하여 속도/안정성 향상)
    news_parts.append(f"<b>📈 [오늘의 경제 주요 뉴스]</b>\n{search_keyword_news('금리 OR 수출 OR 주식 OR 부동산', 4)}")
    news_parts.append(f"<b>👥 [오늘의 사회 주요 뉴스]</b>\n{search_keyword_news('정책 OR IT교육 OR 날씨 OR 사회', 4)}")
    
    return "\n\n━━━━━━━━━━━━━━━\n\n".join(news_parts)

# --- [5. 텔레그램 전송] ---
def send_telegram_message(text):
    bot_token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id: return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML", 
        "disable_web_page_preview": True
    }
    requests.post(url, json=payload)

def run():
    kst_now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    date_str = kst_now.strftime('%Y년 %m월 %d일 %H:%M')
    
    weather = get_weather()
    market_macro = get_market_data()
    market_focus = get_korea_market_focus(4)
    news = get_all_news()
    
    message = (
        f"📊 <b>[{date_str}] 인텔리전스 브리핑</b>\n\n"
        f"📍 <b>[수원 날씨]</b>\n{weather}\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{market_macro}\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"🎯 <b>[국내 증시 관전 포인트]</b>\n{market_focus}\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{news}"
    )
    
    send_telegram_message(message)

if __name__ == "__main__":
    run()
