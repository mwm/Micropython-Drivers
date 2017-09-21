""" Simple-minded PWM using af_pins from micropython build. """

from pyb import Pin, Timer

from  pins_af import PINS_AF
af_map = dict((x[0], x[1:]) for x in PINS_AF)

class PwmError(Exception):
    pass
    
class PWM:
    """A PWM output on the given pin.
    
    This uses the pins_af.py file created by the micropython build.

    The timer argument is the name of the timer to use, as a string in
    the form 'TIM#'.  If it is not set, the first timer available for
    the pin will be used. Either length or freq can be used to specify
    the pulse length of the pwm signal. Length is the total pulse
    length in microseconds, and frequency is Hz, so length=20000
    implies freq=50, which is the default. If both are specified, freq
    is ignored.

    self.timer & self.channel are made available if you want to read or
    adjust the settings after initialization."""

    def __init__(self, pin, timer=None, length=None, freq=None):
        timers = af_map['P' + pin.name()]
        if not timers:
            raise PwmError("Pin does not support PWM.")

        if not timer:
            timer = 'TIM'
        for af, name in timers:
            if name.startswith(timer):
                timer_af, timer_name = af, name
                timer_full, channel = timer_name.split('_')
                if channel.startswith('CH'):
                    break
        else:
            raise PwmError("Pin does not support timer %s" % timer)
        
        if length:
            freq = 1000000 / length
        elif not freq:
            freq = 50
        pin.init(Pin.OUT, alt=af)
        self.timer = Timer(int(timer_full[3:]), freq=freq)
        self.channel = self.timer.channel(int(channel[2:3]), 
                    Timer.PWM_INVERTED if channel.endswith('N') else Timer.PWM,
                    pin=pin)

        self.length = 1000000 / self.timer.freq()
        self.duty(0)

    def duty(self, percentage=None):
        """Get/Set the duty cycle as a percentage.
        
        The duty cycle is the time the output signal is on.
        Returns the last set value if called with no arguments."""

        if percentage is None:
            return round(100 * self.channel.pulse_width() / self.timer.period())
        self.channel.pulse_width_percent(max(0, min(percentage, 100)))

    def pulse_width(self, width=None, time=0):
        """Get/Set the pulse width in microseconds.
        
        The width is the length of time the signal is on.  Returns the
        current value rounded to the nearest int if called with no
        arguments.
        
        Time is the number of milliseconds to take to get to the new
        width.  At least that many milliseconds will pass; if it's 0,
        the change will happen now."""

        if width is None:
            return round(self.length * self.channel.pulse_width() /
                         self.timer.period())
        target = self.timer.period() * min(width, self.length) / self.length
        self.target = round(target)
        if time == 0:
            self.channel.pulse_width(self.target)
        else:
            self.delta = int((target - self.channel.pulse_width()) * self.length
                             / (time * 1000))
            self.channel.callback(self.timed_change)
            # No initial change so we get minimum length.

    def timed_change(self, timer):
        """Make a timed change in width."""

        old = self.channel.pulse_width()
        if abs(old - self.target) > abs(self.delta):
            self.channel.pulse_width(old + self.delta)
        else:
            self.channel.callback(None)
            self.channel.pulse_width(self.target)
            
            
        
