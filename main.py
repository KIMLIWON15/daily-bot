import os
import requests
import datetime

def send_telegram_message(text):
    # 깃허브 Actions가 env로 넘겨준 토큰 값을 파이썬 시스템 환경변수에서 읽어옵니다.
    bot_token = os.environ.get('TELEGRAM_TOKEN')
    # 채팅방 ID도 환경변수에서 읽어옵니다.
    chat_id = os.environ.get('1098765432')
    
    # 만약 Secrets 설정을 안 했다면 경고 출력
    if not bot_token or not chat_id:
        print("❌ 에러: 깃허브 Secrets에 토큰이나 Chat ID가 설정되지 않았습니다.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("🚀 텔레그램 메시지 전송 성공!")
    else:
        print(f"❌ 전송 실패 (에러 코드: {response.status_code})")

def run():
    now = datetime.datetime.now()
    message = f"☀️ 아침 알림 완료!\n실행 시간: {now.strftime('%Y-%m-%d %H:%M:%S')}\n오늘도 좋은 하루 되세요!"
    send_telegram_message(message)

if __name__ == "__main__":
    run()
