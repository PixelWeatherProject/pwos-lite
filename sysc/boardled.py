from machine import Pin

class BoardLed:
    def __init__(self, pin: int, invert: bool) -> None:
        self.pin = Pin(pin, Pin.OUT)
        self.invert = invert
    
    def on(self) -> None:
        if self.invert:
            self.pin.off()
        else:
            self.pin.on()
    
    def off(self) -> None:
        if self.invert:
            self.pin.on()
        else:
            self.pin.off()
