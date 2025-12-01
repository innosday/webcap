import cv2
import time
import os
import sys
import signal
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from picamera2 import Picamera2
from gpiozero import LED

app = FastAPI()

# === 설정 ===
# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LED 설정 (GPIO 17번 핀 사용)
led = LED(17)

# 카메라 설정
try:
    picam2 = Picamera2()
    config = picam2.create_video_configuration(main={"size": (640, 480), "format": "RGB888"})
    picam2.configure(config)
    picam2.start()
    print("✅ 카메라 시작됨")
except Exception as e:
    print(f"❌ 카메라 에러: {e}")

def generate_frames():
    while True:
        try:
            frame = picam2.capture_array()
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.01)
        except Exception as e:
            pass

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace;boundary=frame")

@app.post("/action")
async def take_action(request: Request):
    data = await request.json()
    command = data.get("command")
    print(f"📥 명령 수신: {command}")
    
    response_msg = ""

    # 1. 캡처 기능
    if command == "capture":
        # 현재 시간으로 파일명 생성 (예: capture_20231025_143001.jpg)
        filename = datetime.now().strftime("capture_%Y%m%d_%H%M%S.jpg")
        
        # 현재 화면 한 장 찍기
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # 파일로 저장 (main.py가 있는 폴더에 저장됨)
        cv2.imwrite(filename, frame)
        response_msg = f"저장 완료: {filename}"
        
    # 2. LED 제어 기능
    elif command == "led_on":
        led.on()
        response_msg = "💡 LED 켜짐"
        
    elif command == "led_off":
        led.off()
        response_msg = "🌑 LED 꺼짐"
        
    # 3. 서버 종료 기능
    elif command == "shutdown":
        print("시스템을 종료합니다...")
        # 1초 뒤에 종료 (응답을 보내주기 위해 약간 기다림)
        os.kill(os.getpid(), signal.SIGTERM)
        return JSONResponse(content={"message": "서버가 종료됩니다.", "status": "shutdown"})

    else:
        response_msg = "알 수 없는 명령"

    return JSONResponse(content={"message": response_msg, "status": "ok"})

if __name__ == "__main__":
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        pass
    finally:
        picam2.stop()
        led.off()
