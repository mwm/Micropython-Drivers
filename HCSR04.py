"""Interrupt-driven HC-SR04 driver."""

from pyb import ExtInt, Pin, elapsed_micros, micros, udelay

class HCSR04:
    """Init with pins the trigger and return are tied to.
    
    trigger can be any GPIO pin. Return must be a 5V tolerant GPIO pin
    available for external interrupts. sos is speed of sound per µs in
    the unit of interest, defaulting to cm."""

    def __init__(self, trigger_pin, return_pin, sos=0.034029):
        self.return_pin = return_pin
        trigger_pin.init(mode=Pin.OUT)
        self.trigger_pin = trigger_pin
        self.sos = sos

        self.start_micros = None
        self.elapsed = None
        self.bogus = False
        self.interrupt = ExtInt(return_pin, ExtInt.IRQ_RISING_FALLING,
                                Pin.PULL_DOWN, self.IRQ)

    def trigger(self):
        self.trigger_pin.low()
        udelay(2)
        self.trigger_pin.high()
        udelay(10)
        self.trigger_pin.low()
        self.elapsed = None

    def distance(self, sos=None):
        """Call to get the last distance reading, or 0 if it wasn't valid.
        
        Override the default sos if desired."""

        self.bogus = False
        if not sos:
            sos = self.sos
        if not self.elapsed:
            return 0
        return sos * self.elapsed / 2

    def IRQ(self, pin):
        if self.return_pin.value():
            self.start_micros = micros()
        elif self.start_micros is not None:
            self.elapsed = elapsed_micros(self.start_micros)
        else:
            self.bogus = True
