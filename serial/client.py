"""
Runs on your computer. Bridges the Pico's USB serial connection to the
WebSocket server, in both directions:

  Pico -> serial -> this bridge -> WebSocket server -> browser
  browser -> WebSocket server -> this bridge -> serial -> Pico

Run find-ports.py first to get your SERIAL_PORT value.
"""
import asyncio
import json
from datetime import datetime

import serial
import websockets

# ---- Configuration ----
SERIAL_PORT = '/dev/cu.usbmodem1201'  # 'COM3' on Windows, '/dev/ttyACM0' on Linux
BAUD_RATE = 115200
WEBSOCKET_URL = 'ws://localhost:8765'


async def bridge():
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0)
    print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud")

    async with websockets.connect(WEBSOCKET_URL) as ws:
        print(f"Connected to WebSocket server at {WEBSOCKET_URL}")

        async def read_serial_send_ws():
            """Lines from the Pico (e.g. BTN:PRESSED) go out to the website."""
            buffer = b""
            while True:
                if ser.in_waiting:
                    buffer += ser.read(ser.in_waiting)
                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        text = line.decode("utf-8", errors="ignore").strip()
                        if text:
                            print(f"Serial -> {text}")
                            payload = {
                                "source": "device",
                                "line": text,
                                "timestamp": datetime.now().isoformat(),
                            }
                            await ws.send(json.dumps(payload))
                await asyncio.sleep(0.01)

        async def read_ws_send_serial():
            """Commands from the website (e.g. LED_ON) go out to the Pico."""
            async for message in ws:
                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    continue
                if data.get("source") == "device":
                    continue  # ignore device events relayed back to us
                command = data.get("command")
                if command:
                    print(f"WS -> Serial: {command}")
                    ser.write((command + "\n").encode("utf-8"))

        await asyncio.gather(read_serial_send_ws(), read_ws_send_serial())


if __name__ == "__main__":
    try:
        asyncio.run(bridge())
    except KeyboardInterrupt:
        print("Interrupted")
    except serial.SerialException as e:
        print(f"Serial error: {e}")
        print("Check SERIAL_PORT — run find-ports.py to list available ports.")
