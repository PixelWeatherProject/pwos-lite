from machine import ADC, Pin
from time import sleep_ms

class Battery:
    # Value of the first resistor of the voltage divider
    R1 = 1_000_000 # 1MOhm
    # Value of the second resistor of the voltage divider
    R2 = 300_000 # 300kOhm

    # Critical voltage value that's still higher than the minimum supply voltage for the ESP32S3
    CRITICAL_VOLTAGE = 3.22

    def __init__(self, pin: int) -> None:
        self.adc = ADC(Pin(pin), atten = 0)
    
    def read(self, samples: int) -> float:
        """ Read the ADC value and calculate the voltage. """
        raw = self.read_raw(samples)
        div_volts = (3.3 / 4095) * raw
        in_volts = (div_volts * (self.R1 + self.R2)) / self.R2

        return in_volts
    
    def read_raw(self, samples: int) -> int:
        """ Read the raw ADC value. """
        avg = 0

        for _ in range(samples):
            avg += self.adc.read()
            sleep_ms(1)
        
        avg /= samples
        return avg