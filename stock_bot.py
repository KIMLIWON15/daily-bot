import os
import requests
import datetime

# 🎯 등록할 주식 종목 (원하는 종목코드와 이름을 자유롭게 추가/수정하세요)
TARGET_STOCKS = {
    "005930": "삼성전자",
    "000660": "SK하이닉스",
    "035420": "NAVER",
    "196170": "알테오젠"
}

def get_stock_price(code):
    try:
        url = f"https://m.stock.naver.com/api/stock/{code}/basic"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers).json()
        price = res['closePrice']
        change = res['compareToPreviousClosePrice']
        rate = res['fluctuationsRatio']
        sign_code = res['compareToPreviousPrice']['code']
        sign = "▲" if sign_code == "2" else "▼" if sign_code == "5" else "-"
        return f"{price} ({sign} {change} / {rate}%)"
    except:
        return "조회 실패"

def run():
    kst_now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    time_str = kst_now.strftime('%H:%M')

    messages = [f"📈 [{time_str}] 주요 종목 시세 알림"]
    
    for code, name in TARGET_STOCKS.items():
        price_info = get_stock_price(code)
        messages.append(f"• {name}: {price_info}")
        
    final_message = "\n".join(messages)

    # 새로 만든 금고 열쇠를 사용합니다.
    bot_token = os.environ.get('STOCK_TOKEN')
    chat_id = os.environ.get('STOCK_CHAT_ID')

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": final_message})

if __name__ == "__main__":
    run()
