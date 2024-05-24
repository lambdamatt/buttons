import board
from telephony.inputs import Button
from telephony.joystick import Joystick
joystick = Joystick()

joystick.add_input(
    Button(board.GP4),
    Button(board.GP5),
)

#while True:
#    joystick.update()

while True:
    joystick.update()
    #if the value of the button changes, print the value
    button = joystick.button[0]
    if button.value != joystick._last_report[0]:
        print("Button changed to", button.value)

