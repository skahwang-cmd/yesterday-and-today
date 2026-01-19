import requests
import datetime
import os
import time

def get_weather_comparison():
    lat, lon = 37.5665, 126.978
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min&timezone=Asia%2FSeoul&past_days=1"
    
    for i in range(3):
        try:
            res = requests.get(url, timeout=10)
            res.raise_for_status()
            daily_data = res.json()['daily']
            return daily_data['temperature_2m_max'][1], daily_data['temperature_2m_min'][1], \
                   daily_data['temperature_2m_max'][0], daily_data['temperature_2m_min'][0]
        except Exception as e:
            if i < 2: time.sleep(5)
            else: raise e

def send_telegram():
    try:
        t_max, t_min, y_max, y_min = get_weather_comparison()
        msg = f"📅 날씨 비교\n최고: {t_max}°C (어제보다 {t_max-y_max:+.1f})\n최저: {t_min}°C (어제보다 {t_min-y_min:+.1f})"

        token = os.environ.get('TELEGRAM_TOKEN', '').strip()
        chat_id = os.environ.get('CHAT_ID', '').strip()
        
        # [중요] 상세 에러를 보기 위한 post 로직
        telegram_url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": msg}
        
        response = requests.post(telegram_url, json=payload)
        
        if response.status_code != 200:
            # 텔레그램이 보내준 진짜 이유를 출력함
            print(f"❌ 텔레그램 응답 에러: {response.text}")
        
        response.raise_for_status()
        print("✅ 전송 성공!")

    except Exception as e:
        print(f"🔥 최종 에러 발생: {e}")

if __name__ == "__main__":
    send_telegram()
