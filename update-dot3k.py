#!/usr/bin/env python

import signal

import dot3k.lcd as lcd
import dot3k.joystick as nav
import dot3k.backlight as backlight
import pihole as ph
import threading
import time
import psutil

DELAY = 5

backlight.off()
threads = []


def queries_thread():
    """Print pihole stats to the lcd"""

    lcd.clear()
    t = threading.currentThread()
    while getattr(t, "running", True):
        pihole = ph.PiHole("192.168.1.32")

        lcd.set_cursor_position(0, 0)
        lcd.write('{} queries'.format(pihole.queries))

        lcd.set_cursor_position(0, 1)
        lcd.write('{}% blocked'.format(pihole.ads_percentage))

        lcd.set_cursor_position(0, 2)
        lcd.write('{} total'.format(pihole.blocked))

        time.sleep(5)


def system_thread():
    """Print system load, memory usage, and temperature to the lcd"""

    lcd.clear()
    t = threading.currentThread()
    while getattr(t, "running", True):
        pihole = ph.PiHole("192.168.1.32")

        one_minute, five_minute, fifteen_minute = [
            x / psutil.cpu_count() * 100 for x in psutil.getloadavg()]
        memory = psutil.virtual_memory()
        temp = psutil.sensors_temperatures(
            fahrenheit=True)['cpu-thermal'][0]

        lcd.set_cursor_position(0, 0)
        lcd.write('Load {}'.format(one_minute))

        lcd.set_cursor_position(0, 1)
        lcd.write('Memory {}'.format(memory.percent))

        lcd.set_cursor_position(0, 2)
        lcd.write('{} F'.format(temp.current))

        time.sleep(5)


def thread_cleanup():
    """Pop the current running thread if possible, set the running flag False, and stop the thread"""

    if len(threads) > 0:
        print "cleaning up"
        t = threads.pop()
        t.running = False
        t.join()


@nav.on(nav.UP)
def handle_up(pin):
    thread_cleanup()

    t = threading.Thread(target=queries_thread)
    threads.append(t)
    t.start()


@nav.on(nav.DOWN)
def handle_down(pin):
    thread_cleanup()

    t = threading.Thread(target=system_thread)
    threads.append(t)
    t.start()


if __name__ == "__main__":
    try:
        signal.pause()
    except KeyboardInterrupt:
        thread_cleanup()
