import os
import requests
import datetime
import time

# 🎯 감시할 주식 종목 (10개 카테고리 x 5종목 = 총 50개)
TARGET_CATEGORIES = {
    "💻 [반도체 & 장비]": {
        "005930": "삼성전자", "000660": "SK하이닉스", "042700": "한미반도체", "058470": "리노공업", "036930": "주성엔지니어링"
    },
    "🌐 [IT & 플랫폼 & 통신]": {
        "035420": "NAVER", "035720": "카카오", "018260": "삼성SDS", "017670": "SK텔레콤", "030200": "KT"
    },
    "🧬 [제약 & 바이오]": {
        "207940": "삼성바이오로직스", "068270": "셀트리온", "196170": "알테오젠", "028300": "HLB", "000100": "유한양행"
    },
    "🔋 [2차전지 & 소재]": {
        "373220": "LG에너지솔루션", "006400": "삼성SDI", "051910": "LG화학", "247540": "에코프로비엠", "086520": "에코프로"
    },
    "🚗 [자동차 & 부품]": {
        "005380": "현대차", "000270": "기아", "012330": "현대모비스", "011210": "현대위아", "018880": "한온시스템"
    },
    "🛡️ [방산 & 우주항공]": {
        "012450": "한화에어로스페이스", "047810": "한국항공우주", "064350": "현대로템", "079550": "LIG넥스원", "272210": "한화시스템"
    },
    "🚢 [조선 & 해운 & 기계]": {
        "009540": "HD현대중공업", "042660": "한화오션", "329180": "HD한국조선해양", "010140": "삼성중공업", "011200": "HMM"
    },
    "🏦 [금융 & 지주사]": {
        "055550": "신한지주", "105560": "KB금융", "086790": "하나금융지주", "138040": "메리츠금융지주", "032830": "삼성생명"
    },
    "🎬 [엔터 & 화장품]": {
        "352820": "하이브", "041510": "에스엠", "035900": "JYP Ent.", "090430": "아모레퍼시픽", "051900": "LG생활건강"
    },
    "🏗️ [건설 & 철강 & 에너지]": {
        "000720": "현대건설", "006360": "GS건설", "004020": "현대제철", "010130": "고려아연", "015760": "한국전력"
    }
}

# ⚠️ 변동성 알림 기준
VOLATILITY_LIMIT = 3.0

def get_stock_data(code):
    try:
        url = f"https://m.stock.naver.com/api/stock/{code}/basic"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"}
        res = requests.get(url, headers=headers, timeout=5)
        
        if res.status_code != 200:
            return None
            
        data = res.json()
        
        close_price_str = data.get('closePrice', '0')
        open_price_str = data.get('openPrice', '0')
        
        try:
            current_price = float(close_price_str.replace(",", ""))
        except:
            current_price = 0.0
            
        try:
            open_price = float(open_price_str.replace(",", ""))
        except:
            open_price = 0.0
            
        change = data.get('compareToPreviousClosePrice', '0')
        rate = data.get('fluctuationsRatio', '0.00')
        
        prev_price_info = data.get('compareToPreviousPrice', {})
        sign_code = prev_price_info.get('code', '3')
        sign = "▲" if sign_code == "2" else "▼" if sign_code == "5" else "-"
        
        open_calc_rate = 0.0
        if open_price > 0 and current_price > 0:
            open_calc_rate = ((current_price - open_price) / open_price) * 100
            
        return {
            "current": close_price_str,
            "change_text": f"{sign} {change} / {rate}%",
            "open_rate": open_calc_rate
        }
    except Exception as e:
        return None

def run():
    kst_now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    time_str = kst_now.strftime('%H:%M')

    messages_to_send = []
    current_message = [f"📊 <b>[{time_str}] 주요 섹터별 시세 현황</b>\n"]
    urgent_messages = []
    
    for category, stocks in TARGET_CATEGORIES.items():
        category_text = [f"<b>{category}</b>"]
        
        for code, name in stocks.items():
            data = get_stock_data(code)
            if not data:
                category_text.append(f"• {name}: 정보 업데이트 중")
            else:
                category_text.append(f"• {name}: {data['current']} ({data['change_text']})")
                
                open_rate = data['open_rate']
                if abs(open_rate) >= VOLATILITY_LIMIT:
                    direction = "급등 🚀" if open_rate > 0 else "급락 📉"
                    urgent_messages.append(
                        f"🚨 <b>[긴급 변동 알림]</b>\n"
                        f"• 종목명: <b>{name}</b> ({direction})\n"
                        f"• 현재가: {data['current']}\n"
                        f"• <b>시작가 대비 변동률: {open_rate:+.2f}%</b>\n"
                        f"• 전일대비: {data['change_text']}"
                    )
            
            # 네이버 서버 차단을 막기 위해 한 종목 조회 후 0.2초 대기
            time.sleep(0.2)
            
        category_text.append("")
        
        if len("\n".join(current_message)) + len("\n".join(category_text)) > 3000:
            messages_to_send.append("\n".join(current_message))
            current_message = [f"📊 <b>[{time_str}] 주요 섹터별 시세 현황 (이어서)</b>\n"]
            
        current_message.extend(category_text)
        
    if current_message:
        messages_to_send.append("\n".join(current_message))

    bot_token = os.environ.get('STOCK_TOKEN')
    chat_id = os.environ.get('STOCK_CHAT_ID')
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    if urgent_messages:
        for urgent_msg in urgent_messages:
            requests.post(url, json={"chat_id": chat_id, "text": urgent_msg, "parse_mode": "HTML"})
            
    for msg in messages_to_send:
        requests.post(url, json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"})

if __name__ == "__main__":
    run()
