"""
The base JoystickXL class for updating input states and sending USB HID reports.

This module provides the necessary functions to create a JoystickXL object,
retrieve its input counts, associate input objects and update its input states.
"""

import struct
import time

# These typing imports help during development in vscode but fail in CircuitPython
try:
    from typing import Tuple, Union
except ImportError:
    pass

from telephony.hid import _get_device
from telephony.inputs import Button


class Joystick:
    """Base JoystickXL class for updating input states and sending USB HID reports."""


    _num_buttons = 0
    """The number of buttons this joystick can support."""

    _report_size = 0
    """The size (in bytes) of USB HID reports for this joystick."""



    @property
    def num_buttons(self) -> int:
        """Return the number of available buttons in the USB HID descriptor."""
        return self._num_buttons


    def __init__(self) -> None:
        """
        Create a JoystickXL object with all inputs in idle states.

        .. code::

           from joystick_xl.joystick import Joystick

           js = Joystick()

        .. note:: A JoystickXL ``usb_hid.Device`` object has to be created in
           ``boot.py`` before creating a ``Joystick()`` object in ``code.py``,
           otherwise an exception will be thrown.
        """
        # load configuration from ``boot_out.txt``
        try:
            with open("/boot_out.txt", "r") as boot_out:
                for line in boot_out.readlines():
                    if "JoystickXL" in line:
                        config = [int(s) for s in line.split() if s.isdigit()]
                        if len(config) < 2:
                            raise (ValueError)
                        Joystick._num_buttons = config[0]
                        Joystick._report_size = config[1]
                        break
            if Joystick._report_size == 0:
                raise (ValueError)
#        except (OSError, ValueError):
#            raise (Exception("Error loading JoystickXL configuration."))
        finally:
            pass

        self._device = _get_device()
        self._report = bytearray(self._report_size)
        self._last_report = bytearray(self._report_size)
        self._format = "<"



        self.button = list()
        """List of button inputs associated with this joystick through ``add_input``."""

        self._button_states = list()
        for _ in range((self.num_buttons // 8) + bool(self.num_buttons % 8)):
            self._button_states.append(0)
            self._format += "B"

        try:
            self.reset_all()
        except OSError:
            time.sleep(1)
            self.reset_all()


    @staticmethod
    def _validate_button_number(button: int) -> bool:
        """
        Ensure the supplied button index is valid.

        :param button: The 0-based index of the button to validate.
        :type button: int
        :raises ValueError: No buttons are configured for the JoystickXL device.
        :raises ValueError: The supplied button index is out of range.
        :return: ``True`` if the supplied button index is valid.
        :rtype: bool
        """
        if Joystick._num_buttons == 0:
            raise ValueError("There are no buttons configured.")
        if not 0 <= button <= Joystick._num_buttons - 1:
            raise ValueError("Specified button is out of range.")
        return True


    def add_input(self, *input: Union[Button]) -> None:
        """
        Associate one or more axis, button or hat inputs with the joystick.

        The provided input(s) are automatically added to the ``axis``, ``button`` and
        ``hat`` lists based on their type.  The order in which inputs are added will
        determine their index/reference number. (i.e., the first button object that is
        added will be ``Joystick.button[0]``.)  Inputs of all types can be added at the
        same time and will be sorted into the correct list.

        :param input: One or more ``Axis``, ``Button`` or ``Hat`` objects.
        :type input: Axis, Button, or Hat
        :raises TypeError: If an object that is not an ``Axis``, ``Button`` or ``Hat``
            is passed in.
        :raises OverflowError: If an attempt is made to add more than the available
            number of axes, buttons or hat switches to the respective list.
        """
        for i in input:
            if isinstance(i, Button):
                if len(self.button) < self._num_buttons:
                    self.button.append(i)
                else:
                    raise OverflowError("List is full, cannot add another button.")
            else:
                raise TypeError("Input must be a Button, Axis or Hat object.")

    def update(self, always: bool = False, halt_on_error: bool = False) -> None:
        """
        Update all inputs in associated input lists and generate a USB HID report.

        :param always: When ``True``, send a report even if it is identical to the last
            report that was sent out.  Defaults to ``False``.
        :type always: bool, optional
        :param halt_on_error: When ``True``, an exception will be raised and the program
            will halt if an ``OSError`` occurs when the report is sent.  When ``False``,
            the report will simply be dropped and no exception will be raised.  Defaults
            to ``False``.
        :type halt_on_error: bool, optional
        """
        # Update axis values but defer USB HID report generation.
    
        # Update button states but defer USB HID report generation.
        if len(self.button):
            button_values = [(i, b.value) for i, b in enumerate(self.button)]
            self.update_button(*button_values, defer=True, skip_validation=True)

        # Update hat switch values, but defer USB HID report generation.
      
        # Generate a USB HID report.
        report_data = list()

      
       
        report_data.extend(self._button_states)

        struct.pack_into(self._format, self._report, 0, *report_data)

        # Send the USB HID report if required.
        if always or self._last_report != self._report:
            try:
                self._device.send_report(self._report)
                self._last_report[:] = self._report
            except OSError:
                # This can occur if the USB is busy, or the host never properly
                # connected to the USB device.  We just drop the update and try later.
                if halt_on_error:
                    raise

    def reset_all(self) -> None:
        """Reset all inputs to their idle states."""
        for i in range(len(self._button_states)):
            self._button_states[i] = 0
        self.update(always=True)



    def update_button(
        self,
        *button: Tuple[int, bool],
        defer: bool = False,
        skip_validation: bool = False,
    ) -> None:
        """
        Update the value of one or more button input(s).

        :param button: One or more tuples containing a button index (0-based) and
           value (``True`` if pressed, ``False`` if released).
        :type button: Tuple[int, bool]
        :param defer: When ``True``, prevents sending a USB HID report upon completion.
           Defaults to ``False``.
        :type defer: bool
        :param skip_validation: When ``True``, bypasses the normal input number/value
           validation that occurs before they get processed.  This is used for *known
           good values* that are generated using the ``Joystick.axis[]``,
           ``Joystick.button[]`` and ``Joystick.hat[]`` lists.  Defaults to ``False``.
        :type skip_validation: bool

        .. code::

           # Update a single button
           update_button((0, True))  # 0 = b1

           # Updates multiple buttons
           update_button((1, False), (7, True))  # 1 = b2, 7 = b8

        .. note::

           ``update_button`` is called automatically for any button objects added to the
           built in ``Joystick.button[]`` list when ``Joystick.update()`` is called.
        """
        for b, value in button:
            if skip_validation or self._validate_button_number(b):
                _bank = b // 8
                _bit = b % 8
                if value:
                    self._button_states[_bank] |= 1 << _bit
                else:
                    self._button_states[_bank] &= ~(1 << _bit)
        if not defer:
            self.update()
  