import requests
import datetime
import os
import time

def get_weather_info():
    lat, lon = 37.5665, 126.978
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,weather_code&timezone=Asia%2FSeoul&past_days=1"
    
    for i in range(3):
        try:
            res = requests.get(url, timeout=10)
            res.raise_for_status()
            daily_data = res.json()['daily']
            
            y_max, y_min = daily_data['temperature_2m_max'][0], daily_data['temperature_2m_min'][0]
            t_max, t_min = daily_data['temperature_2m_max'][1], daily_data['temperature_2m_min'][1]
            w_code = daily_data['weather_code'][1]
            
            return t_max, t_min, y_max, y_min, w_code
        except Exception as e:
            if i < 2: time.sleep(5)
            else: raise e

def get_weather_emoji(code):
    if code == 0: return "☀️ 맑음"
    if 1 <= code <= 3: return "☁️ 흐림/구름"
    if code in [45, 48]: return "🌫️ 안개"
    if 51 <= code <= 67: return "☔ 비/이슬비"
    if 71 <= code <= 77: return "❄️ 눈 소식"
    if code >= 95: return "⚡ 천둥번개"
    return "🌈 날씨 확인 필요"

def send_telegram():
    try:
        t_max, t_min, y_max, y_min, w_code = get_weather_info()
        weather_desc = get_weather_emoji(w_code)
        
        # --- [수정된 부분] 한국 시간대(KST) 강제 설정 ---
        KST = datetime.timezone(datetime.timedelta(hours=9))
        now_date = datetime.datetime.now(KST).strftime('%m월 %d일')
        # ----------------------------------------------
        
        msg = f"🔔 [{now_date} 날씨 리포트]\n"
        msg += f"날씨 상태: {weather_desc}\n"
        msg += "----------------------------\n"
        msg += f"최고 기온: {t_max}°C (어제보다 {t_max-y_max:+.1f})\n"
        msg += f"최저 기온: {t_min}°C (어제보다 {t_min-y_min:+.1f})\n\n"
        
        diff = t_max - y_max
        if diff > 2: msg += "추천: 어제보다 따뜻함. 가볍게 입으셈."
        elif diff < -2: msg += "추천: 어제보다 꽤 추워짐. 든든하게 입으셈."
        else: msg += "추천: 어제와 비슷하니 평소처럼 입으셈."

        token = os.environ.get('TELEGRAM_TOKEN', '').strip()
        chat_id = os.environ.get('CHAT_ID', '').strip()
        
        telegram_url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(telegram_url, json={"chat_id": chat_id, "text": msg})
        print("✅ 전송 성공!")

    except Exception as e:
        print(f"🔥 최종 에러 발생: {e}")

if __name__ == "__main__":
    send_telegram()
