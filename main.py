import cv2
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# CORS 설정 (노트북에서 접속 허용을 위해 필수)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 IP 허용 (보안 필요시 노트북 IP로 특정 가능)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 카메라 초기화 (0번은 보통 기본 연결된 카메라)
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # 프레임을 JPG로 인코딩
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
            # MJPEG 포맷으로 스트리밍 (중요!)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.get("/video_feed")
async def video_feed():
    """웹사이트의 <img> 태그 소스로 사용될 스트리밍 엔드포인트"""
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace;boundary=frame")

@app.post("/action")
async def take_action(request: Request):
    """웹사이트 버튼 클릭 시 상호작용하는 엔드포인트"""
    data = await request.json()
    command = data.get("command")
    
    print(f"노트북에서 받은 명령: {command}")
    
    # 여기에 실제 하드웨어 제어 코드 추가 가능 (예: LED 켜기 등)
    if command == "capture":
        return JSONResponse(content={"message": "사진 촬영 명령 수신됨", "status": "ok"})
    
    return JSONResponse(content={"message": "알 수 없는 명령", "status": "fail"})

if __name__ == "__main__":
    # host="0.0.0.0"으로 설정해야 외부(노트북)에서 접속 가능
    uvicorn.run(app, host="0.0.0.0", port=8000)
