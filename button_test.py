import digitalio
import board
import time


btn1 = digitalio.DigitalInOut(board.GP20)
btn1.switch_to_input(pull=digitalio.Pull.DOWN)


while True:
    time.sleep(1)
    print(btn1.value)