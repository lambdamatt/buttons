"""
Initial USB configuration tools for use in ``boot.py`` setup.

This module provides the necessary functions to create a CircuitPython USB HID device
with a descriptor that includes the configured type and quantity of inputs.
"""

import usb_hid  # type: ignore (this is a CircuitPython built-in)

from telephony import __version__


def create_telephony(
    buttons: int = 16,
    report_id: int = 0x0b,
) -> usb_hid.Device:
    """
    Create the ``usb_hid.Device`` required by ``usb_hid.enable()`` in ``boot.py``.

    .. note::

        ButtonXL will add an entry to the ``boot_out.txt`` file on your ``CIRCUITPY``
        drive.  It is used by the ``Telephony`` module to retrieve configuration
        settings.

    :param axes: The number of axes to support, from 0 to 8.  (Default is 4)
    :type axes: int, optional
    :param buttons: The number of buttons to support, from 0 to 128.  (Default is 16)
    :type buttons: int, optional
    :param hats: The number of hat switches to support, from 0 to 4.  (Default is 1)
    :type hats: int, optional
    :param report_id: The USB HID report ID number to use.  (Default is 4)
    :type report_d: int, optional
    :return: A ``usb_hid.Device`` object with a descriptor identifying it as a telephony
        with the specified number of buttons, axes and hat switches.
    :rtype: ``usb_hid.Device``

    """
    _num_buttons = buttons

    # Validate the number of configured axes, buttons and hats.
    if _num_buttons < 0 or _num_buttons > 128:
        raise ValueError("Button count must be from 0-128.")


    _report_length = 0

    # Formatting is disabled below to allow the USB descriptor elements to be
    # grouped and annotated such that the descriptor is readable and maintainable.

    # fmt: off
    _descriptor = bytearray((
        0x05, 0x0b,                         # : USAGE_PAGE (Generic Desktop)
        0x09, 0x05,                         # : USAGE (Telephony)
        0xA1, 0x01,                         # : COLLECTION (Application)
        0x85, report_id,                    # :   REPORT_ID (Default is 4)
    ))


#    if _num_buttons:
#        _descriptor.extend(bytes((
#            0x05, 0x09,                     # :     USAGE_PAGE (Button)
#            0x19, 0x01,                     # :     USAGE_MINIMUM (Button 1)
#            0x29, _num_buttons,             # :     USAGE_MAXIMUM (num_buttons)
#            0x15, 0x00,                     # :     LOGICAL_MINIMUM (0)
#            0x25, 0x01,                     # :     LOGICAL_MAXIMUM (1)
#            0x95, _num_buttons,             # :     REPORT_COUNT (num_buttons)
#            0x75, 0x01,                     # :     REPORT_SIZE (1)
#            0x81, 0x02,                     # :     INPUT (Data,Var,Abs)
#        )))

    if _num_buttons:
        _descriptor.extend(bytes((
            0x25, 0x01,                     # :     USAGE_PAGE (Button)
            0x15, 0x00,                     # :     USAGE_MINIMUM (Button 1)
            0x09, 0x2f
            ,             # :     USAGE_MAXIMUM (num_buttons)
            0x15, 0x00,                     # :     LOGICAL_MINIMUM (0)
            0x75, 0x01,                     # :     LOGICAL_MAXIMUM (1)
            0x95, 0x01,             # :     REPORT_COUNT (num_buttons)
            0x81, 0x02,                     # :     REPORT_SIZE (1)
            0x95, 0x07,                     # :     INPUT (Data,Var,Abs)
            0x81, 0x03,

        )))


        _button_pad = _num_buttons % 8
        if _button_pad:
            _descriptor.extend(bytes((
                0x75, 0x01,                 # :     REPORT_SIZE (1)
                0x95, 8 - _button_pad,      # :     REPORT_COUNT (_button_pad)
                0x81, 0x03,                 # :     INPUT (Cnst,Var,Abs)
            )))

        _report_length += ((_num_buttons // 8) + bool(_button_pad))

    _descriptor.extend(bytes((
        0xC0,                               # : END_COLLECTION
    )))
    # fmt: on

    # write configuration data to boot.out using 'print'
    print(
        "+ Enabled ButtonXL",
        __version__,
        _num_buttons,
        "buttons",
        _report_length,
        "report bytes.",
    )

    return usb_hid.Device(
        report_descriptor=bytes(_descriptor),
        usage_page=0x0b,  # same as USAGE_PAGE from descriptor above
        usage=0x05,  # same as USAGE from descriptor above
        report_ids=(report_id,),  # report ID defined in descriptor
        in_report_lengths=(_report_length,),  # length of reports to host
        out_report_lengths=(0,),  # length of reports from host
    )


def _get_device() -> usb_hid.Device:
    """Find a ButtonXL device in the list of active USB HID devices."""
    for device in usb_hid.devices:
        if (
            device.usage_page == 0x0b
            and device.usage == 0x05
            and hasattr(device, "send_report")
        ):
            return device
    raise ValueError("Could not find ButtonXL HID device - check boot.py.)")