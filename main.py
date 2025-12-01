import cv2
import time
import numpy as np
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Picamera2 라이브러리 가져오기
from picamera2 import Picamera2

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Picamera2 설정 ===
try:
    picam2 = Picamera2()
    # 해상도 및 포맷 설정 (RGB888로 설정해야 OpenCV 변환이 쉽습니다)
    config = picam2.create_video_configuration(main={"size": (640, 480), "format": "RGB888"})
    picam2.configure(config)
    picam2.start()
    print("카메라가 성공적으로 시작되었습니다.")
except Exception as e:
    print(f"카메라 초기화 실패: {e}")

def generate_frames():
    while True:
        try:
            # 1. Picamera2에서 이미지를 배열(numpy array) 형태로 캡처
            frame = picam2.capture_array()
            
            # 2. Picamera는 RGB 순서, OpenCV는 BGR 순서를 쓰므로 색상 변환 필요
            # 변환 안 하면 화면이 파랗게 나옵니다.
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # 3. 이미지를 JPG로 인코딩 (압축)
            ret, buffer = cv2.imencode('.jpg', frame)
            
            # 4. 바이트로 변환하여 전송
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            # 너무 빠른 루프 방지 (약 30fps 조절)
            # time.sleep(0.01) 
            
        except Exception as e:
            print(f"프레임 생성 에러: {e}")
            break

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace;boundary=frame")

@app.post("/action")
async def take_action(request: Request):
    data = await request.json()
    command = data.get("command")
    print(f"명령 수신: {command}")
    
    if command == "capture":
        return JSONResponse(content={"message": "Picamera 촬영 완료", "status": "ok"})
    
    return JSONResponse(content={"message": "알 수 없는 명령", "status": "fail"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
