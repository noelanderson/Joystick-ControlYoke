# SPDX-FileCopyrightText: Copyright (c) 2022 Noel Anderson
#
# SPDX-License-Identifier: MIT

"""
`AS5600`
================================================================================
CircuitPython library for connecting an AMS AS5600 12-bit on-axis magnetic rotary position sensor 
* Author(s): Noel Anderson

Implementation Notes
--------------------
**Hardware:**

* `AS5600 <https://ams.com/as5600>`

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards: https://github.com/adafruit/circuitpython/releases
* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
"""

from micropython import const
import adafruit_bus_device.i2c_device as i2c_device

# Register Map

_AS5600_DEFAULT_I2C_ADDR = const(0x36)
_AS5600_REG_ZMCO = const(0x00)          # R
_AS5600_REG_ZPOS_HI = const(0x01)       # R/W/P
_AS5600_REG_ZPOS_LO = const(0x02)       # R/W/P
_AS5600_REG_MPOS_HI = const(0x03)       # R/W/P
_AS5600_REG_MPOS_LO = const(0x04)       # R/W/P
_AS5600_REG_MANG_HI = const(0x05)       # R/W/P
_AS5600_REG_MANG_LO = const(0x06)       # R/W/P
_AS5600_REG_CONF_HI = const(0x07)       # R/W/P
_AS5600_REG_CONF_LO = const(0x08)       # R/W/P
_AS5600_REG_RAW_ANGLE_HI = const(0x0C)  # R
_AS5600_REG_RAW_ANGLE_LO = const(0x0D)  # R
_AS5600_REG_ANGLE_HI = const(0x0E)      # R
_AS5600_REG_ANGLE_LO = const(0x0F)      # R
_AS5600_REG_STATUS = const(0x0B)        # R
_AS5600_REG_AGC = const(0x1A)           # R
_AS5600_REG_MAGNITUDE_HI = const(0x1B)  # R
_AS5600_REG_MAGNITUDE_LO = const(0x1C)  # R
_AS5600_REG_BURN = const(0xFF)          # W

# Commands

_BURN_ANGLE_COMMAND = const(0x80)
_BURN_SETTINGS_COMMAND = const(0x40)

# Bit maps and offsets for status & config regiters

_STATUS_MH = const(0b00001000)
_STATUS_ML = const(0b00010000)
_STATUS_MD = const(0b00100000)
_STATUS_MASK = const(0b00111000)

_ONE_BIT_MASK = const(0b00000001)
_TWO_BIT_MASK = const(0b00000011)
_THREE_BIT_MASK = const(0b00000111)
_POWER_MODE_OFFSET = const(0)
_HYSTERESIS_OFFSET = const(2)
_OUTPUT_STAGE_OFFSET = const(4)
_PWM_FREQUENCY_OFFSET = const(6)
_SLOW_FILTER_OFFSET = const(0)
_FAST_FILTER_OFFSET = const(2)
_WATCH_DOG_OFFSET = const(5)

# User-facing constants:

POWER_MODE_NOM = const(0)
POWER_MODE_LPM1 = const(1)
POWER_MODE_LPM2 = const(2)
POWER_MODE_LPM3 = const(3)

HYSTERESIS_OFF = const(0)
HYSTERESIS_1LSB = const(1)
HYSTERESIS_2LSB = const(2)
HYSTERESIS_3LSB = const(3)

OUTPUT_STAGE_ANALOG_FULL = const(0)
OUTPUT_STAGE_ANALOG_REDUCED = const(1)
OUTPUT_STAGE_DIGITAL_PWM = const(2)

PWM_FREQUENCY_115HZ = const(0)
PWM_FREQUENCY_230HZ = const(1)
PWM_FREQUENCY_460HZ = const(2)
PWM_FREQUENCY_920HZ = const(3)

SLOW_FILTER_16X = const(0)
SLOW_FILTER_8X = const(1)
SLOW_FILTER_4X = const(2)
SLOW_FILTER_2X = const(3)

FAST_FILTER_THRESHOLD_SLOW = const(0)
FAST_FILTER_THRESHOLD_6LSB = const(1)
FAST_FILTER_THRESHOLD_7LSB = const(2)
FAST_FILTER_THRESHOLD_9LSB = const(3)
FAST_FILTER_THRESHOLD_18LSB = const(4)
FAST_FILTER_THRESHOLD_21LSB = const(5)
FAST_FILTER_THRESHOLD_24LSB = const(6)
FAST_FILTER_THRESHOLD_10LSB = const(7)


class AS5600:

    def __init__(self, i2c, address=_AS5600_DEFAULT_I2C_ADDR):
        self._device = i2c_device.I2CDevice(i2c, address)

    # Output Registers

    @property
    def angle(self):
        """Get the current 12-bit angle (ANGLE)."""
        return self._read_16(_AS5600_REG_ANGLE_HI)

    @property
    def raw_angle(self):
        """Get the current unscaled and unmodified 12-bit angle (RAWANGLE)."""
        return self._read_16(_AS5600_REG_RAW_ANGLE_HI)

    # Status Registers

    @property
    def status(self) -> int:
        """Get the 8-bit status register (STATUS)."""
        return self._read_8(_AS5600_REG_STATUS) & _STATUS_MASK

    @property
    def is_magnet_too_strong(self) -> bool:
        """ Test MH Status Bit"""
        return bool(self.status & _STATUS_MH)

    @property
    def is_magnet_too_weak(self) -> bool:
        """ Test ML Status Bit"""
        return bool(self.status & _STATUS_ML)

    @property
    def is_magnet_detected(self) -> bool:
        """ Test MD Status Bit"""
        return bool(self.status & _STATUS_MD)

    @property
    def gain(self) -> int:
        """Get the 8-bit Automatic Gain Control value (AGC)."""
        return self._read_8(_AS5600_REG_AGC)

    @property
    def magnitude(self) -> int:
        """Get the 12-bit CORDIC magnitude (MAGNITUDE)."""
        return self._read_16(_AS5600_REG_MAGNITUDE_HI)

    # Configuration Registers

    @property
    def zmco(self) -> int:
        """Get the 8-bit burn count (ZMCO)."""
        return self._read_8(_AS5600_REG_ZMCO)

    @property
    def zero_position(self) -> int:
        """Get and set the 12-bit zero position (ZPOS)."""
        return self._read_16(_AS5600_REG_ZPOS_HI)

    @zero_position.setter
    def zero_position(self, value: int) -> int:
        if not 0 <= value <= 4095:
            raise ValueError("Value must be between 0 & 4095")
        return self._write_16(_AS5600_REG_ZPOS_HI, value)

    @property
    def max_position(self) -> int:
        """Get and set the 12-bit maximum position (MPOS)."""
        return self._read_16(_AS5600_REG_MPOS_HI)

    @max_position.setter
    def max_position(self, value: int) -> int:
        if not 0 <= value <= 4095:
            raise ValueError("Value must be between 0 & 4095")
        return self._write_16(_AS5600_REG_MPOS_HI, value)

    @property
    def max_angle(self) -> int:
        """Get and set the 12-bit maximum angle (MANG)."""
        return self._read_16(_AS5600_REG_MANG_HI)

    @max_angle.setter
    def max_angle(self, value: int) -> int:
        if not 0 <= value <= 4095:
            raise ValueError("Value must be between 0 & 4095")
        return self._write_16(_AS5600_REG_MANG_HI, value)

    @property
    def power_mode(self) -> int:
        """Get and set the Power Mode (PM) configuration."""
        return self._read_conf_register(_AS5600_REG_CONF_LO, _TWO_BIT_MASK, _POWER_MODE_OFFSET)

    @power_mode.setter
    def power_mode(self, value: int) -> int:
        if not POWER_MODE_NOM <= value <= POWER_MODE_LPM3:
            raise ValueError("Power Mode (PM) value must be between {:d} & {:d}".format(POWER_MODE_NOM, POWER_MODE_LPM3))
        return self._write_conf_register(_AS5600_REG_CONF_LO, _TWO_BIT_MASK, _POWER_MODE_OFFSET, value)

    @property
    def hysteresis(self) -> int:
        """Get and set the Hysteresis (HYST) configuration."""
        return self._read_conf_register(_AS5600_REG_CONF_LO, _TWO_BIT_MASK, _HYSTERESIS_OFFSET)

    @hysteresis.setter
    def hysteresis(self, value: int) -> int:
        if not HYSTERESIS_OFF <= value <= HYSTERESIS_3LSB:
            raise ValueError("Hysteresis (HYST) value must be between {:d} & {:d}".format(HYSTERESIS_OFF, HYSTERESIS_3LSB))
        return self._write_conf_register(_AS5600_REG_CONF_LO, _TWO_BIT_MASK, _HYSTERESIS_OFFSET, value)

    @property
    def output_stage(self) -> int:
        """Get and set the Output Stage (OUTS) configuration."""
        return self._read_conf_register(_AS5600_REG_CONF_LO, _TWO_BIT_MASK, _OUTPUT_STAGE_OFFSET)

    @output_stage.setter
    def output_stage(self, value: int) -> int:
        if not OUTPUT_STAGE_ANALOG_FULL <= value <= OUTPUT_STAGE_DIGITAL_PWM:
            raise ValueError("Output Stage (OUTS) value must be between{:d} & {:d}".format(OUTPUT_STAGE_ANALOG_FULL, OUTPUT_STAGE_DIGITAL_PWM))
        return self._write_conf_register(_AS5600_REG_CONF_LO, _TWO_BIT_MASK, _OUTPUT_STAGE_OFFSET, value)

    @property
    def pwm_frequency(self) -> int:
        """Get and set the PWM Frequency (PWMF) configuration."""
        return self._read_conf_register(_AS5600_REG_CONF_LO, _TWO_BIT_MASK, _PWM_FREQUENCY_OFFSET)

    @pwm_frequency.setter
    def pwm_frequency(self, value: int) -> int:
        if not PWM_FREQUENCY_115HZ <= value <= PWM_FREQUENCY_920HZ:
            raise ValueError("PWM Frequency (PWMF) value must be between {:d} & {:d}".format(PWM_FREQUENCY_115HZ, PWM_FREQUENCY_920HZ))
        return self._write_conf_register(_AS5600_REG_CONF_LO, _TWO_BIT_MASK, _PWM_FREQUENCY_OFFSET, value)

    @property
    def slow_filter(self) -> int:
        """Get and set the Slow Filter (SF) configuration."""
        return self._read_conf_register(_AS5600_REG_CONF_HI, _TWO_BIT_MASK, _SLOW_FILTER_OFFSET)

    @slow_filter.setter
    def slow_filter(self, value: int) -> int:
        if not SLOW_FILTER_16X <= value <= SLOW_FILTER_2X:
            raise ValueError("Slow  Filter (SF) value must be between {:d} & {:d}".format(SLOW_FILTER_16X, SLOW_FILTER_2X))
        return self._write_conf_register(_AS5600_REG_CONF_HI, _TWO_BIT_MASK, _SLOW_FILTER_OFFSET, value)

    @property
    def fast_filter(self) -> int:
        """Get and set the Fast Filter Threshold (FTH) configuration."""
        return self._read_conf_register(_AS5600_REG_CONF_HI, _THREE_BIT_MASK, _FAST_FILTER_OFFSET)

    @fast_filter.setter
    def fast_filter(self, value: int) -> int:
        if not FAST_FILTER_THRESHOLD_SLOW <= value <= FAST_FILTER_THRESHOLD_10LSB:
            raise ValueError("Fast  Filter (FTH) value must be between {:d} & {:d}".format(FAST_FILTER_THRESHOLD_SLOW, FAST_FILTER_THRESHOLD_10LSB))
        return self._write_conf_register(_AS5600_REG_CONF_HI, _THREE_BIT_MASK, _FAST_FILTER_OFFSET, value)

    @property
    def watch_dog(self) -> int:
        """Get and set the Watchdog (WD) configuration."""
        return self._read_conf_register(_AS5600_REG_CONF_HI, _ONE_BIT_MASK, _WATCH_DOG_OFFSET)

    @watch_dog.setter
    def watch_dog(self, value: int) -> int:
        if not 0 <= value <= 1:
            raise ValueError("Watchdog (WD) value must be 0 or 1")
        return self._write_conf_register(_AS5600_REG_CONF_HI, _ONE_BIT_MASK, _WATCH_DOG_OFFSET, value)

    # Burn Commands

    def burn_in_angle(self):
        """Perform a permanent writing of ZPOS and MPOS to non-volatile memory"""
        self._write_8(_AS5600_REG_BURN, _BURN_ANGLE_COMMAND)

    def burn_in_settings(self):
        """Perform a permanent writing of MANG and CONFIG to non-volatile memory"""
        self._write_8(_AS5600_REG_BURN, _BURN_SETTINGS_COMMAND)

    # Internal Class Functions

    def _read_8(self, address: int) -> int:
        # Read and return a byte from the specified 8-bit register address.
        result = bytearray(1)
        with self._device as i2c:
            i2c.write(bytes([address]))
            i2c.readinto(result)
        return result[0]

    def _write_8(self, address: int, value: int) -> int:
        # write a byte to the specified 8-bit register address.
        result = bytearray(1)
        with self._device as i2c:
            i2c.write(bytes([address, value]))
            i2c.write(bytes([address]))
            i2c.readinto(result)
        return result[0]

    def _read_16(self, address: int) -> int:
        # Read and return a 16-bit unsigned big endian value read from the specified 16-bit register address.
        result = bytearray(2)
        with self._device as i2c:
            i2c.write(bytes([address]))
            i2c.readinto(result)
        return (result[0] << 8) | result[1]

    def _write_16(self, address: int, value: int) -> int:
        # Write a 16-bit big endian value to the specified 16-bit register address.
        result = bytearray(2)
        with self._device as i2c:
            i2c.write(bytes([address, (value & 0xFF00) >> 8, value & 0x00FF]))
            i2c.write(bytes([address]))
            i2c.readinto(result)
        return (result[0] << 8) | result[1]

    def _read_conf_register(self, register: int, mask: int, offset: int) -> int:
        # Read configuration register bits
        mask = mask << offset
        result = self._read_8(register)
        return (result & mask) >> offset

    def _write_conf_register(self, register: int, mask: int, offset: int, value: int) -> int:
        # Write configuration register bits
        mask = mask << offset
        inverse_mask = ~mask & 0xFF
        current_value = self._read_8(register)
        value = (current_value & inverse_mask) | (value << offset)
        result = self._write_8(register, value)
        return (result & mask) >> offset
