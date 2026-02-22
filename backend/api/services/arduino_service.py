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

    def send_command(self, command: str, expected_response_prefix: str = "OK", timeout: int = 5):
        if not self.send(command):
            return False, "Failed to send command."

        return self._await_response(expected_response_prefix, timeout)

    def _await_response(self, expected_response_prefix: str, timeout: int = 5):
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = self.read_line()
            if response:
                print(f"Arduino response: {response}")
                if response.startswith(expected_response_prefix):
                    return True, response
                elif response.startswith("ERROR"):
                    return False, response
            time.sleep(0.1) # Small delay to prevent busy-waiting
        return False, "Timeout waiting for response."

    def send_set_command(self, config_key: str, config_value: str):
        command = f"SET {config_key} {config_value}"
        success, response = self.send_command(command, "OK: Config Updated")
        return success, response

    def send_tool_command(self, tool_mode: str):
        command = f"TOOL {tool_mode}"
        success, response = self.send_command(command, "OK: Mode")
        if success and ("OK: Mode SERVO" in response or "OK: Mode LASER" in response):
            return True, response
        return False, response

    def send_fire_command(self, value: int):
        command = f"FIRE {value}"
        success, response = self.send_command(command, "OK:")
        if success and ("OK: Servo Angle" in response or "OK: Laser PWM" in response):
            return True, response
        return False, response

    def send_move_command(self, x: float, y: float, z: float):
        command = f"MOVE X{x} Y{y} Z{z}"
        success, response = self.send_command(command, "OK: Moved")
        return success, response

    def send_home_command(self):
        command = "HOME"
        success, response = self.send_command(command, "STATUS: Homing...")
        if success:
            print("Homing initiated, waiting for completion...")
            success, response = self._await_response("OK: Homed")
            return success, response
        return False, response

    def send_stop_command(self):
        command = "STOP"
        success, response = self.send_command(command, "OK: Stopped")
        return success, response


            
