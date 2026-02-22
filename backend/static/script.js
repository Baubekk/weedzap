document.addEventListener("DOMContentLoaded", () => {
    const wsStatus = document.getElementById("ws-status");
    const logOutput = document.getElementById("log-output");
    const cameraFeed = document.getElementById("cameraFeed");

    const currentStepsX = document.getElementById("current-steps_x");
    const currentStepsY = document.getElementById("current-steps_y");
    const currentStepsZ = document.getElementById("current-steps_z");
    const currentLimitX = document.getElementById("current-limit_x");
    const currentLimitY = document.getElementById("current-limit_y");
    const currentLimitZ = document.getElementById("current-limit_z");
    const currentMaxSpeed = document.getElementById("current-max_speed");
    const currentAccel = document.getElementById("current-accel");

    const setStepsXInput = document.getElementById("set-steps_x");
    const btnSetStepsX = document.getElementById("btn-set-steps_x");
    const setStepsYInput = document.getElementById("set-steps_y");
    const btnSetStepsY = document.getElementById("btn-set-steps_y");
    const setStepsZInput = document.getElementById("set-steps_z");
    const btnSetStepsZ = document.getElementById("btn-set-steps_z");
    const setLimitXInput = document.getElementById("set-limit_x");
    const btnSetLimitX = document.getElementById("btn-set-limit_x");
    const setLimitYInput = document.getElementById("set-limit_y");
    const btnSetLimitY = document.getElementById("btn-set-limit_y");
    const setLimitZInput = document.getElementById("set-limit_z");
    const btnSetLimitZ = document.getElementById("btn-set-limit_z");
    const setMaxSpeedInput = document.getElementById("set-max_speed");
    const btnSetMaxSpeed = document.getElementById("btn-set-max_speed");
    const setAccelInput = document.getElementById("set-accel");
    const btnSetAccel = document.getElementById("btn-set-accel");

    const moveXInput = document.getElementById("move-x");
    const moveYInput = document.getElementById("move-y");
    const moveZInput = document.getElementById("move-z");
    const moveSpeedInput = document.getElementById("move-speed");
    const btnMoveTo = document.getElementById("btn-move-to");
    const btnHome = document.getElementById("btn-home");

    const setToolModeSelect = document.getElementById("set-tool-mode");
    const btnSetToolMode = document.getElementById("btn-set-tool-mode");
    const btnFireTool = document.getElementById("btn-fire-tool");
    const btnStopTool = document.getElementById("btn-stop-tool");

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
        };

        websocket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            // logMessage(`Received: ${JSON.stringify(message)}`);

            if (message.type === "camera_frame") {
                cameraFeed.src = `data:image/jpeg;base64,${message.data}`;
            } else if (message.type === "config_ack" && message.status === "success") {
                logMessage("Config update acknowledged successfully. Fetching latest config.");
                fetchCurrentConfig();
            } else if (message.type.endsWith("_ack")) {
                logMessage(`ACK Received: Type - ${message.type}, Status - ${message.status}, Message - ${message.message || "No additional message."}`);
            } else {
                logMessage(`Unhandled message type: ${message.type}`, "warning");
            }
        };

        websocket.onclose = () => {
            wsStatus.textContent = "Disconnected";
            wsStatus.style.color = "red";
            logMessage("Websocket disconnected. Attempting to reconnect in 5 seconds...", "warning");
            setTimeout(connectWebSocket, 5000); // Attempt to reconnect
        };

        websocket.onerror = (error) => {
            logMessage(`Websocket error: ${error.message}`, "error");
            wsStatus.textContent = "Error";
            wsStatus.style.color = "red";
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

            // Dynamically update UI elements based on the config
            for (const key in config) {
                const element = document.getElementById(`current-${key}`);
                if (element) {
                    element.textContent = config[key];
                } else {
                    logMessage(`Config parameter '${key}': ${config[key]} (No specific UI element found, logging instead)`);
                }
            }
        } catch (error) {
            logMessage(`Error fetching config: ${error}`, "error");
        }
    }

    function sendWebSocketMessage(type, command, data) {
        const message = {
            type: type,
            command: command,
            data: data
        };
        if (websocket.readyState === WebSocket.OPEN) {
            websocket.send(JSON.stringify(message));
            logMessage(`Sent: ${JSON.stringify(message)}`);
        } else {
            logMessage("Websocket not connected.", "error");
        }
    }

    // Configuration Commands (Websocket)
    function sendConfigCommand(param, value) {
        const message = {
            type: "config",
            param: param,
            value: value
        };
        if (websocket.readyState === WebSocket.OPEN) {
            websocket.send(JSON.stringify(message));
            logMessage(`Sent: ${JSON.stringify(message)}`);
        } else {
            logMessage("Websocket not connected.", "error");
        }
    }

    btnSetStepsX.addEventListener("click", () => {
        const value = parseFloat(setStepsXInput.value);
        if (!isNaN(value) && value >= 0 && value <= 10000) {
            sendConfigCommand("steps_x", value);
        } else {
            logMessage("Invalid steps_x value. Must be between 0 and 10000.", "error");
        }
    });

    btnSetStepsY.addEventListener("click", () => {
        const value = parseFloat(setStepsYInput.value);
        if (!isNaN(value) && value >= 0 && value <= 10000) {
            sendConfigCommand("steps_y", value);
        } else {
            logMessage("Invalid steps_y value. Must be between 0 and 10000.", "error");
        }
    });

    btnSetStepsZ.addEventListener("click", () => {
        const value = parseFloat(setStepsZInput.value);
        if (!isNaN(value) && value >= 0 && value <= 10000) {
            sendConfigCommand("steps_z", value);
        } else {
            logMessage("Invalid steps_z value. Must be between 0 and 10000.", "error");
        }
    });

    btnSetLimitX.addEventListener("click", () => {
        const value = parseFloat(setLimitXInput.value);
        if (!isNaN(value) && value >= 0 && value <= 10000) {
            sendConfigCommand("limit_x", value);
        } else {
            logMessage("Invalid limit_x value. Must be between 0 and 10000.", "error");
        }
    });

    btnSetLimitY.addEventListener("click", () => {
        const value = parseFloat(setLimitYInput.value);
        if (!isNaN(value) && value >= 0 && value <= 10000) {
            sendConfigCommand("limit_y", value);
        } else {
            logMessage("Invalid limit_y value. Must be between 0 and 10000.", "error");
        }
    });

    btnSetLimitZ.addEventListener("click", () => {
        const value = parseFloat(setLimitZInput.value);
        if (!isNaN(value) && value >= 0 && value <= 10000) {
            sendConfigCommand("limit_z", value);
        } else {
            logMessage("Invalid limit_z value. Must be between 0 and 10000.", "error");
        }
    });

    btnSetMaxSpeed.addEventListener("click", () => {
        const value = parseFloat(setMaxSpeedInput.value);
        if (!isNaN(value) && value >= 0 && value <= 10000) {
            sendConfigCommand("max_speed", value);
        } else {
            logMessage("Invalid max_speed value. Must be between 0 and 10000.", "error");
        }
    });

    btnSetAccel.addEventListener("click", () => {
        const value = parseFloat(setAccelInput.value);
        if (!isNaN(value) && value >= 0 && value <= 10000) {
            sendConfigCommand("accel", value);
        } else {
            logMessage("Invalid accel value. Must be between 0 and 10000.", "error");
        }
    });

    // Movement Commands (Websocket)
    btnMoveTo.addEventListener("click", () => {
        const x = parseFloat(moveXInput.value);
        const y = parseFloat(moveYInput.value);
        const z = parseFloat(moveZInput.value);
        // const speed = parseFloat(moveSpeedInput.value); // Speed is not part of the movement message in the new spec

        if (!isNaN(x) && !isNaN(y) && !isNaN(z)) {
            sendWebSocketMessage("movement", "move", { x: x, y: y, z: z });
        } else {
            logMessage("Invalid X, Y, or Z movement values.", "error");
        }
    });

    btnHome.addEventListener("click", () => {
        sendWebSocketMessage("movement", "home", {});
    });

    // Laser/Tool Commands (Websocket)
    btnSetToolMode.addEventListener("click", () => {
        const toolMode = setToolModeSelect.value;
        sendWebSocketMessage("laser", "set_tool_mode", { tool_mode: toolMode });
    });
    // Also listen for change event on the select element itself
    setToolModeSelect.addEventListener("change", () => {
        const toolMode = setToolModeSelect.value;
        sendWebSocketMessage("laser", "set_tool_mode", { tool_mode: toolMode });
    });

    btnFireTool.addEventListener("click", () => {
        // Assuming a default value or a configured value for now, as no input field is specified
        const value = 255; // Example default value for firing power
        sendWebSocketMessage("laser", "fire_tool", { value: value });
    });

    btnStopTool.addEventListener("click", () => {
        sendWebSocketMessage("laser", "stop_tool", {});
    });

    // Initial websocket connection
    connectWebSocket();
});