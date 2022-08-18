import struct
import time
import board
import busio
from adafruit_hid import find_device
import usb_hid
import adafruit_bus_device.i2c_device as i2c_device
import AS5600

JOYSTICK = 0x04
GENERIC_DESKTOP = 0x01
REPORT_SIZE = 5

class Joystick:
    def __init__(self, devices):
        self._previous_report = bytearray(REPORT_SIZE)
        self._device = find_device(devices, usage_page=GENERIC_DESKTOP, usage=JOYSTICK)

    def update(self, x = 0, y = 0, buttons = 0 ):
        report = bytearray(REPORT_SIZE)
        struct.pack_into('<HHB', report, 0, x, y, buttons)
        if report != self._previous_report:
            self._previous_report = report
            self._device.send_report(report)


joystick = Joystick(usb_hid.devices)

# Create I2C bus.
i2c = busio.I2C (scl=board.CC_SCL, sda=board.CC_SDA)

# Create Magnetic Rotation Sensor.
angleSensor = AS5600.AS5600(i2c)

print(angleSensor.status)
print("MagnetDetected: ", angleSensor.is_magnet_detected)
print("Too Strong: ", angleSensor.is_magnet_too_strong)
print("Too Weak: ", angleSensor.is_magnet_too_weak)

raw = angleSensor.raw_angle
angle = angleSensor.angle
print ("raw /angle: ", raw, angle)

print ("zpos: ", angleSensor.zero_position)
print ("mpos: ", angleSensor.max_position)
print ("mang: ", angleSensor.max_angle)

zpos = angleSensor.zero_position = raw
mpos = angleSensor.max_position = raw +256
print ("zpos: ", angleSensor.zero_position)
print ("mpos: ", angleSensor.max_position)
print ("mang: ", angleSensor.max_angle)

print ("raw /angle: ", angleSensor.raw_angle, angleSensor.angle)

print ("zmco: ", angleSensor.zmco)
print ("status: {:08b}".format(angleSensor.status))
print ("agc: ", angleSensor.gain)

hyst = angleSensor.hysteresis = AS5600.HYSTERESIS_3LSB
print ("Hyst: ", hyst)

time.sleep(5)
while True:
    raw = angleSensor.raw_angle
    angle = angleSensor.angle
    print ("raw / angle: ", raw, angle)  
    joystick.update(angle, 0, 0)
    time.sleep(0.1)

'''
# while True:
    for n in range(0, 4095, 10):
        if b == 0: b = 0b10000
        b = b >> 1
        joystick.update(n, n, b)
        time.sleep(0.2)

    for n in range(4095, 0, -10):
        if b == 0:
            b = 0b10000
        b = b >> 1
        joystick.update(n, n, b)
        time.sleep(0.2)
'''
