import os
import requests
import datetime

# 🎯 감시할 주식 종목 (10개 카테고리 x 10종목 = 총 100개)
TARGET_CATEGORIES = {
    "💻 [반도체 & 장비]": {
        "005930": "삼성전자", "000660": "SK하이닉스", "042700": "한미반도체", "058470": "리노공업", "036930": "주성엔지니어링",
        "039030": "이오테크닉스", "074600": "원익IPS", "222800": "심텍", "000990": "DB하이텍", "084370": "유진테크"
    },
    "🌐 [IT & 플랫폼 & 통신]": {
        "035420": "NAVER", "035720": "카카오", "018260": "삼성SDS", "017670": "SK텔레콤", "030200": "KT",
        "032640": "LG유플러스", "259960": "크래프톤", "036570": "엔씨소프트", "251270": "넷마블", "047050": "포스코DX"
    },
    "🧬 [제약 & 바이오]": {
        "207940": "삼성바이오로직스", "068270": "셀트리온", "196170": "알테오젠", "028300": "HLB", "000100": "유한양행",
        "096530": "씨젠", "008930": "한미사이언스", "128940": "한미약품", "000250": "삼천당제약", "145020": "휴젤"
    },
    "🔋 [2차전지 & 소재]": {
        "373220": "LG에너지솔루션", "006400": "삼성SDI", "051910": "LG화학", "247540": "에코프로비엠", "086520": "에코프로",
        "003670": "포스코퓨처엠", "005490": "POSCO홀딩스", "278280": "천보", "365340": "엔켐", "175330": "엘앤에프"
    },
    "🚗 [자동차 & 부품]": {
        "005380": "현대차", "000270": "기아", "012330": "현대모비스", "011210": "현대위아", "018880": "한온시스템",
        "005850": "에스엘", "204320": "HL만도", "161390": "한국타이어앤테크놀로지", "033310": "엠에스오토텍", "011070": "LG이노텍"
    },
    "🛡️ [방산 & 우주항공]": {
        "012450": "한화에어로스페이스", "047810": "한국항공우주", "064350": "현대로템", "079550": "LIG넥스원", "272210": "한화시스템",
        "082320": "한화", "005090": "SNT다이내믹스", "320170": "빅텍", "010820": "퍼스텍", "095270": "웨이브일렉트로"
    },
    "🚢 [조선 & 해운 & 기계]": {
        "009540": "HD현대중공업", "042660": "한화오션", "329180": "HD한국조선해양", "010140": "삼성중공업", "011200": "HMM",
        "028670": "팬오션", "004380": "대한해운", "034020": "두산에너빌리티", "241560": "두산밥캣", "267250": "HD현대건설기계"
    },
    "🏦 [금융 & 지주사]": {
        "055550": "신한지주", "105560": "KB금융", "086790": "하나금융지주", "316140": "우리금융지주", "032830": "삼성생명",
        "000810": "삼성화재", "006800": "미래에셋증권", "039490": "키움증권", "138040": "메리츠금융지주", "003550": "LG"
    },
    "🎬 [엔터 & 화장품]": {
        "352820": "하이브", "041510": "에스엠", "035900": "JYP Ent.", "122870": "와이지엔터테인먼트", "090430": "아모레퍼시픽",
        "051900": "LG생활건강", "031430": "신세계인터내셔날", "161890": "한국콜마", "192820": "코스맥스", "222040": "코스메카코리아"
    },
    "🏗️ [건설 & 철강 & 에너지]": {
        "000720": "현대건설", "006360": "GS건설", "047040": "대우건설", "004020": "현대제철", "010130": "고려아연",
        "001430": "세아베스틸지주", "015760": "한국전력", "036460": "한국가스공사", "010950": "S-Oil", "011780": "금호석유"
    }
}

# ⚠️ 변동성 알림 기준 (시가 대비 3% 이상 상승 또는 하락 시 알림)
VOLATILITY_LIMIT = 3.0

def get_stock_data(code):
    try:
        url = f"https://m.stock.naver.com/api/stock/{code}/basic"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        res = requests.get(url, headers=headers).json()
        
        current_price = float(res['closePrice'].replace(",", ""))
        open_price = float(res['openPrice'].replace(",", ""))
        
        change = res['compareToPreviousClosePrice']
        rate = res['fluctuationsRatio']
        sign_code = res['compareToPreviousPrice']['code']
        sign = "▲" if sign_code == "2" else "▼" if sign_code == "5" else "-"
        
        if open_price > 0:
            open_calc_rate = ((current_price - open_price) / open_price) * 100
        else:
            open_calc_rate = 0.0
            
        return {
            "current": res['closePrice'],
            "change_text": f"{sign} {change} / {rate}%",
            "open_rate": open_calc_rate
        }
    except:
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
                continue
                
            category_text.append(f"• {name}: {data['current']} ({data['change_text']})")
            
            # 조건부 변동성 체크 (3% 이상)
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
        category_text.append("")
        
        # 텔레그램 글자 수 제한 방지: 3000자가 넘어가면 메시지를 자르고 새로 담기
        if len("\n".join(current_message)) + len("\n".join(category_text)) > 3000:
            messages_to_send.append("\n".join(current_message))
            current_message = [f"📊 <b>[{time_str}] 주요 섹터별 시세 현황 (이어서)</b>\n"]
            
        current_message.extend(category_text)
        
    if current_message:
        messages_to_send.append("\n".join(current_message))

    bot_token = os.environ.get('STOCK_TOKEN')
    chat_id = os.environ.get('STOCK_CHAT_ID')
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    # 1. 3% 이상 변동된 긴급 종목 우선 발송
    if urgent_messages:
        for urgent_msg in urgent_messages:
            requests.post(url, json={"chat_id": chat_id, "text": urgent_msg, "parse_mode": "HTML"})
            
    # 2. 정기 리포트 발송 (자동 분할 전송)
    for msg in messages_to_send:
        requests.post(url, json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"})

if __name__ == "__main__":
    run()
