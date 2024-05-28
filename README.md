## BUTTONS
#### This project is the starting point for making USB HID buttons with circuitpython, beyond the easy stuff. The use cases are specific and personal.

---
##### NOTE:
###### there is a branch called `fixitup` that I am using to rename things so they don't reference joystick things. Once I am happy with that I will merge it into main. Also, if you make big changes to the codebase, you will need to delete the `boot_out.txt` file from the root of the `CIRCUITPYTHON` volume, as it caches information about the board and the code. this is created in `hid.py` and called in `joystick.py`

----
This first commit aims to make a button that acts as a Call Control device for Google Meet
The code is ripped off from the incredible [JoystickXL Project](https://github.com/fasteddy516/CircuitPython_JoystickXL) because it was the most complete and thought out project I could find that extends the CircutPython usb_hid device reports. It does it with the `Generic Desktop` usage_page and the `Joystick` usage, but we need to use the `Telephony` usage page and the `headset` usage.

Currently Mute is implemented but there is cruft all over the place and most of the classes and variables are still using joystick and gamepad nameing conventions. 

---

TODO:
- [x] make mute work
- [x] instantiate a public repo
- [ ] refactor, clean up and streamline
- [ ] add additional functionality like `hang up` and `mute status led`

---

#### I am standing on the shoulders of giants, namely:

- The whole [Adafruit/CircuitPython team and community](https://circuitpython.org/)
- [JoystickXL](https://github.com/fasteddy516/CircuitPython_JoystickXL/blob/main/joystick_xl/hid.py)
- [imrehg](https://github.com/imrehg/arduino-usb-phone-hid)

and they have my gratitude.

---

#### This codebase is extremely unstable, and if I stick with it, will change constantly.

Helpful tools:

IDE: [Thonny](https://thonny.org/)

HID I/O debugging: [hidviz](https://github.com/hidviz/hidviz) 

https://docs.kernel.org/hid/hidintro.html


#### A couple of notes:
`boot.py` is a blessed filename that runs very early in the boot process. This is used to do lower level things like setting the USB modes etc. 
our `boot.py` gets all of the things in place to have this run as a USB HID with the correct report descriptor for telephony
`thing.py` is a development kludge. Typically, the auto-executing script would go in a blessed file calle `code.py` (`main.py` also works) but I don't want the script to auto-exec because REPL. There is probably a better/more correct way to do this but this is what is working for me

REF: [circuitpythondocs](https://docs.circuitpython.org/en/latest/README.html#behavior)
