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
        ports = serial.tools.list_ports.comports()

        acm_ports = [p.device for p in ports if "ttyACM" in p.device]

        if not acm_ports:
            raise RuntimeError("No /dev/ttyACMx devices found")

        port = acm_ports[0]
        try:
            print(f"Trying {port}...")
            s = serial.Serial(port, self.baudrate, timeout=1)
            time.sleep(2)
            s.reset_input_buffer()
            s.write(b'w\n')

            start = time.time()

            while time.time() - start < 3:
                line = s.readline().decode(errors='ignore').strip()
                if line:
                    print("Received:", line)
                    if line.lower().startswith("ok"):
                        self.serial = s
                        print(f"Connected to Arduino on {port}")
                        return

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

    def send_command(self, command: str, expected_response_prefixes: list[str] = None, timeout: int = 5):
        if expected_response_prefixes is None:
            expected_response_prefixes = ["OK"]

        if not self.send(command):
            return False, "Failed to send command."

        return self._await_response(expected_response_prefixes, timeout)

    def _await_response(self, expected_response_prefixes: list[str], timeout: int = 5):
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = self.read_line()
            if response:
                print(f"Arduino response: {response}")
                for prefix in expected_response_prefixes:
                    if prefix == "POS X:" and response.startswith("POS X:") and "Y:" in response and "Z:" in response:
                        return True, response
                    elif response.startswith(prefix):
                        return True, response
                if response.startswith("ERROR"):
                    return False, response
            time.sleep(0.1) # Small delay to prevent busy-waiting
        return False, "Timeout waiting for response."


    def send_set_command(self, param_name: str, value: str):
        command = f"SET {param_name} {value}"
        success, response = self.send_command(command, ["OK: Config Updated"])
        return success, response

    def send_tool_on_command(self, tool_number: int) -> tuple[bool, str]:
        command = f"TOOLON {tool_number}"
        return self.send_command(command, ["OK: Laser tool attached", "OK: Servo tool attached"])

    def send_tool_off_command(self) -> tuple[bool, str]:
        command = "TOOLOFF"
        return self.send_command(command, ["OK: Laser tool returned", "OK: Servo tool returned"])

    def send_jog_command(self, dx: float, dy: float, dz: float) -> tuple[bool, str]:
        command = f"JOG X{dx} Y{dy} Z{dz}"
        return self.send_command(command, ["POS X:"])

    def send_pos_command(self) -> tuple[bool, str]:
        command = "POS"
        return self.send_command(command, ["POS X:"])

    def send_status_command(self) -> tuple[bool, str]:
        command = "STATUS"
        return self.send_command(command, ["STATUS:"])

    def send_led_command(self, state: int) -> tuple[bool, str]:
        command = f"LED {state}"
        return self.send_command(command, ["OK: LED ON", "OK: LED OFF"])



    def send_move_command(self, x: float, y: float, z: float):
        command = f"MOVE X{x} Y{y} Z{z}"
        success, response = self.send_command(command, ["POS X:"])
        return success, response

    def send_home_command(self):
        command = "HOME"
        success, response = self.send_command(command, ["STATUS: Home OK"])
        return success, response

    def send_stop_command(self):
        command = "STOP"
        success, response = self.send_command(command, "OK: Stopped")
        return success, response


            
