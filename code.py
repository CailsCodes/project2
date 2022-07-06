from time import sleep, time

from math import sin

import alarm
import board
import displayio
from analogio import AnalogIn
from busio import SPI
from digitalio import DigitalInOut, Pull
from terminalio import FONT
from vectorio import Rectangle

import adafruit_displayio_ssd1305
from DS1302 import DS1302 as Clock
from adafruit_display_text.label import Label

#------------------------------------------------
# For potentiometer

POTENTIOMETER_PIN = board.GP26
potent_analog_in = AnalogIn(POTENTIOMETER_PIN)

def get_voltage(analog_in):
    return((analog_in.value * 3.3) / 65025)

# MAX_VOL = 3.3
# MIN_VOL = 0.01

# -----------------------------------------------
# For buttons

FORWARD_PIN     = board.GP0 
BACK_PIN        = board.GP1 
SWITCH_PIN      = board.GP20

def init_input(PIN):
    _input = DigitalInOut(PIN)
    _input.switch_to_input(pull=Pull.DOWN)
    return _input

forward = init_input(FORWARD_PIN)
back = init_input(BACK_PIN)
switch = init_input(SWITCH_PIN)


#------------------------------------------------
# For RTC / Clock

rtc = Clock()

#------------------------------------------------
# For display

BLACK = displayio.Palette(1)
BLACK[0] = 0x000000

WHITE = displayio.Palette(1)
WHITE[0] = 0xFFFFFF

WIDTH       = 128
HEIGHT      = 32

OLED_DC_PIN     = board.GP8
OLED_CS_PIN     = board.GP9
OLED_CLK_PIN    = board.GP10
OLED_MOSI_PIN   = board.GP11
OLED_RESET_PIN  = board.GP12

displayio.release_displays()
spi = SPI(clock=OLED_CLK_PIN, MOSI=OLED_MOSI_PIN)
display_bus = displayio.FourWire(spi, command=OLED_DC_PIN, chip_select=OLED_CS_PIN, baudrate=1000000, reset=OLED_RESET_PIN)
display = adafruit_displayio_ssd1305.SSD1305(display_bus, width=WIDTH, height=HEIGHT)

#-----------------------------------------------
# Draw background

canvas = displayio.Group()
display.show(canvas)
display.rotation = 180

background = displayio.Bitmap(display.width, display.height, 1)
bg_sprite = displayio.TileGrid(background, pixel_shader=BLACK, x=0, y=0)
canvas.append(bg_sprite)

#-----------------------------------------------


def to_sleep():
    """Put microcontroller to sleep"""
    switch.deinit()
    switch_alarm = alarm.pin.PinAlarm(SWITCH_PIN, value=True, edge=True)
    alarm.light_sleep_until_alarms(switch_alarm)
    return init_input(SWITCH_PIN)


def draw_text_center(text, y=0):
    text_area = Label(FONT, text=text, color=WHITE[0])
    text_width = text_area.bounding_box[2]
    x_pos = (display.width // 2) - (text_width // 2)
    text_group = displayio.Group(x=x_pos, y=y)
    text_group.append(text_area)
    return text_group


def convert_voltage(voltage):
    # return int(voltage//0.033)
    return int(voltage//0.066) * 2


def input_status():
    return not any([forward.value, back.value, switch.value])


def clock():
    global canvas

    clock_index = len(canvas)
    date_index = clock_index + 1

    while input_status():
        year, month, day, _, hour, minute, second = rtc.DateTime()
        _time = f"{hour:02d}:{minute:02d}:{second:02d}"
        _date = f"{day:02d}/{month:02d}/{year}"
        clock_text = draw_text_center(_time, 5)
        date_text = draw_text_center(_date, 20)

        try:
            canvas[clock_index] = clock_text
        except IndexError:
            canvas.append(clock_text)
            canvas.append(date_text)

    else:
        _ = canvas.pop(date_index)
        _ = canvas.pop(clock_index)
        return


def volume():
    global canvas

    text_index = len(canvas)
    bar_index = text_index + 1

    text_group = draw_text_center("Volume", y=11)
    canvas.append(text_group)

    while input_status():
        volts = get_voltage(potent_analog_in)
        vol = max(convert_voltage(volts), 1)
        vol_bar = Rectangle(pixel_shader=WHITE, width=vol, height=10, x=14, y=21)
        try:
            canvas[bar_index] = vol_bar
        except IndexError:
            canvas.append(vol_bar)
    else:
        _ = canvas.pop(bar_index)
        _ = canvas.pop(text_index)
        return


def frequency():
    global canvas

    sine_index = len(canvas)

    sine_palette = displayio.Palette(2)
    sine_palette[0] = BLACK[0]
    sine_palette[1] = WHITE[0]

    sine_wave = displayio.Bitmap(display.width, 20, 2)
    sw_sprite = displayio.TileGrid(sine_wave, pixel_shader=sine_palette, x=0, y=11)
    canvas.append(sw_sprite)

    start = time()

    while input_status():
        h = (start - time()) * 10
        volts = get_voltage(potent_analog_in)
        b = max(convert_voltage(volts), 2)
        
        sine_wave.fill(0)

        for x in range(display.width):
            y = int(10 * sin((x - h) / b) + 10)
            try:
                sine_wave[x,y] = 1
            except IndexError:
                pass

        sine_wave.dirty()
        sleep(0.2)

    else:
        _ = canvas.pop(sine_index)
        return


menu = {
    0 : clock,
    1 : volume,
    2 : frequency
    }

window = 0
num_windows = len(menu) - 1

while True:
    sleep(0.1)
    menu[window]()

    if forward.value:
        window += 1 if window < num_windows else -num_windows
    elif back.value:
        window -= 1 if window > 0 else -num_windows

    while forward.value or back.value:
        pass

    if switch.value:
        switch = to_sleep()

    
    
