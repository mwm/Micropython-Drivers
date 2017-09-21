"""DRV8835 motor controller drivers"""

from pyb import Pin

from . hbridge import HBridge

class DRV8835:
    """Control software for a DRV8835 motor driver chip.

    Initialize a DRV8835 chip in mode. If the DRV8835's mode pin isn't
    wired to the state for mode, then it should be connected to the
    given pin."""

    PHASE_ENABLE = 1
    IN_IN = 0

    def __init__(self, mode, pin=None):
        """Init the DRV8835 to use PHASE_ENABLE or IN_IN mode.

        If provided, pin is a pyb.Pin object for the DRV8835 mode
        input. If that is wired to the proper state, this doesn't need
        to be set. If it's provided, it will be set for mode."""

        self._mode = mode

	# Enable the proper mode.
        if pin:
            pin.init(Pin.OUT)
            pin.value(mode)

    def motor(self, in1, in2, coast=False, timer=None, freq=None,
              timer_2=None, freq_2=None):
        """Returns a driver for one of the motors attached to the chip.
        
        Use the in1 & in2 pins to control the motor using this chip's
        mode. In PHASE_ENABLE mode, in1 is a digital pin used for
        phase (direction) control, and in2 is a PWM pin for speed
        control. In IN_IN mode, both pins are used for PWM out. The
        timer and freq parameters will be used for in1, with timer2
        and freq2 used for in2.
        
        If the chip is used in IN_IN mode, the it can allow the motors
        to coast, and has an mode for both forward and reverse, where
        the motors coast instead of braking during the off part of the
        pwm speed signal. Set coast to true to use this for forward
        and reverse instead of the default braking behavior.

        If timer is set but not timer2, then timer will be used for
        timer2. freq and freq2 are treated the same. If a timer is not
        set, the first timer on the pin will be used. If freq is not
        set, it will default to 20000."""

        if self._mode == DRV8835.PHASE_ENABLE:
            mode = HBridge.ONE_SPEED
        elif coast:
            mode = HBridge.RUN_COAST
        else:
            mode = HBridge.RUN_BRAKE

        return HBridge(mode, in1, in2, freq=freq, timer_1=timer,
                       freq_2=freq_2, timer_2=timer_2)


class PololuShield(DRV8835):
    def __init__(self, mode):
        self._mode = mode

    motors = {1: ('D7', 'D9'), 2: ('D8', 'D10')}

    def motor(self, motor, coast=False, timer=None, freq=None,
              timer_2=None, freq_2=None):
        """Return motor 1 or motor 2, as labelled on shield."""

        return DRV8835.motor(self, Pin(self.motors[motor][0]),
                             Pin(self.motors[motor][1]),
                             coast=coast, timer=timer, freq=freq,
                             timer_2=timer_2, freq_2=freq_2)
