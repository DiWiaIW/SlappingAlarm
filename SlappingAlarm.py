import RPi.GPIO as GPIO
import time
import sys
import tm1637
from datetime import datetime

# Initialize the display module
tm = tm1637.TM1637(clk=3, dio=2, brightness=2)
tm.show("", True)

# GPIO setup
GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

# Define modes and keys
MODE_SHOW_CURRENT_TIME = 1
MODE_SETTING_ALARM = 2
mode = MODE_SHOW_CURRENT_TIME

STR_NO_ALARM = '-- --'
KEY_SHOW_ALARM = 'A'  # Press to show alarm time
KEY_CHANGE_ALARM = 'B'  # Click and type in alarm time, click again to set
KEY_CLEAR_ALARM = 'C'  # Clear 1 digit when setting alarm
ROW = [25, 8, 7, 1]
COL = [12, 16, 20, 21]

MAP = [["D", "#", "0", "*"], ["C", "9", "8", "7"], ["B", "6", "5", "4"], ["A", "3", "2", "1"]]

# Setup GPIO pins
for pin in ROW:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

for pin in COL:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Function to scan the keypad
def scan():
    for r in range(0, len(ROW), 1):
        GPIO.output(ROW[r], GPIO.HIGH)
        for c in range(0, len(COL), 1):
            if GPIO.input(COL[c]) == GPIO.HIGH:
                while GPIO.input(COL[c]) == GPIO.HIGH:
                    time.sleep(0.1)
                GPIO.output(ROW[r], GPIO.LOW)
                return MAP[r][c]
        GPIO.output(ROW[r], GPIO.LOW)
    return None

# Main loop
alarm = list("----")
alarm_index = 0
display_str = ""
try:
    while True:
        key = scan()  # key = None if there is no key pressed

        if key != None:
            print(" Entered: " + key)
            if mode == MODE_SHOW_CURRENT_TIME:
                if key == KEY_CHANGE_ALARM:
                    mode = MODE_SETTING_ALARM
            elif mode == MODE_SETTING_ALARM:
                if '0' <= key <= '9':
                    if alarm_index < 4:
                        alarm[alarm_index] = key
                        alarm_index += 1
                elif key == KEY_CLEAR_ALARM:
                    if alarm_index > 0:
                        alarm_index -= 1
                        alarm[alarm_index] = "-"
                elif key == KEY_CHANGE_ALARM:
                    print("alarm set to " + f"{alarm[0]}{alarm[1]}:{alarm[2]}{alarm[3]}")
                    mode = MODE_SHOW_CURRENT_TIME

        current_time = list(datetime.now().strftime("%H%M"))
        dot = ":"
        if int(datetime.now().strftime("%S")) % 2 == 0:
            dot = " "

        if mode == MODE_SHOW_CURRENT_TIME:
            if current_time == alarm:
                print(" Alarm triggered!")
            display_str = ''.join([current_time[0], current_time[1], dot, current_time[2], current_time[3]])
        elif mode == MODE_SETTING_ALARM:
            display_str = f"{alarm[0]}{alarm[1]}:{alarm[2]}{alarm[3]} setting alarm mode"

        print(f'\r{display_str}', end='')
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Bye bye")
    GPIO.cleanup()
]]