"""
Runs on the Raspberry Pi Pico (MicroPython).
Save this file as main.py on the Pico itself (it auto-runs on boot).

Wiring:
  LED_PIN     -> long leg of LED -> LED -> resistor (~220-330 ohm) -> GND
  BUTTON_PIN  -> one leg of button -> other leg -> 3V3 (we use PULL_DOWN,
                 so the pin reads LOW when unpressed and HIGH when pressed)

Protocol over USB serial (one message per line):
  Pico -> host:  "BTN:PRESSED"   when the button is pressed
                 "BTN:RELEASED"  when the button is released
  host -> Pico:  "LED_ON"        turn the LED on
                 "LED_OFF"       turn the LED off
                 "LED_TOGGLE"    flip the LED state
"""
import sys
import select
import time
from machine import Pin

# ---- Configuration: change these to match your wiring ----
LED_PIN = 15
BUTTON_PIN = 14
DEBOUNCE_MS = 50

led = Pin(LED_PIN, Pin.OUT)
button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_DOWN)
led.value(0)

# Poll stdin (the USB serial connection) without blocking, so the loop
# can watch the button and read incoming commands at the same time.
poll = select.poll()
poll.register(sys.stdin, select.POLLIN)


def read_command():
    """Return a line sent from the host, or None if nothing is waiting."""
    if poll.poll(0):
        line = sys.stdin.readline()
        return line.strip()
    return None


last_state = button.value()
last_change = time.ticks_ms()

while True:
    # 1. Handle any command coming from the website (via the bridge)
    cmd = read_command()
    if cmd == "LED_ON":
        led.value(1)
    elif cmd == "LED_OFF":
        led.value(0)
    elif cmd == "LED_TOGGLE":
        led.toggle()

    # 2. Watch the physical button, debounced
    current_state = button.value()
    now = time.ticks_ms()
    if current_state != last_state and time.ticks_diff(now, last_change) > DEBOUNCE_MS:
        last_change = now
        last_state = current_state
        if current_state == 1:
            print("BTN:PRESSED")
        else:
            print("BTN:RELEASED")

    time.sleep_ms(10)
