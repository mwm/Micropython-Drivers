"""Keyes Fundumoto Arduino motor/servo/sensor shield."""

# Since an arduino shield, so we use the Arduino Pin labels,

from pyb import Pin
from . hbridge import HBridge
from . servo import Servo


class Fundumoto:
    motors = dict(A=('D12', 'D10'), B=('D11', 'D13'))

    @classmethod
    def motor(cls, name, freq=None, timer=None):
        """Return motor for motor A or motor B, as labelled on shield."""
        return HBridge(HBridge.ONE_SPEED, Pin(cls.motors[name][0]),
                       Pin(cls.motors[name][1]), freq=freq, timer_1=timer)

    @staticmethod
    def buzzer():
        """Get the buzzer pin."""

        return Pin('D4', mode=Pin.OUT)

    @staticmethod
    def servo(timer=None, length=20000):
        """Get the servo connector."""

        return Servo(Pin('D9'), timer, length)
