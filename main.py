import os
import requests
from bs4 import BeautifulSoup
import datetime

# --- [1. 날씨 정보] ---
def get_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=37.2639&longitude=127.0286&current=temperature_2m,relative_humidity_2m,weather_code&timezone=Asia%2FSeoul"
        res = requests.get(url).json()["current"]
        
        temp = res["temperature_2m"]
        code = res["weather_code"]
        
        weather = "맑음 ☀️"
        if code in [1, 2, 3]: weather = "구름 ☁️"
        elif code in [45, 48]: weather = "안개 🌫️"
        elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]: weather = "비 🌧️"
        elif code in [71, 73, 75, 77, 85, 86]: weather = "눈 ❄️"
        
        return f"🌡️ 온도: {temp}°C ({weather})"
    except: return "⚠️ 날씨 정보를 불러오지 못했습니다."

# --- [2. 증시 및 매크로 지표 파서 (야후 파이낸스 API)] ---
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
    # 1. 미국 3대 지수 & 필라델피아 반도체
    dji = fetch_yahoo_data("^DJI")
    spx = fetch_yahoo_data("^GSPC")
    ndx = fetch_yahoo_data("^IXIC")
    sox = fetch_yahoo_data("^SOX")
    
    # 2. 빅테크 동향
    nvda = fetch_yahoo_data("NVDA")
    tsla = fetch_yahoo_data("TSLA")
    aapl = fetch_yahoo_data("AAPL")
    
    # 3. 시장 지표 (환율, 금리, 유가, VIX, 비트코인)
    usdkrw = fetch_yahoo_data("KRW=X")
    tnx = fetch_yahoo_data("^TNX") # 10년물 금리는 % 자체가 price
    wti = fetch_yahoo_data("CL=F")
    vix = fetch_yahoo_data("^VIX")
    btc = fetch_yahoo_data("BTC-USD", is_crypto=True)
    ewy = fetch_yahoo_data("EWY") # MSCI 한국지수 ETF
    
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
        url = "https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258" # 시황/전망
        headers = {"User-Agent": "Mozilla/5.0"}
        soup = BeautifulSoup(requests.get(url, headers=headers).content.decode('euc-kr', 'replace'), "html.parser")
        
        subjects = soup.select(".articleSubject a")
        results = []
        for a in subjects[:3]: # 상위 3개 시황
            results.append(f"• {a.text.strip()}")
        return "\n".join(results)
    except: return "⚠️ 국내 증시 관전 포인트를 불러오지 못했습니다."

# --- [4. 맞춤형 뉴스 크롤러] ---
def search_naver_news(query, count=2):
    """네이버 뉴스 검색 결과를 가져옵니다."""
    try:
        url = f"https://search.naver.com/search.naver?where=news&query={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        soup = BeautifulSoup(requests.get(url, headers=headers).text, "html.parser")
        
        items = soup.select(".news_tit")
        results = []
        for item in items[:count]:
            title = item.text.strip()
            link = item.get("href")
            results.append(f"• {title}\n🔗 {link}")
        return "\n".join(results)
    except: return f"⚠️ '{query}' 뉴스를 불러오지 못했습니다."

def get_category_news(sid1, count=3):
    """네이버 속보 카테고리(경제/사회)를 가져옵니다."""
    try:
        url = f"https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1={sid1}"
        headers = {"User-Agent": "Mozilla/5.0"}
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
        return "\n".join(results)
    except: return "⚠️ 카테고리 뉴스를 불러오지 못했습니다."

def get_boannews(count=3):
    """보안뉴스(boannews.com) 메인 기사를 가져옵니다."""
    try:
        url = "https://www.boannews.com/media/t_list.asp"
        headers = {"User-Agent": "Mozilla/5.0"}
        soup = BeautifulSoup(requests.get(url, headers=headers).text, "html.parser")
        
        items = soup.select(".news_list")
        results = []
        for item in items[:count]:
            title = item.select_one(".news_txt").text.strip()
            link = "https://www.boannews.com" + item.select_one("a").get("href")
            results.append(f"• {title}\n🔗 {link}")
        return "\n".join(results)
    except: return "⚠️ 보안뉴스 정보를 불러오지 못했습니다."

def get_all_news():
    news_parts = []
    news_parts.append(f"🛡️ [국내 보안이슈 (보안뉴스)]\n{get_boannews(3)}")
    news_parts.append(f"🏢 [보안회사 동향]\n{search_naver_news('보안회사 OR 정보보안기업', 2)}")
    news_parts.append(f"🔐 [제로트러스트 & N2FS]\n{search_naver_news('제로트러스트 OR N2FS', 3)}")
    news_parts.append(f"📈 [오늘의 경제]\n{get_category_news('101', 3)}")
    news_parts.append(f"👥 [오늘의 사회]\n{get_category_news('102', 3)}")
    return "\n\n".join(news_parts)

# --- [5. 텔레그램 전송] ---
def send_telegram_message(text):
    bot_token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
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
        f"━━━━━━━━━━━━━━━\n"
        f"🌐 [글로벌 증시 & 매크로]\n{market_macro}\n\n"
        f"🎯 [국내 증시 관전 포인트 (시황)]\n{market_focus}\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{news}"
    )
    
    print("텔레그램 발송 중...")
    send_telegram_message(message)
    print("브리핑 전송 완료!")

if __name__ == "__main__":
    run()
