import os
import requests
from bs4 import BeautifulSoup
import datetime

def get_weather():
    """네이버에서 수원 날씨 정보를 크롤링합니다."""
    try:
        # 수원 날씨 검색 결과 페이지
        url = "https://search.naver.com/search.naver?query=%EC%88%98%EC%9B%90+%EB%82%A0%C3%94%B8"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 현재 온도 및 날씨 상태 추출
        temperature = soup.find("div", {"class": "temperature_text"}).text.strip().replace("현재 온도", "")
        weather_status = soup.find("span", {"class": "weather before_slash"}).text.strip()
        
        # 미세먼지 정보 추출
        today_chart = soup.find("ul", {"class": "today_chart_list"})
        dust = today_chart.find_all("li")[0].find("span", {"class": "txt"}).text.strip() # 미세먼지
        ultra_dust = today_chart.find_all("li")[1].find("span", {"class": "txt"}).text.strip() # 초미세먼지
        
        return f"🌡️ 온도: {temperature} ({weather_status})\n😷 미세먼지: {dust} / 초미세: {ultra_dust}"
    except Exception as e:
        return "⚠️ 날씨 정보를 불러오지 못했습니다."

def get_stock():
    """네이버 페이 증시에서 코스피, 코스닥 지수를 크롤링합니다."""
    try:
        url = "https://finance.naver.com/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        res = requests.get(url, headers=headers)
        # 네이버 금융은 EUC-KR 인코딩을 주로 사용하므로 깨짐 방지 처리를 합니다.
        soup = BeautifulSoup(res.content.decode('euc-kr', 'replace'), "html.parser")
        
        # 코스피 정보
        kospi_area = soup.find("div", {"class": "kospi_area"})
        kospi_num = kospi_area.find("span", {"class": "num"}).text.strip()
        kospi_change = kospi_area.find("span", {"class": "num_s2"}).text.strip()
        
        # 코스닥 정보
        kosdaq_area = soup.find("div", {"class": "kosdaq_area"})
        kosdaq_num = kosdaq_area.find("span", {"class": "num"}).text.strip()
        kosdaq_change = kosdaq_area.find("span", {"class": "num_s2"}).text.strip()
        
        return f"📈 코스피: {kospi_num} ({kospi_change})\n📉 코스닥: {kosdaq_num} ({kosdaq_change})"
    except Exception as e:
        return "⚠️ 증시 정보를 불러오지 못했습니다."

def get_news():
    """네이버 뉴스 속보 페이지에서 주요 헤드라인 5개를 크롤링합니다."""
    try:
        url = "https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1=001" # 속보 전체
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 뉴스 리스트 영역 찾기
        list_body = soup.find("div", {"class": "list_body"})
        news_links = list_body.find_all("a")
        
        headlines = []
        seen_titles = set()
        
        for link in news_links:
            title = link.text.strip()
            href = link.get("href")
            
            # 빈 제목이나 이미지 링크, 중복 제목 필터링
            if title and len(title) > 10 and title not in seen_titles:
                seen_titles.add(title)
                headlines.append(f"• {title}\n🔗 {href}")
                if len(headlines) == 5: # 딱 5개만 수집
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
        "disable_web_page_preview": True # 뉴스 링크 미리보기가 너무 길게 뜨는 것을 방지
    }
    
    requests.post(url, json=payload)

def run():
    now = datetime.datetime.now()
    date_str = now.strftime('%Y년 %m월 %d일 %H:%M')
    
    print("데이터 수집 시작...")
    weather_info = get_weather()
    stock_info = get_stock()
    news_info = get_news()
    
    # 텔레그램으로 보낼 알림 본문 조립
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
