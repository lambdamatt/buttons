"""ButtonXL standard boot.py."""

import usb_hid  # type: ignore (this is a CircuitPython built-in)
from telephony.hid import create_telephony

# This will enable a telephony USB HID device.  All other standard CircuitPython USB HID
# devices (keyboard, mouse, consumer control) will be disabled.
usb_hid.enable((create_telephony(buttons=2),))