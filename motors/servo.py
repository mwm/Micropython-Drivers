"""A Python version of the pyboard's "Servo" class.

Where the PyBoard version uses specific ports, this takes a Pin to
output the PWM signal to. It used the pwm2 library to set up
pwm. Since that libraries pulse width routines work in microseconds,
not "raw" pulse widths (timer internal counter values), the
pulse_width routine uses microseconds instead of those raw values.

Besides a Pin, the user can specify a timer to use a different alt
function of the pin instead of the default one, and the length of the
PWM signal in µ-seconds. This defaults to 20000.

Finally, the default values for the pulse min, max and centre are the
industry expected values rather than the values for the Servos
commonly used with the Pyboard. There is no real industry standard,
and most servos will vary from these values, so you need to calibrate
your servos in any case."""

from pwm2 import PWM

class Servo:
    def __init__(self, pin, timer=None, length=20000):
        """Init PWM signal on pin
        
         Optionally specify timer (see pwm2.py for details), and the
         PWM pulse length in microseconds."""

        self.pwm = PWM(pin, timer, length=length)
        self.pulse_min = round(length * .05)
        self.pulse_max = round(length * .1)
        self.pulse_centre = round(length * .075)
        self.pulse_angle_90 = self.pulse_speed_100 = self.pulse_max

        self.angle(0)

    def calibration(self, pulse_min, pulse_max, pulse_centre,
                    pulse_angle_90=None, pulse_speed_100=None):
        """Set calibration values for the servo. 
        
        Set the minimum and maximum pulse values allowed, the value
        to go to for angle/speed 0 (pulse_centre), and the pulse widht in
        microseconds for angle 90/speed 100.
        
        Rather than make all these values optional, the servo object exposes
        the calibration values to be read."""
        
        self.pulse_min = pulse_min
        self.pulse_max = pulse_max
        self.pulse_centre = pulse_centre
        if pulse_angle_90 is not None:
            self.pulse_angle_90 = pulse_angle_90
        if pulse_speed_100 is not None:
            self.pulse_speed_100 = pulse_speed_100

    def angle(self, angle=None, time=0):
        """Get/set the current angle.
        
        Output rounded to the nearest integer."""

        if angle is None:
            return round(90 * (self.pulse_width() - self.pulse_centre)
                         / self.pulse_angle_90)
        width = self.pulse_centre + self.pulse_angle_90 * angle / 90
        self.pulse_width(width, time=time)
    
    def speed(self, speed=None, time=0):
        """Get/set the current speed.
        
        Output rounded to the nearest integer."""

        if speed is None:
            return round(100 * (self.pulse_width() - self.pulse_centre)
                         / self.pulse_speed_100)
        width = self.pulse_centre + self.pulse_speed_100 * speed / 100
        self.pulse_width(width, time=time)
    
    def pulse_width(self, width=None, time=0):
        """Get/set the current pulse width in microseconds.
        
        This returns the pwm2 PWM class pulse_width."""

        if width is None:
            return self.pwm.pulse_width()
        self.pwm.pulse_width(min(max(width, self.pulse_min), self.pulse_max),
                             time)
