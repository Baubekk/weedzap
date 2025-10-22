import threading
from backend.api.internal.ac_framework import component
from backend.api.main import weedzap

import serial
import time

@component(weedzap)
class ArduinoService:
    def __init__(self):
        self.retry_interval = 5
        self.serial = None
        self._stop = False
        self.thread = threading.Thread(target=self._connection_loop, daemon=True)

    def start(self):
        self.thread.start()

    def stop(self):
        self._stop = True
        if self.serial and self.serial.is_open:
            self.serial.close()

    def _connection_loop(self):
        while not self._stop:
            if not self.serial or not self.serial.is_open:
                self._connect()
            time.sleep(self.retry_interval)

    def _connect(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        for port in ports:
            try:
                print(f"Trying {port}...")
                s = serial.Serial(port, self.baudrate, timeout=1)
                time.sleep(2)
                s.write(b'PING\n')
                reply = s.readline().decode().strip()
                if reply.startswith("PONG") or reply.startswith("Arduino"):
                    self.serial = s
                    print(f"Connected to Arduino on {port}")
                    return
                else:
                    s.close()
            except serial.SerialException:
                pass
        print("Arduino not found. Retrying...")

    def send(self, message: str):
        if not self.is_connected():
            print("Cannot send, Arduino not connected.")
            return False
        try:
            self.serial.write((message + '\n').encode())
            return True
        except serial.SerialException:
            print("Lost connection during send.")
            self.serial.close()
            return False

    def read_line(self):
        if not self.is_connected():
            return None
        try:
            line = self.serial.readline().decode().strip()
            return line if line else None
        except serial.SerialException:
            print("Lost connection during read.")
            self.serial.close()
            return None

            
