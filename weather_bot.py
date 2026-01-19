import requests
import datetime
import os

def get_weather_comparison():
    # 서울 좌표 (다른 지역은 위경도 수정 가능)
    lat, lon = 37.5665, 126.978
    # past_days=1 옵션으로 어제와 오늘 데이터를 동시에 가져옴
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min&timezone=Asia%2FSeoul&past_days=1"
    
    res = requests.get(url)
    res.raise_for_status()
    daily_data = res.json()['daily']
    
    # 인덱스 0이 어제, 1이 오늘 데이터임
    y_max, y_min = daily_data['temperature_2m_max'][0], daily_data['temperature_2m_min'][0]
    t_max, t_min = daily_data['temperature_2m_max'][1], daily_data['temperature_2m_min'][1]
    
    return t_max, t_min, y_max, y_min

def send_telegram():
    try:
        t_max, t_min, y_max, y_min = get_weather_comparison()
        
        # 기온 차이 계산
        max_diff = t_max - y_max
        min_diff = t_min - y_min
        
        # 메시지 구성
        now_date = datetime.datetime.now().strftime('%Y-%m-%d')
        msg = f"📅 {now_date} 날씨 비교 정보\n\n"
        msg += f"🔺 최고 기온: {t_max}°C (어제보다 {max_diff:+.1f}°C)\n"
        msg += f"🔻 최저 기온: {t_min}°C (어제보다 {min_diff:+.1f}°C)\n\n"
        
        if max_diff > 2:
            msg += "💡 어제보다 훨씬 따뜻함. 가볍게 입으셈!"
        elif max_diff < -2:
            msg += "💡 어제보다 꽤 추워짐. 든든하게 챙겨 입으셈!"
        else:
            msg += "💡 어제와 비슷한 날씨임."

        # 환경변수에서 토큰과 ID를 가져옴 (GitHub Secrets 연동용)
        token = os.environ['TELEGRAM_TOKEN']
        chat_id = os.environ['CHAT_ID']
        
        telegram_url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(telegram_url, json={"chat_id": chat_id, "text": msg})
        print("전송 성공!")

    except Exception as e:
        print(f"에러 발생: {e}")

if __name__ == "__main__":
    send_telegram()