import threading
import serial.tools.list_ports
import time
from ..internal.ac_framework import component

@component
class ArduinoService:
    def __init__(self):
        self.retry_interval = 5
        self.serial = None
        self._stop = False
        self.thread = threading.Thread(target=self._connection_loop, daemon=True)
        self.baudrate = 115200

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
        port = "/dev/serial0"
        try:
            print(f"Trying {port}...")
            s = serial.Serial(port, self.baudrate, timeout=1)
            time.sleep(2)
            s.write(b'w\n')
            reply = s.readline().decode().strip()
            if reply.lower().startswith('ok'):
                self.serial = s
                print(f"Connected to Arduino on {port}")
                return
            else:
                s.close()
        except serial.SerialException as e:
            print(f"Failed to connect to {port}: {e}")

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

    def is_connected(self):
        return self.serial and self.serial.is_open


            
