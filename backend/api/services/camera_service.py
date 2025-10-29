# VIBE CODED this whole file cuz vpadlu
# backend/api/services/camera_service.py
import cv2
import base64
import asyncio
from ..internal.ac_framework import component, inject
from .singleton_websocket_service import WebsocketService

@component
class CameraService:
    def __init__(self, websocket_service: WebsocketService):
        self.websocket_service = websocket_service
        self._camera_active = False
        self._camera_task = None
        self.cap = None

    async def start_stream(self):
        if self._camera_active:
            print("Camera stream is already active.")
            return

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Cannot open webcam. Please ensure a camera is connected and accessible.")
            return

        self._camera_active = True
        self._camera_task = asyncio.create_task(self._stream_frames_loop())
        print("Camera stream started.")

    async def stop_stream(self):
        if not self._camera_active:
            print("Camera stream is not active.")
            return

        self._camera_active = False
        if self._camera_task:
            self._camera_task.cancel()
            try:
                await self._camera_task
            except asyncio.CancelledError:
                pass
        if self.cap:
            self.cap.release()
            self.cap = None
        print("Camera stream stopped.")

    async def _stream_frames_loop(self):
        try:
            while self._camera_active:
                ret, frame = self.cap.read()
                if ret:
                    # Encode frame to JPEG
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80] # 80% quality
                    _, buffer = cv2.imencode('.jpg', frame, encode_param)
                    
                    # Convert to base64 string for JSON serialization
                    jpeg_as_text = base64.b64encode(buffer).decode('utf-8')
                    
                    await self.websocket_service.send({
                        "type": "camera_frame",
                        "data": jpeg_as_text
                    })
                await asyncio.sleep(0.03) # Approximately 30 FPS (1/30 = 0.033 seconds)
        except asyncio.CancelledError:
            print("Camera stream loop cancelled.")
        except Exception as e:
            print(f"Error in camera stream loop: {e}")
        finally:
            if self.cap:
                self.cap.release()
                self.cap = None
            print("Camera resources released.")