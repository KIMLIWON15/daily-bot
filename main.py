import os
import requests
from bs4 import BeautifulSoup
import datetime
import urllib.parse
import xml.etree.ElementTree as ET
import html

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

# --- [2. 증시 및 매크로 지표] ---
def get_korea_index(ticker_code, is_stock=False):
    """네이버 모바일 공식 API로 국내 지수 및 종목 시세를 차단 없이 가져옵니다."""
    try:
        if is_stock:
            url = f"https://m.stock.naver.com/api/stock/{ticker_code}/basic"
        else:
            url = f"https://m.stock.naver.com/api/index/{ticker_code}/basic"
            
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
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"}
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
    except: return "확인 불가"

def get_market_data():
    kospi = get_korea_index("KOSPI")
    kosdaq = get_korea_index("KOSDAQ")
    
    samsung = get_korea_index("005930", is_stock=True)   # 삼성전자
    hynix = get_korea_index("000660", is_stock=True)     # SK하이닉스
    lgensol = get_korea_index("373220", is_stock=True)  # LG에너지솔루션
    hyundai = get_korea_index("005380", is_stock=True)   # 현대차
    kia = get_korea_index("000270", is_stock=True)       # 기아
    celltrion = get_korea_index("068270", is_stock=True) # 셀트리온
    sambao = get_korea_index("207940", is_stock=True)    # 삼성바이오로직스
    naver = get_korea_index("035420", is_stock=True)     # NAVER
    kakao = get_korea_index("035720", is_stock=True)     # 카카오
    alteogen = get_korea_index("196170", is_stock=True)  # 알테오젠
    
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
        f"[국내 주요 지수]\n"
        f"• 코스피: {kospi}\n• 코스닥: {kosdaq}\n\n"
        f"[국내 주요 종목 10선]\n"
        f"• 삼성전자: {samsung}\n• SK하이닉스: {hynix}\n• LG에너지솔루션: {lgensol}\n"
        f"• 현대차: {hyundai}\n• 기아: {kia}\n• 셀트리온: {celltrion}\n"
        f"• 삼성바이오: {sambao}\n• NAVER: {naver}\n• 카카오: {kakao}\n"
        f"• 알테오젠: {alteogen}\n\n"
        f"[미국 주요 지수]\n"
        f"• 다우존스: {dji}\n• S&P500: {spx}\n• 나스닥: {ndx}\n• 필라델피아 반도체: {sox}\n\n"
        f"[주요 빅테크]\n"
        f"• 엔비디아: {nvda}\n• 테슬라: {tsla}\n• 애플: {aapl}\n\n"
        f"[글로벌 매크로 & 자금 흐름]\n"
        f"• 원/달러 환율: {usdkrw}\n• 미국채 10년물: {tnx}\n• WTI 국제유가: {wti}\n"
        f"• VIX 공포지수: {vix}\n• 비트코인: {btc}\n• MSCI 한국 ETF: {ewy}"
    )
    return macro_text

# --- [3. 국내 증시 관전 포인트] ---
def get_korea_market_focus():
    try:
        url = "https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        soup = BeautifulSoup(requests.get(url, headers=headers).content.decode('euc-kr', 'replace'), "html.parser")
        
        subjects = soup.select(".articleSubject a")
        results = []
        for a in subjects[:3]:
            title = html.escape(a.text.strip())
            link = "https://finance.naver.com" + a.get("href")
            results.append(f"• <a href='{link}'>{title}</a>")
        return "\n\n".join(results)
    except: return "⚠️ 국내 증시 관전 포인트를 불러오지 못했습니다."

# --- [4. 맞춤형 뉴스 크롤러 (통합 우회 검색)] ---
def search_keyword_news(query, count=2):
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
            
        if not results:
            return f"⚠️ '{query}' 관련 최신 뉴스가 없습니다."
            
        return "\n\n".join(results)
    except Exception as e:
        return f"⚠️ '{query}' 뉴스를 불러오지 못했습니다."

def get_category_news(sid1, count=3):
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
                safe_title = html.escape(title)
                results.append(f"• <a href='{href}'>{safe_title}</a>")
                if len(results) == count: break
        return "\n\n".join(results)
    except: return "⚠️ 카테고리 뉴스를 불러오지 못했습니다."

# --- [4-1. 전문 매체 (보안뉴스) 속보 크롤러] ---
def get_boannews(count=3):
    """보안뉴스 RSS에서 핵심 키워드(제로트러스트, N2FS 등) 기사를 가장 먼저 가져옵니다."""
    try:
        url = "https://www.boannews.com/media/news_rss.xml"
        res = requests.get(url)
        res.encoding = res.apparent_encoding # 인코딩 깨짐 방지
        root = ET.fromstring(res.text)
        
        items = root.findall('.//item')
        results = []
        
        target_keywords = ['제로트러스트', 'N2FS', '망분리', '다중계층', 'MLS', '보안가이드'] 
        
        # 1순위: 타겟 키워드가 포함된 기사 탐색
        for item in items:
            title = item.find('title').text
            link = item.find('link').text
            if any(kw in title.upper() for kw in target_keywords):
                safe_title = html.escape(title.strip())
                results.append(f"• 🚨 <a href='{link}'>{safe_title}</a>")
                if len(results) >= count: break
        
        # 2순위: 키워드 기사가 부족하면 일반 최신 보안 속보로 채움
        if len(results) < count:
            for item in items:
                title = item.find('title').text
                link = item.find('link').text
                safe_title = html.escape(title.strip())
                formatted_link = f"• <a href='{link}'>{safe_title}</a>"
                
                if formatted_link not in results and not formatted_link.startswith("• 🚨"):
                    results.append(formatted_link)
                if len(results) >= count: break
                
        return "\n\n".join(results)
    except Exception as e:
        return "⚠️ 보안 전문 매체 속보를 불러오지 못했습니다."

# --- [4-2. 통합 뉴스 구성] ---
def get_all_news():
    news_parts = []
    
    # 1. 속도 최우선: 보안 매체 직접 크롤링 (키워드 매칭 시 강조)
    news_parts.append(f"⚡ [보안뉴스 최신 속보]\n{get_boannews(3)}")
    
    # 2. 정확도 및 정책 동향: 구글 검색 키워드 고도화
    news_parts.append(f"🛡️ [제로트러스트 & N2FS 종합 동향]\n{search_keyword_news('제로트러스트 OR N2FS OR 망분리 OR 다중계층보안', 3)}")
    
    # 3. 경쟁사/업계 동향
    news_parts.append(f"🏢 [보안회사 동향]\n{search_keyword_news('보안회사 OR 정보보안기업', 2)}")
    
    # 4. 일반 뉴스
    news_parts.append(f"📈 [오늘의 경제]\n{get_category_news('101', 3)}")
    news_parts.append(f"👥 [오늘의 사회]\n{get_category_news('102', 3)}")
    
    return "\n\n━━━━━━━━━━━━━━━\n\n".join(news_parts)

# --- [5. 텔레그램 전송 (HTML 모드)] ---
def send_telegram_message(text):
    bot_token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("❌ 에러: 환경 변수(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID) 설정 확인 필요")
        return

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
    
    print("데이터 수집 시작...")
    weather = get_weather()
    market_macro = get_market_data()
    market_focus = get_korea_market_focus()
    news = get_all_news()
    
    message = (
        f"📊 [{date_str}] 인텔리전스 브리핑\n\n"
        f"📍 [오늘의 수원 날씨]\n{weather}\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"🌐 [증시 & 매크로 지표]\n{market_macro}\n\n"
        f"🎯 [국내 증시 관전 포인트]\n{market_focus}\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{news}"
    )
    
    print("텔레그램 발송 중...")
    send_telegram_message(message)
    print("브리핑 전송 완료!")

if __name__ == "__main__":
    run()
