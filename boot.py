import usb_hid

REPORT_ID = 0x05
JOYSTICK = 0x04
GENERIC_DESKTOP = 0x01

JOYSTICK_REPORT_DESCRIPTOR = bytes((
    0x05, 0x01,                      # UsagePage(Generic Desktop[1])
    0x09, 0x04,                      # UsageId(Joystick[4])
    0xA1, 0x01,                      # Collection(Application)
    0x85, 0x05,                      #     ReportId(5)
    0xA1, 0x02,                      #     Collection(Logical)
    0x05, 0x01,                      #         UsagePage(Generic Desktop[1])
    0x09, 0x30,                      #         UsageId(X[48])
    0x09, 0x31,                      #         UsageId(Y[49])
    0x46, 0xFF, 0x0F,                #         PhysicalMaximum(4,095)
    0x15, 0x00,                      #         LogicalMinimum(0)
    0x26, 0xFF, 0x0F,                #         LogicalMaximum(4,095)
    0x95, 0x02,                      #         ReportCount(2)
    0x75, 0x10,                      #         ReportSize(16)
    0x81, 0x02,                      #         Input(Data, Variable, Absolute, NoWrap, Linear, PreferredState, NoNullPosition, BitField)
    0x05, 0x09,                      #         UsagePage(Button[9])
    0x19, 0x01,                      #         UsageIdMin(Button 1[1])
    0x29, 0x04,                      #         UsageIdMax(Button 4[4])
    0x45, 0x00,                      #         PhysicalMaximum(0)
    0x25, 0x01,                      #         LogicalMaximum(1)
    0x95, 0x04,                      #         ReportCount(4)
    0x75, 0x01,                      #         ReportSize(1)
    0x81, 0x02,                      #         Input(Data, Variable, Absolute, NoWrap, Linear, PreferredState, NoNullPosition, BitField)
    0xC0,                            #     EndCollection()
    0x95, 0x01,                      #     ReportCount(1)
    0x75, 0x04,                      #     ReportSize(4)
    0x81, 0x03,                      #     Input(Constant, Variable, Absolute, NoWrap, Linear, PreferredState, NoNullPosition, BitField)
    0xC0,                            # EndCollection()
))

joystick = usb_hid.Device(
    report_descriptor = JOYSTICK_REPORT_DESCRIPTOR,
    usage_page = GENERIC_DESKTOP,
    usage  = JOYSTICK,
    report_ids=(REPORT_ID,),
    in_report_lengths=(5,),        # This joystick sends 5 bytes (40bits) in its report. Two 16bit axis, four 1bit buttons, 4 padding bits.
    out_report_lengths=(0,),       # It does not receive any reports.
)

usb_hid.enable((joystick,))
