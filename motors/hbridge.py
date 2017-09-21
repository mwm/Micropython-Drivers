"""HBridge motor controller driver

Provides an interface to a generic h-bridge motor drive."""

from pyb import Pin
from pwm2 import PWM

class HBridge:
    """A generic h-bridge dual motor controller."""

    ONE_SPEED = 0
    RUN_COAST = 1
    RUN_BRAKE = 2

    def __init__(self, mode, in1, in2, freq=None, timer_1=None,
                 freq_2=None, timer_2=None):
        """Specify the run mode and two input pins for the HBridge.

        If mode is ONE_SPEED, then in1 is a digital pin that controls
        direction, and in2 will be used for a PWM speed control, as
        specified by freq and timer_1.  The defaults are 20KHz and the
        default timer for that pin. See pwm2.py for more information.
        
        Otherwise, in1 and in2 are both PWM pins for speed
        control. in1 uses freq and timer_1. as above. in2 uses freq_2
        and timer2, with freq_2 defaulting to freq."""

        self.mode = mode
        if freq is None:
            freq = 20000
        if mode == self.ONE_SPEED:
            self.in1 = in1
            self.in1.init(mode=Pin.OUT)
            self.in2 = PWM(in2, timer=timer_1, freq=freq)
        else:
            self.in1 = PWM(in1, timer=timer_1, freq=freq)
            self.in2 = PWM(in2, timer=timer_2, freq=freq_2 if freq_2 else freq)
        self.go(0)

    def go(self, speed=None):
        """Go at given speed, from 100 (forward) to -100 (reverse).
            
        Call with no arguments to get the last set value."""

        if speed is None:
            return self._speed
        self._speed = speed

        # Shut motors down to avoid jerks
        self.in2.duty(0)
        if self.mode != self.ONE_SPEED:
            self.in1.duty(0)

        forward = speed > 0
        speed = min(abs(speed), 100)
        if self.mode == self.ONE_SPEED:
            self.in1.value(forward)
            self.in2.duty(speed)
        elif self.mode == self.RUN_COAST:
            if forward:
                self.in1.duty(0)
                self.in2.duty(speed)
            else:
                self.in1.duty(speed)
                self.in2.duty(0)
        elif forward:
            self.in1.duty(100 - speed)
            self.in2.duty(100)
        else:
            self.in1.duty(100)
            self.in2.duty(100 - speed)

    def forward(self, speed):
        """Go forward at given speed (from 0 to 100)."""

        self.go(max(speed, 0))

    def reverse(self, speed):
        """Go in reverse at given speed (from 0 to 100)."""
            
        self.go(-max(speed, 0))

    def coast(self):
        """Stop the motors."""
        
        if self.mode == self.ONE_SPEED:
            self.go(0)
        else:
            self._speed = 0
            self.in1.duty(0)
            self.in2.duty(0)

    def brake(self):
        """Apply the motors brakes.
        
        In ONE_SPEED mode, this is the same as coast."""
        
        if self.mode == self.ONE_SPEED:
            self.go(0)
        else:
            self._speed = 0
            self.in1.duty(100)
            self.in2.duty(100)
