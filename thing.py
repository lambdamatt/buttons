import board
from telephony.inputs import Button
from telephony.telephony import Telephony
telephony = Telephony()

telephony.add_input(
    Button(board.GP4),
    Button(board.GP5),
)

#while True:
#    telephony.update()

while True:
    telephony.update()
    #if the value of the button changes, print the value
    button = telephony.button[0]
    if button.value != telephony._last_report[0]:
        print("Button changed to", button.value)

