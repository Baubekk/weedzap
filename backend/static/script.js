document.addEventListener('DOMContentLoaded', () => {
    const wsStatus = document.getElementById('ws-status');
    const logOutput = document.getElementById('log-output');
    const cameraFeed = document.getElementById('cameraFeed');

    const currentSpeed = document.getElementById('current-speed');
    const currentAcceleration = document.getElementById('current-acceleration');
    const currentMovementMode = document.getElementById('current-movement-mode');
    const currentLaserState = document.getElementById('current-laser-state');

    const setSpeedInput = document.getElementById('set-speed');
    const btnSetSpeed = document.getElementById('btn-set-speed');
    const setAccelerationInput = document.getElementById('set-acceleration');
    const btnSetAcceleration = document.getElementById('btn-set-acceleration');
    const setMovementModeSelect = document.getElementById('set-movement-mode');
    const btnSetMovementMode = document.getElementById('btn-set-movement-mode');
    const setLaserStateSelect = document.getElementById('set-laser-state');
    const btnSetLaserState = document.getElementById('btn-set-laser-state');

    const btnHold = document.querySelectorAll('.btn-hold');
    const stepValueInput = document.getElementById('step-value');
    const btnStep = document.querySelectorAll('.btn-step');
    const btnFireLaser = document.getElementById('btn-fire-laser');

    let websocket;
    let isLaserFiring = false; // To track laser firing state for toggle button

    function logMessage(message, type = 'info') {
        const p = document.createElement('p');
        p.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        if (type === 'error') p.style.color = 'red';
        if (type === 'warning') p.style.color = 'orange';
        logOutput.appendChild(p);
        logOutput.scrollTop = logOutput.scrollHeight;
    }

    function connectWebSocket() {
        websocket = new WebSocket('ws://localhost:8000/ws');

        websocket.onopen = () => {
            wsStatus.textContent = 'Connected';
            wsStatus.style.color = 'green';
            logMessage('Websocket connected.');
            fetchCurrentConfig(); // Fetch initial config on connection
        };

        websocket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            // logMessage(`Received: ${JSON.stringify(message)}`);
            // Handle responses from the websocket if needed
            // For example, if the backend sends updates to config, update UI here
            if (message.type === "camera_frame") {
                cameraFeed.src = `data:image/jpeg;base64,${message.data}`;
            }
        };

        websocket.onclose = () => {
            wsStatus.textContent = 'Disconnected';
            wsStatus.style.color = 'red';
            logMessage('Websocket disconnected. Attempting to reconnect in 5 seconds...', 'warning');
            setTimeout(connectWebSocket, 5000); // Attempt to reconnect
        };

        websocket.onerror = (error) => {
            logMessage(`Websocket error: ${error.message}`, 'error');
            wsStatus.textContent = 'Error';
            wsStatus.style.color = 'red';
        };
    }

    async function fetchCurrentConfig() {
        try {
            const response = await fetch('/config/laser');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const config = await response.json();
            currentSpeed.textContent = config.laser_speed;
            currentAcceleration.textContent = config.laser_acceleration;
            currentMovementMode.textContent = config.laser_movement_mode;
            currentLaserState.textContent = config.laser_state;
            logMessage('Fetched current laser configuration.');
        } catch (error) {
            logMessage(`Error fetching config: ${error}`, 'error');
        }
    }

    async function sendConfigUpdate(endpoint, body) {
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(body)
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            logMessage(`Successfully updated ${endpoint.split('/').pop()}.`);
            fetchCurrentConfig(); // Refresh displayed config
        } catch (error) {
            logMessage(`Error updating config for ${endpoint}: ${error}`, 'error');
        }
    }

    // Event Listeners for Configuration Controls
    btnSetSpeed.addEventListener('click', () => {
        const speed = parseFloat(setSpeedInput.value);
        if (!isNaN(speed) && speed >= 0 && speed <= 10000) {
            sendConfigUpdate('/config/laser/speed', { laser_speed: speed });
        } else {
            logMessage('Invalid speed value. Must be between 0 and 10000.', 'error');
        }
    });

    btnSetAcceleration.addEventListener('click', () => {
        const acceleration = parseFloat(setAccelerationInput.value);
        if (!isNaN(acceleration) && acceleration >= 0 && acceleration <= 10000) {
            sendConfigUpdate('/config/laser/acceleration', { laser_acceleration: acceleration });
        } else {
            logMessage('Invalid acceleration value. Must be between 0 and 10000.', 'error');
        }
    });

    btnSetMovementMode.addEventListener('click', () => {
        const mode = setMovementModeSelect.value;
        sendConfigUpdate('/config/laser/movement-mode', { laser_movement_mode: mode });
    });

    btnSetLaserState.addEventListener('click', () => {
        const state = setLaserStateSelect.value;
        sendConfigUpdate('/config/laser/state', { laser_state: state });
    });

    // Event Listeners for Movement Controls (Websocket)
    btnHold.forEach(button => {
        button.addEventListener('mousedown', () => {
            const axis = button.dataset.axis;
            const positive = button.dataset.positive === 'true';
            const message = {
                type: 'laser',
                data: {
                    component: 'movement',
                    data: {
                        mode: 'hold',
                        data: {
                            axis: axis,
                            active: true,
                            positive: positive
                        }
                    }
                }
            };
            if (websocket.readyState === WebSocket.OPEN) {
                websocket.send(JSON.stringify(message));
                logMessage(`Sent hold movement: ${JSON.stringify(message)}`);
            } else {
                logMessage('Websocket not connected for hold movement.', 'error');
            }
        });

        button.addEventListener('mouseup', () => {
            const axis = button.dataset.axis;
            const message = {
                type: 'laser',
                data: {
                    component: 'movement',
                    data: {
                        mode: 'hold',
                        data: {
                            axis: axis,
                            active: false, // Stop holding
                            positive: true // Value doesn't matter when active is false
                        }
                    }
                }
            };
            if (websocket.readyState === WebSocket.OPEN) {
                websocket.send(JSON.stringify(message));
                logMessage(`Sent stop hold movement: ${JSON.stringify(message)}`);
            } else {
                logMessage('Websocket not connected for stop hold movement.', 'error');
            }
        });
    });

    btnStep.forEach(button => {
        button.addEventListener('click', () => {
            const axis = button.dataset.axis;
            const value = parseInt(stepValueInput.value);
            if (!isNaN(value)) {
                const message = {
                    type: 'laser',
                    data: {
                        component: 'movement',
                        data: {
                            mode: 'step',
                            data: {
                                axis: axis,
                                value: value
                            }
                        }
                    }
                }
                if (websocket.readyState === WebSocket.OPEN) {
                    websocket.send(JSON.stringify(message));
                    logMessage(`Sent step movement: ${JSON.stringify(message)}`);
                } else {
                    logMessage('Websocket not connected for step movement.', 'error');
                }
            } else {
                logMessage('Invalid step value. Must be an integer.', 'error');
            }
        });
    });

    // Event Listener for Firing Control (Websocket)
    btnFireLaser.addEventListener('click', () => {
        const newState = !isLaserFiring; // Toggle state
        const message = {
            type: 'laser',
            data: {
                component: 'firing',
                data: {
                    active: newState
                }
            }
        };
        if (websocket.readyState === WebSocket.OPEN) {
            websocket.send(JSON.stringify(message));
            isLaserFiring = newState;
            btnFireLaser.textContent = isLaserFiring ? 'Stop Firing' : 'Fire Laser (Toggle)';
            logMessage(`Sent laser firing command: ${JSON.stringify(message)}`);
        } else {
            logMessage('Websocket not connected for laser firing.', 'error');
        }
    });

    // Initial websocket connection
    connectWebSocket();
});