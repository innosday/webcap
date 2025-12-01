# 📸 Raspberry Pi Smart CCTV & Controller

라즈베리파이(Raspberry Pi)와 파이카메라(PiCamera2)를 활용하여 실시간 영상을 웹으로 송출하고, 웹사이트에서 하드웨어를 원격 제어하는 IoT 프로젝트입니다.

FastAPI를 사용하여 고성능 비동기 서버를 구축하였으며, MJPEG 스트리밍 방식을 사용하여 지연 시간을 최소화했습니다.

## ✨ 주요 기능 (Features)

* **📺 실시간 비디오 스트리밍:** Picamera2와 OpenCV를 활용한 저지연 MJPEG 스트리밍.
* **📸 원격 사진 촬영:** 웹 버튼 클릭 시 라즈베리파이 로컬 저장소에 고화질 사진 저장.
* **💡 LED 원격 제어:** GPIO를 활용하여 웹에서 LED On/Off 제어.
* **⛔ 원격 시스템 종료:** 웹에서 라즈베리파이 서버 프로그램 안전 종료.
* **📱 반응형 웹 클라이언트:** 노트북, 태블릿 등 외부 기기 브라우저에서 접속 가능.

## 🔌 하드웨어 연결 (Hardware Wiring)

| 컴포넌트 | 라즈베리파이 핀 (BCM) | 물리적 핀 번호 (Physical) |
| :--- | :--- | :--- |
| **LED (+)** | GPIO 17 | Pin 11 |
| **LED (-)** | GND | Pin 6, 9, etc. |

---

## 🚀 설치 및 실행 방법 (Installation)

### 1. 환경 설정 (Raspberry Pi)

이 프로젝트는 `Picamera2` 시스템 라이브러리를 사용하므로 가상환경 설정 시 주의가 필요합니다.

```bash
# 1. 저장소 클론 (또는 프로젝트 폴더 생성)
git clone [레포지토리 주소]
cd [프로젝트 폴더]

# 2. 가상환경 생성 (시스템 패키지 포함 옵션 필수!)
python -m venv venv --system-site-packages

# 3. 가상환경 활성화
source venv/bin/activate

# 4. 필수 라이브러리 설치
# (picamera2는 시스템에 내장되어 있으므로 설치 불필요)
pip install fastapi uvicorn[standard] opencv-python multipart
```
