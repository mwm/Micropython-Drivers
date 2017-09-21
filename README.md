Drivers for the various devices in my ongoing robotics work.

# PWM
The pwm2 file uses the pins_af.py file built for each board to
automatically select and configure timer for the given pin. It allows
you to pick alternative timers if the pin uses them and specify the
pulse length in microseconds.

You can get and set the pulse width in microseconds as well as duty
cycle. Changes to the pulse width can be made to occure over a period
of time.

# HCSR04
Driver for an HCSR04 ultrasonic rangefinder.

This interrupt-driven driver allows concurrent operations while
ranging.  It should be timed out, though, as the device will return
garbage if the maximum distance is exceeded.

# Motors
A collection of motor drivers.

## Layers
Motor drivers have three layers.

### Circuits
This is the physical circuit used. It determines the types of motors
controlled and how to do so.

### Implementation
A chip or breakout that implements a specific circuit, usually with
some support hardware for specific behavior, possibly tweaking the
behavior or providing a specific option.

An implementation class will be created with parameters specific to
that implementation, then provide a method to connect pins to the
appropriate circuit objects.

### Shields
Sheilds are implementations for specific connections. Since the
connections are hard wired, the instance objects will have methods to
return the circuit objects by name, returning the circuit object with
the connections used by the sheild.

## Servo circuits
A Python vesion of the PyBoard's Servo driver, but a bit more
flexible. Servos allow you to rotate the motor shaft to a specific
angle, or at a specific speed (a "continuous rotation" servo),
depending on the hardware, and to do so over a period of time.

The PyBoard servo driver's "raw" pulse widths are replaced by width
measured in microseconds.

## H-bridge circuits
An h-bridge circuit is four switches controlling inputs to a
motor. While four switches imply 16 different states, some of them are
uninteresting duplicates of other states, and some are to interesting,
shorting power across the motor and destroying your hardware.  So
there are four interesting states, controlled by *in1* and *in2*.

### H-bridge inputs
The two inputs *in1* and *in2* select between four different states:

1. Both inputs low turns off the drive so the motor coasts.
2. One input high and one low drives the motor in one direction.
3. Swapping the state of the inputs reverses the motor direction.
4. Both inputs high will apply a braking force to the motor.

### H-bridge controls
The speed of a motor can be controlled by using a pwm signal on one of
the inputs. If the high input is a pwm signal, then the motor switches
between run and coast modes, with a higher duty cycle being higher
speed. If the low input is a pwm signal, the motor switches between
run and brake modes, with a higher duty cycle being lower
speed. Run/coast mode is a bit easier on the electronics, but the
ouput power falls off very quickly as the duty cycle drops. Run/brake
mode doesn't have that problem, and is often preferable because of it.
In tests with the DRV8835, run/brake mode could move my platform with
a duty cycle below 10%, but run/coast wouldn't budget it until the
duty cycle was over 50%.

The downside of this approach is that having variable speed in both
directions requires pwm signals on both inputs. So a common
alternative input scheme replaces those two inputs, only one of which
needs to be pwm. One is *direction* (or *phase*), and is sent to the
two inputs to the h-bridge, one inverted. The motor runs in one
direction when it is high, and the other when low. The other is
normally called *enable*, and switches the inputs between the state
selected by *direction* and both being in the same state, either on or
off. Using pwm on this input makes it a speed control, providing a
bi-directional variable speed motor control with a single pwm signal.

### Fundumoto - L298-based Arduino motor/servo/sensor shield
This is a very basic shield, using a single L289 with a pair of
h-bridges, wired as run/coast motors with enable and direction
inputs. Due to it's simple nature, it just uses the h-bridge driver
directly.

It also provides a buzzer and servo connectors.

### DRV8835 - Driver for the TI DRV8835 on the Polulu carrier.
This chip supports both a run/brake mode with speed and direction
inputs, or the two pwm inputs passed through to the h-bridge. A single
mode input selects the mode for both h-bridges on the chip.

There is
an [Arduino shield version](https://www.pololu.com/product/2511) of
this from Pololu. The mode input is connected to ground or vcc, and
not under software control.
