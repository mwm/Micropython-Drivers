"""Drivers for various motor controll systems.

These normally have three layers:

Motors, which we don't usually talk to directly.

A motor controller. This could be something like an h-bridge or servo,
usually with some extra circuitry to make them easier to use. See
hbridge.md for more information on those.

A board for the controller. This almost always does power management,
may select the mode for the controller, and if designed for a specific
µ-controller board may determine what pins are used."""

# Keys Fundumoto Arduino shield. An L298 with two h-bridges (motor_a and motor_b)
# in ONE_SPEED mode, and a buzzer wired to specific arduino pins.
from . import fundumoto

# DRV8835 h-bridge chip drivers. Two h-bridges that can be used in ONE_SPEED
# mode (though it's run/brake instead of run/coast) or controlled directly, but
# both must be the same. Also available on an Arduino shield.
from .  drv8835 import DRV8835
