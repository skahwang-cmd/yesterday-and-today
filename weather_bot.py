import requests
import datetime
import os
import time

def get_weather_comparison():
    lat, lon = 37.5665, 126.978
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min&timezone=Asia%2FSeoul&past_days=1"
    
    # 최대 3번까지 재시도함
    for i in range(3):
        try:
            res = requests.get(url, timeout=10)
            res.raise_for_status()
            daily_data = res.json()['daily']
            
            y_max, y_min = daily_data['temperature_2m_max'][0], daily_data['temperature_2m_min'][0]
            t_max, t_min = daily_data['temperature_2m_max'][1], daily_data['temperature_2m_min'][1]
            
            return t_max, t_min, y_max, y_min
        except Exception as e:
            print(f"시도 {i+1}회 실패: {e}")
            if i < 2: # 마지막 시도가 아니면 5초 쉬고 다시 함
                time.sleep(5)
            else:
                raise e # 3번 다 실패하면 에러를 밖으로 던짐

def send_telegram():
    try:
        t_max, t_min, y_max, y_min = get_weather_comparison()
        
        max_diff = t_max - y_max
        min_diff = t_min - y_min
        
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

        token = os.environ['TELEGRAM_TOKEN']
        chat_id = os.environ['CHAT_ID']
        
        telegram_url = f"https://api.telegram.org/bot{token}/sendMessage"
        response = requests.post(telegram_url, json={"chat_id": chat_id, "text": msg})
        response.raise_for_status() # 텔레그램 전송 실패 시에도 에러 발생시킴
        
        print("전송 성공!")

    except Exception as e:
        print(f"최종 에러 발생: {e}")

if __name__ == "__main__":
    send_telegram()
