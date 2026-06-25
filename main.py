import os
import requests
from bs4 import BeautifulSoup
import datetime

def get_weather():
    """오픈 날씨 API를 통해 수원 지역의 현재 날씨를 정확하게 가져옵니다."""
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=37.2639&longitude=127.0286&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m&timezone=Asia%2FSeoul"
        res = requests.get(url).json()
        current = res["current"]
        
        temp = current["temperature_2m"]
        humidity = current["relative_humidity_2m"]
        wind = current["wind_speed_10m"]
        code = current["weather_code"]
        
        weather_status = "맑음"
        if code in [1, 2, 3]: weather_status = "구름 조금"
        elif code in [45, 48]: weather_status = "안개"
        elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]: weather_status = "비 🌧️"
        elif code in [71, 73, 75, 77, 85, 86]: weather_status = "눈 ❄️"
        elif code in [95, 96, 99]: weather_status = "천둥번개 ⚡"
        
        return f"🌡️ 온도: {temp}°C ({weather_status})\n💧 습도: {humidity}% / 💨 풍속: {wind} km/h"
    except Exception as e:
        return "⚠️ 기상 API 통신 장애로 날씨를 불러오지 못했습니다."

def get_stock():
    """네이버 금융 메인 페이지에서 코스피, 코스닥 지수를 가장 확실한 정공법으로 크롤링합니다."""
    try:
        url = "https://finance.naver.com/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.content.decode('euc-kr', 'replace'), "html.parser")
        
        # 1. 코스피 정보 추출 (블라인드 텍스트 포함 정교한 파싱)
        kospi_area = soup.find("div", {"class": "kospi_area"})
        k_num = kospi_area.find("span", {"class": "num"}).text.strip()
        # 상승/하락 기호와 수치 결합
        k_change = kospi_area.find("span", {"class": "num_s2"}).text.strip()
        k_change = k_change.replace("상승", "▲ ").replace("하락", "▼ ").replace("보합", "")
        
        # 2. 코스닥 정보 추출
        kosdaq_area = soup.find("div", {"class": "kosdaq_area"})
        kd_num = kosdaq_area.find("span", {"class": "num"}).text.strip()
        kd_change = kosdaq_area.find("span", {"class": "num_s2"}).text.strip()
        kd_change = kd_change.replace("상승", "▲ ").replace("하락", "▼ ").replace("보합", "")
        
        return f"📈 코스피: {k_num} ({k_change})\n📉 코스닥: {kd_num} ({kd_change})"
    except Exception as e:
        return "⚠️ 증시 정보를 불러오지 못했습니다."

def get_news():
    """네이버 뉴스 속보 페이지에서 주요 헤드라인 5개를 크롤링합니다."""
    try:
        url = "https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1=001"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        
        list_body = soup.find("div", {"class": "list_body"})
        news_links = list_body.find_all("a")
        
        headlines = []
        seen_titles = set()
        
        for link in news_links:
            title = link.text.strip()
            href = link.get("href")
            
            if title and len(title) > 10 and title not in seen_titles:
                seen_titles.add(title)
                headlines.append(f"• {title}\n🔗 {href}")
                if len(headlines) == 5:
                    break
                    
        return "\n\n".join(headlines)
    except Exception as e:
        return "⚠️ 뉴스 헤드라인을 불러오지 못했습니다."

def send_telegram_message(text):
    """텔레그램으로 최종 조립된 메시지를 전송합니다."""
    bot_token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("❌ 에러: 깃허브 Secrets 설정 확인 필요")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True
    }
    
    requests.post(url, json=payload)

def run():
    now = datetime.datetime.now()
    date_str = now.strftime('%Y년 %m월 %d일 %H:%M')
    
    print("데이터 수집 시작...")
    weather_info = get_weather()
    stock_info = get_stock()
    news_info = get_news()
    
    message = (
        f"☀️ [{date_str}] 아침 브리핑\n\n"
        f"📍 [오늘의 수원 날씨]\n{weather_info}\n\n"
        f"📊 [주요 증시 현황]\n{stock_info}\n\n"
        f"📰 [실시간 뉴스 헤드라인]\n{news_info}"
    )
    
    print("텔레그램 발송 중...")
    send_telegram_message(message)
    print("브리핑 전송 완료!")

if __name__ == "__main__":
    run()
