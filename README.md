# LED + Button over WebSockets

Built on top of https://github.com/julianlaxamana/websockets-examples.

Two things happen, both in real time:
- A button on the website turns a **physical LED** on/off.
- Pressing a **physical button** updates a counter/log on the website.

## How it works

```
[Physical Button] --> Pico (MicroPython) --> USB Serial --> bridge --> WS server --> Browser
[Browser button]  <-- USB Serial <-- Pico <-- bridge      <-- WS server <-- Browser
```

- **pico/main.py** — MicroPython firmware. Watches the button pin, prints
  `BTN:PRESSED` / `BTN:RELEASED` over USB serial, and listens for
  `LED_ON` / `LED_OFF` / `LED_TOGGLE` commands to drive the LED pin.
- **serial/client.py** — runs on your computer. Bidirectional bridge between
  the Pico's serial port and the WebSocket server.
- **websockets/server/server.py** — plain relay: broadcasts whatever it
  receives to every other connected client.
- **websockets/client/** — the React/Vite site. Has an LED on/off button and
  a live counter + log fed by the Pico's button presses.

## Hardware / wiring

You need a Raspberry Pi Pico (or Pico W), an LED, a push button, a couple
of ~220-330 ohm resistors, and a breadboard.

- **LED**: GPIO 15 → long leg (anode) of LED → short leg → resistor → GND
- **Button**: GPIO 14 → one leg of button → other leg → 3V3
  (the firmware uses an internal `PULL_DOWN`, so the pin reads LOW when the
  button is untouched and HIGH when pressed)

Change `LED_PIN` / `BUTTON_PIN` at the top of `pico/main.py` if you wire
different GPIOs.

## Setup

1. **Flash the Pico**
   - Open `pico/main.py` in Thonny (or your MicroPython tool of choice).
   - Save it *onto the Pico* as `main.py` so it auto-runs on boot.

2. **Find the serial port**
   ```bash
   cd serial
   pip install pyserial
   python find-ports.py
   ```
   Copy the port it prints (e.g. `/dev/cu.usbmodem1201`, `COM3`, or
   `/dev/ttyACM0`) into `SERIAL_PORT` in `serial/client.py`.

3. **Install server deps**
   ```bash
   pip install websockets pyserial
   ```

4. **Install frontend deps**
   ```bash
   cd websockets/client
   npm install
   ```

## Running it (4 terminals)

1. **WebSocket server**
   ```bash
   cd websockets/server
   python server.py
   ```
2. **Serial bridge** (Pico must already be plugged in and running main.py)
   ```bash
   cd serial
   python client.py
   ```
3. **Frontend**
   ```bash
   cd websockets/client
   npm run dev
   ```
4. Open the printed local URL (usually http://localhost:5173) in your
   browser.

Click **Turn LED On** on the site — the physical LED should light up.
Press the physical button — the "Physical button presses" counter on the
site should increment and the log should show `BTN:PRESSED`.

## Troubleshooting

- **Bridge can't open the serial port**: re-run `find-ports.py`, make sure
  nothing else (like Thonny's REPL) has the port open, and double check
  `SERIAL_PORT` in `serial/client.py`.
- **LED never turns on**: check the LED's polarity (flat side / short leg
  is the cathode → goes toward GND) and that the resistor is in the loop.
- **Button never triggers**: confirm wiring matches `PULL_DOWN` (button
  pulls the pin HIGH when pressed) — if you wired it the other way, use
  `Pin.PULL_UP` in `main.py` and flip the `if current_state == 1` logic.
- **Site says "Not connected"**: make sure `server.py` is running before
  you load the page, and that you haven't changed the port from `8765`.
