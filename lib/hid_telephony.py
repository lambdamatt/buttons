import usb_hid

TELEPHONY_REPORT_DESCRIPTOR = bytes((
    0x05, 0x0b,  # USAGE_PAGE (Telephony Devices)
    0x09, 0x05,  # USAGE (Headset)
    0xa1, 0x01,  # COLLECTION (Application)
    0x85, 0x01,  #   REPORT_ID (1)
    0x25, 0x01,  #   LOGICAL_MAXIMUM (1)
    0x15, 0x00,  #   LOGICAL_MINIMUM (0)
    0x09, 0x20,  #   USAGE (Hook Switch)
    0x09, 0x2f,  #   USAGE (Phone Mute)
    0x75, 0x01,  #   REPORT_SIZE (1)
    0x95, 0x02,  #   REPORT_COUNT (2)
    0x81, 0x02,  #   INPUT (Data,Var,Abs)
    0x95, 0x06,  #   REPORT_COUNT (6)
    0x81, 0x03,  #   INPUT (Cnst,Var,Abs)
    0x85, 0x02,  #   REPORT_ID (2)
    0x05, 0x08,  #   USAGE_PAGE (LEDs)
    0x09, 0x09,  #   USAGE (Mute)
    0x09, 0x17,  #   USAGE (Off-Hook)
    0x09, 0x18,  #   USAGE (Ring)
    0x95, 0x03,  #   REPORT_COUNT (3)
    0x91, 0x02,  #   OUTPUT (Data,Var,Abs)
    0x95, 0x05,  #   REPORT_COUNT (5)
    0x91, 0x03,  #   OUTPUT (Cnst,Var,Abs)
    0xc0         # END_COLLECTION
))

telephony = usb_hid.Device(
    report_descriptor=TELEPHONY_REPORT_DESCRIPTOR,
    usage_page=0x0b,        # Telephony
    usage=0x05,             # Headset
    report_ids=(1,),        # Descriptor uses report ID 1
    in_report_lengths=(1,), # This telephony device sends 1 byte in its report
    out_report_lengths=(1,) # It does not receive any reports
)

usb_hid.enable(
    (usb_hid.Device.KEYBOARD,
     usb_hid.Device.MOUSE,
     usb_hid.Device.CONSUMER_CONTROL,
     telephony)
)
