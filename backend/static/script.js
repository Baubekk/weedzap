document.addEventListener("DOMContentLoaded", () => {
    const wsStatus = document.getElementById("ws-status");
    const logOutput = document.getElementById("log-output");
    const cameraFeed = document.getElementById("cameraFeed");

    // Current Configuration Displays
    const currentConfigElements = {
        steps_x: document.getElementById("current-steps_x"),
        steps_y: document.getElementById("current-steps_y"),
        steps_z: document.getElementById("current-steps_z"),
        x_max_l: document.getElementById("current-x_max_l"),
        y_max_l: document.getElementById("current-y_max_l"),
        z_max_l: document.getElementById("current-z_max_l"),
        h_spd_x: document.getElementById("current-h_spd_x"),
        h_spd_y: document.getElementById("current-h_spd_y"),
        h_spd_z: document.getElementById("current-h_spd_z"),
        homing_speed_slow: document.getElementById("current-homing_speed_slow"),
        max_speed: document.getElementById("current-max_speed"),
        accel: document.getElementById("current-accel"),

    };

    // Configuration Input Elements and Buttons
    const configInputs = {
        steps_x: { input: document.getElementById("set-steps_x"), button: document.getElementById("btn-set-steps_x"), type: parseFloat, min: 0, max: 10000 },
        steps_y: { input: document.getElementById("set-steps_y"), button: document.getElementById("btn-set-steps_y"), type: parseFloat, min: 0, max: 10000 },
        steps_z: { input: document.getElementById("set-steps_z"), button: document.getElementById("btn-set-steps_z"), type: parseFloat, min: 0, max: 10000 },
        x_max_l: { input: document.getElementById("set-x_max_l"), button: document.getElementById("btn-set-x_max_l"), type: parseFloat, min: 0, max: 10000 },
        y_max_l: { input: document.getElementById("set-y_max_l"), button: document.getElementById("btn-set-y_max_l"), type: parseFloat, min: 0, max: 10000 },
        z_max_l: { input: document.getElementById("set-z_max_l"), button: document.getElementById("btn-set-z_max_l"), type: parseFloat, min: 0, max: 10000 },
        h_spd_x: { input: document.getElementById("set-h_spd_x"), button: document.getElementById("btn-set-h_spd_x"), type: parseFloat, min: 0, max: 10000 },
        h_spd_y: { input: document.getElementById("set-h_spd_y"), button: document.getElementById("btn-set-h_spd_y"), type: parseFloat, min: 0, max: 10000 },
        h_spd_z: { input: document.getElementById("set-h_spd_z"), button: document.getElementById("btn-set-h_spd_z"), type: parseFloat, min: 0, max: 10000 },
        homing_speed_slow: { input: document.getElementById("set-homing_speed_slow"), button: document.getElementById("btn-set-homing_speed_slow"), type: parseFloat, min: 0, max: 10000 },
        max_speed: { input: document.getElementById("set-max_speed"), button: document.getElementById("btn-set-max_speed"), type: parseFloat, min: 0, max: 10000 },
        accel: { input: document.getElementById("set-accel"), button: document.getElementById("btn-set-accel"), type: parseFloat, min: 0, max: 10000 },
    };

    // Movement Controls
    const moveXInput = document.getElementById("move-x");
    const moveYInput = document.getElementById("move-y");
    const moveZInput = document.getElementById("move-z");
    const moveSpeedInput = document.getElementById("move-speed");
    const btnMoveTo = document.getElementById("btn-move-to");
    const btnHome = document.getElementById("btn-home");
    const jogDxInput = document.getElementById("jog-dx");
    const jogDyInput = document.getElementById("jog-dy");
    const jogDzInput = document.getElementById("jog-dz");
    const btnJog = document.getElementById("btn-jog");
    const btnPosQuery = document.getElementById("btn-pos-query");
    const currentPosDisplay = document.getElementById("current-pos");
    const btnStatusQuery = document.getElementById("btn-status-query");
    const statusDisplay = document.getElementById("current-status");

    // Tool Management Controls
    const toolNumberInput = document.getElementById("tool-number");
    const btnToolOn = document.getElementById("btn-tool-on");
    const btnToolOff = document.getElementById("btn-tool-off");
    const fireValueInput = document.getElementById("fire-value");
    const btnFire = document.getElementById("btn-fire");
    const btnGetCurrentToolStatus = document.getElementById("btn-get-current-tool-status");

    // Arbitrary Arduino Command
    const arduinoCommandInput = document.getElementById("arduino-command-input");
    const sendArduinoCommandBtn = document.getElementById("send-arduino-command");

    // LED Controls
    const btnLedOn = document.getElementById("btn-led-on");
    const btnLedOff = document.getElementById("btn-led-off");

    let websocket;

    function logMessage(message, type = "info") {
        const p = document.createElement("p");
        p.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        if (type === "error") p.style.color = "red";
        if (type === "warning") p.style.color = "orange";
        logOutput.appendChild(p);
        logOutput.scrollTop = logOutput.scrollHeight;
    }

    function connectWebSocket() {
        websocket = new WebSocket(`ws://${window.location.hostname}:8000/ws`);

        websocket.onopen = () => {
            wsStatus.textContent = "Connected";
            wsStatus.style.color = "green";
            logMessage("Websocket connected.");
            fetchCurrentConfig(); // Fetch initial config on connection
            get_current_tool_status();
            get_current_position();
            get_status();
        };



        websocket.onclose = (event) => {
            wsStatus.textContent = "Disconnected";
            wsStatus.style.color = "red";
            logMessage(`Websocket disconnected. Code: ${event.code}, Reason: ${event.reason}. Attempting to reconnect in 5 seconds...`, "warning");
            setTimeout(connectWebSocket, 5000); // Attempt to reconnect
        };

        websocket.onerror = (error) => {
            logMessage(`Websocket error: ${error.message}`, "error");
            wsStatus.textContent = "Error";
            wsStatus.style.color = "red";
        };

        // Update websocket.onmessage to handle new message types
        websocket.onmessage = (event) => {
            const message = JSON.parse(event.data);

            if (message.type === "camera_frame") {
                cameraFeed.src = `data:image/jpeg;base64,${message.data}`;
            } else if (message.type === "config_ack") {
                if (message.status === "success") {
                    logMessage(`Config update acknowledged: ${message.param} = ${message.value}. ${message.message || ""}`);
                    fetchCurrentConfig();
                } else {
                    logMessage(`Config update failed for ${message.param}: ${message.message}`, "error");
                }
            } else if (message.type === "movement_ack") {
                if (message.status === "success") {
                    logMessage(`Movement acknowledged. Command: ${message.command}. ${message.message || ""}`);
                } else {
                    logMessage(`Movement failed. Command: ${message.command}. Error: ${message.message}`, "error");
                }
            } else if (message.type === "laser_ack") {
                if (message.status === "success") {
                    logMessage(`Laser acknowledged. Command: ${message.command}. ${message.message || ""}`);
                } else {
                    logMessage(`Laser failed. Command: ${message.command}. Error: ${message.message}`, "error");
                }
            } else if (message.type === "led_ack") {
                if (message.status === "success") {
                    logMessage(`LED acknowledged. Command: ${message.command}. ${message.message || ""}`);
                } else {
                    logMessage(`LED failed. Command: ${message.command}. Error: ${message.message}`, "error");
                }
            } else if (message.type === "raw_ack") {
                if (message.status === "success") {
                    logMessage(`Raw command acknowledged. Command: ${message.command}. ${message.message || ""}`);
                } else {
                    logMessage(`Raw command failed. Command: ${message.command}. Error: ${message.message}`, "error");
                }
            } else if (message.type === "pos_update") {
                currentPosDisplay.textContent = `X: ${message.data.x}, Y: ${message.data.y}, Z: ${message.data.z}`;
                logMessage(`Position updated to X: ${message.data.x}, Y: ${message.data.y}, Z: ${message.data.z}`);
            } else if (message.type === "status_update") {
                statusDisplay.textContent = `Machine: ${message.data.machine_state}, Tool: ${message.data.tool_state}, Alarm: ${message.data.alarm}, Hold: ${message.data.hold}`;
                logMessage(`Status updated: Machine State - ${message.data.machine_state}, Tool State - ${message.data.tool_state}, Alarm - ${message.data.alarm}, Hold - ${message.data.hold}`);
            } else if (message.type === "arduino_response") {
                logMessage(`Arduino Response: ${message.data}`, "info");
            } else {
                logMessage(`Unhandled message type: ${message.type}. Content: ${JSON.stringify(message)}`, "warning");
            }
        };
    }

    async function fetchCurrentConfig() {
        try {
            const response = await fetch("/config/all");
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const config = await response.json();
            logMessage("Fetched all current configurations.");

            for (const key in config) {
                const element = currentConfigElements[key];
                if (element) {
                    element.textContent = config[key];
                } else {
                    if (!["movement_mode", "laser_movement_mode", "laser_state", "speed"].includes(key)) {
                        logMessage(`Config parameter '${key}': ${config[key]} (No specific UI element found, logging instead)`);
                    }
                }
            }
        } catch (error) {
            logMessage(`Error fetching config: ${error}`, "error");
        }
    }

    function sendWebSocketMessage(message) {
        if (websocket.readyState === WebSocket.OPEN) {
            websocket.send(JSON.stringify(message));
            logMessage(`Sent: ${JSON.stringify(message)}`);
        } else {
            logMessage("Websocket not connected.", "error");
        }
    }

    function sendConfigUpdate(param, value) {
        sendWebSocketMessage({
            type: "config",
            param: param,
            value: value
        });
    }

    function sendMovementCommand(command, data = {}) {
        sendWebSocketMessage({
            type: "movement",
            command: command,
            data: data
        });
    }

    function sendLaserCommand(command, data = {}) {
        sendWebSocketMessage({
            type: "laser",
            command: command,
            data: data
        });
    }

    function sendLedCommand(command, data = {}) {
        sendWebSocketMessage({
            type: "led",
            command: command,
            data: data
        });
    }

    function sendRawCommand(command) {
        sendWebSocketMessage({
            type: "raw",
            command: command
        });
    }

    function get_current_tool_status() {
        sendLaserCommand("tool_status");
    }

    function get_current_position() {
        sendMovementCommand("pos");
    }

    function get_status() {
        sendMovementCommand("status");
    }

    // Configuration Commands Event Listeners
    for (const key in configInputs) {
        const { input, button, type, min, max } = configInputs[key];
        if (button) {
            button.addEventListener("click", () => {
                let value = type(input.value);


                if (!isNaN(value) && value >= min && value <= max) {
                    sendConfigUpdate(key, value);
                } else {
                    logMessage(`Invalid ${key} value. Must be between ${min} and ${max}.`, "error");
                }
            });
        }
    }

    // Movement Commands Event Listeners
    btnMoveTo.addEventListener("click", () => {
        const x = parseFloat(moveXInput.value);
        const y = parseFloat(moveYInput.value);
        const z = parseFloat(moveZInput.value);

        const speed = parseFloat(moveSpeedInput.value);
        if (!isNaN(x) && !isNaN(y) && !isNaN(z) && !isNaN(speed)) {
            sendMovementCommand("move", { x: x, y: y, z: z, speed: speed });
        } else {
            logMessage("Invalid X, Y, or Z movement values.", "error");
        }
    });

    btnHome.addEventListener("click", () => {
        sendMovementCommand("home");
    });

    btnJog.addEventListener("click", () => {
        const dx = parseFloat(jogDxInput.value);
        const dy = parseFloat(jogDyInput.value);
        const dz = parseFloat(jogDzInput.value);

        if (!isNaN(dx) && !isNaN(dy) && !isNaN(dz)) {
            sendMovementCommand("jog", { dx: dx, dy: dy, dz: dz });
        } else {
            logMessage("Invalid dX, dY, or dZ jog values.", "error");
        }
    });

    btnPosQuery.addEventListener("click", () => {
        sendMovementCommand("pos");
    });

    btnStatusQuery.addEventListener("click", () => {
        sendMovementCommand("status");
    });

    // Laser/Tool Commands Event Listeners
    btnToolOn.addEventListener("click", () => {
        const toolNumber = parseInt(toolNumberInput.value, 10);
        if (!isNaN(toolNumber) && toolNumber >= 1 && toolNumber <= 2) {
            sendLaserCommand("tool_on", { tool_number: toolNumber });
        } else {
            logMessage("Invalid tool number. Must be 1 (Laser) or 2 (Servo).", "error");
        }
    });

    btnToolOff.addEventListener("click", () => {
        const toolNumber = parseInt(toolNumberInput.value, 10);
        if (!isNaN(toolNumber) && toolNumber >= 1 && toolNumber <= 2) {
            sendLaserCommand("tool_off", { tool_number: toolNumber });
        } else {
            logMessage("Invalid tool number. Must be 1 (Laser) or 2 (Servo).", "error");
        }
    });

    btnFire.addEventListener("click", () => {
        const value = parseInt(fireValueInput.value, 10);
        if (!isNaN(value) && value >= 0 && value <= 255) {
            sendLaserCommand("fire_tool", { value: value });
        } else {
            logMessage("Invalid fire value. Must be between 0 and 255.", "error");
        }
    });

    // btnGetCurrentToolStatus.addEventListener("click", () => {
    //     sendLaserCommand("tool_status");
    // });

    // LED Control Event Listeners
    btnLedOn.addEventListener("click", () => {
        sendLedCommand("set_state", { state: 1 });
    });

    btnLedOff.addEventListener("click", () => {
        sendLedCommand("set_state", { state: 0 });
    });

    // Arbitrary Arduino Command Event Listener
    sendArduinoCommandBtn.addEventListener("click", () => {
        const command = arduinoCommandInput.value;
        if (command) {
            sendRawCommand(command);
            arduinoCommandInput.value = ""; // Clear input after sending
        } else {
            logMessage("Please enter an Arduino command to send.", "warning");
        }
    });



    // Theme switching logic
    const themeSwitch = document.getElementById('theme-switch');
    const body = document.body;

    function applyTheme(theme) {
        if (theme === 'dark') {
            body.classList.add('dark-theme');
            if (themeSwitch) themeSwitch.checked = true;
        } else {
            body.classList.remove('dark-theme');
            if (themeSwitch) themeSwitch.checked = false;
        }
    }

    // Load theme on page load
    const storedTheme = localStorage.getItem('theme');
    if (storedTheme) {
        applyTheme(storedTheme);
    } else {
        // Default to light theme if no preference is found
        applyTheme('light');
    }

    // Event listener for theme switch
    if (themeSwitch) {
        themeSwitch.addEventListener('change', () => {
            const newTheme = themeSwitch.checked ? 'dark' : 'light';
            applyTheme(newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }

    // THEME SWITCH

    const toggle = document.getElementById("theme-toggle");

    // load saved theme
    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark-theme");
        toggle.checked = true;
    }

    toggle.addEventListener("change", () => {
        document.body.classList.toggle("dark-theme");

        if (document.body.classList.contains("dark-theme")) {
            localStorage.setItem("theme", "dark");
        } else {
            localStorage.setItem("theme", "light");
        }
    });

    // Initial websocket connection
    connectWebSocket();
});