class Gang:
    """Coordinated control of groups of motors.
    
    Pass in two lists of motors: the forward set runs forward to go
    forward, the reverse set needs to run in reverse to go forward."""

    def __init__(self, forward, reverse):
        self._forward = forward
        self._reverse = reverse
        delta = len(forward) - len(reverse)
        if delta > 0:
            self._reverse += [None] * delta
        elif delta < 0:
            self._forward +=  [None] * -delta
        
    def go(self, speed):
        """Go at given speed, from -100 to 100.
            
        Set forward to false to go in reverse."""

        # Zip the engines together so we have at most one extra engine
        # in a gang running.
        for m1, m2 in zip(self._forward, self._reverse):
            if m1:
                m1.go(speed)
            if m2:
                m2.go(-speed)
        
    def forward(self, speed):
        """Drive motors to go forward."""

        self.go(speed)

    def reverse(self, speed):
        """Drive motors to go in reverse."""

        self.go(-speed)

    def coast(self):
        """Stop running the motors."""
        
        self.go(0)

    def brake(self):
        """Active braking if the driver supports it. Worst case,
        just stop the motors."""

        for m1, m2 in zip(self._forward, self._reverse):
            if m1:
                m1.brake()
            if m2:
                m2.brake()
