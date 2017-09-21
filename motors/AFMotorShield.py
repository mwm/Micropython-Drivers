"""Driver for the Adafruit Motor/Stepper/Servo shield, V1 controller shield.

THIS SHIELD WILL NOT WORK WITH 3-Volt logic systems.

Hence, not properly tested."""

# Note that it's an arduino shield, so we use the Arduino Pin labels,
# in the hope they'll work for micropython on any board with Arudino
# headers.

# TBD: Implement this.
# Function		Arduino		NucleoF401RE
# -------------------------------------------------
# Servo #1		D9		PC7		
# Servo #2		D10		PB6

from pyb import Pin
from pwm2 import PWM
import stm

class MotorError(Exception):
    pass

class AFMotorShieldV1:
    """Driver for the AdaFruit Motor/Stepper/Shield"""
    
    This uses L293D drivers, but the control pins are tied to an 8 bit
    shift register, not the L293D. So in order to set the mode on the
    L293D, you HAVE to use the AFMotorShieldV1 to set mode. The
    PMW pins used to control speed are connected to the L239D so
    you can use them directly.

    Yeah, the docs say version 1 is ancient and obsolete, but I have
    one, so..."""

    motors = 4 * [None]

    # Each tuple is A, B bitmasks for the latch and pin for PWM speed control
    motor_bits = [(1 << 2, 1 << 3, 'D12'),
                  (1 << 1, 1 << 4, 'D3'),
                  (1 << 5, 1 << 7, 'D5'),
                  (1 << 0, 1 << 6, 'D6')]

    latch_pin = Pin('D12', Pin.OUT)
    clk_pin = Pin('D4', Pin.OUT)
    en_pin = Pin('D7', Pin.OUT)
    data_pin = Pin('D8', Pin.OUT)

    def __init__(self):
        """Create my instance variables."""

        self.latch_pin = Pin('D12', Pin.OUT)
        self.clock_pin = Pin('D4', Pin.OUT)
        self.data_pin = Pin('D8', Pin.OUT)
        self.en_pin = Pin('D7', Pin.OUT)

        self.latch_value = 0
        self.update_latch()
        self.en_pin.off()

    def motor(self,  motor, reversed=False):
        """Init motor # motor. Optionally treat it as reversed.
        
        Motor numbers from 1 to 4, as labelled on the board.
        Use reverse for one of a left/right pair of motors."""

        if 1 <= motor <= 4:
            motor -= 1
            self.motors[motor] = _L293D(self, *self.motor_bits[motor],
                                        reversed=reversed)
        else:
            raise MotorError("Motors are 1, 2, 3 and 4")

    def motor_list(self, motor):
        if motor is None:
            return [m for m in self.motors if m is not None]
        elif 1 <= motor <= 4 and self.motors[motor - 1] is not None:
            return self.motors[motor - 1]
        else:
            raise MotorError("Motor %d isn't attached" % motor)

    def update_latch(self):
        """Let the L293 chips know what we want."""

        self.latch_pin.off()
        self.data_pin.off()
        for bit in range(7, -1, -1):
            self.clock_pin.off()
            if self.latch_value & (1 << bit):
                self.data_pin.on()
            else:
                self.data_pin.off()
            self.clock_pin.on()
        self.latch_pin.on()

    def go(self, speed, motor=None):
        """Run the indicated motor at the given speed.
        
        Speed is from 100 (forward) to -100 (reverse).  If you don't
        provide a motor number, applies to all attached motors."""

        self.en_pin.off()
        motors = self.motor_list(motor)
        forward = speed > 0
        for motor in motors:
            if forward:
                motor.forward()
            else:
                motor.reverse()
            motor.go(0)

        self.update_latch()

        speed = abs(speed)
        for motor in motors:
            motor.go(speed)

        self.en_pin.on()
            
    def forward(self, speed, motor=None):
        """Go forward at given speed (from 0 to 100)."""

        self.go(max(speed, 0), motor)

    def reverse(self, speed, motor=None):
        """Go in reverse at given speed (from 0 to 100)."""
            
        self.go(-max(speed, 0), motor)

    def coast(self, motor=None):
        """Stop the motors."""
        
        self.go(0, motor)

    def brake(self, motor=None):
        """Apply the brakes."""

        for motor in self.motor_list(motor):
            motor.brake()
        self.update_latch()


class _L293D:
    """An L293D motor driver for the AFMotorShieldV1 driver.

    These shouldn't be used directly - use the
    go/forward/reverse/stop/brake methods of the AFMotorShieldV1 class
    instead.

    If you MUST have a simple API for a single motor, use
    AFMotorWrapper."""

    # Note that the arguments after parent match the
    # AFMotorShieldV1.motor_bits tuple order
    def __init__(self, parent, a, b, pwm, reversed=False):
        self.parent, self.a, self.b = parent, a, b
        self.pwm = PWM(Pin(pwm), freq=2000)

        # _forward indicates the direction we want to go
        # _reversed means our directions are reversed.
        self._forward = True
        self._reversed = reversed

        # And make sure we're stopped
        self.brake()

    def go(self, speed=None):
        """Turn at given speed, from 0 to 100.

        Return current speed if speed is None"""

        if speed is None:
            return speed if self._forward and not self._reversed else -speed
        else:
            self.pwm.duty(speed)

    def forward(self):
        """Set the latch bits so I go forward."""

        self._forward = True
        self.parent.latch_value |= self.a
        self.parent.latch_value &= self.b

    def reverse(self):
        """Set the latch bits so I go in reverse."""
            
        self._forward = False
        self.parent.latch_value &= ~self.a
        self.parent.latch_value |= self.b

    def brake(self, latch=True):
        """Hit the brakes."""

        self.go(0)	# Coast until we update the latch.
        self.parent.latch_value &= ~(self.a | self.b)


gpio_size = stm.GPIOB - stm.GPIOA
def make_gpio(pin):
    """Given a pin, return a pair of ODR & mask for it."""

    return stm.GPIOA + gpio_size * pin.port() + stm.GPIO_ODR, 1 << pin.pin()
