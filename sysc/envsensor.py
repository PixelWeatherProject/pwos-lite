class EnvironmentSensor:
    """ Contains functionality that an environment sensor must be able to do. """

    def connected(self) -> bool:
        """
        Check if the environment sensor is connected.

        Upon a connection or communication error, an exception shall be raised.
        """
        raise Exception("not implemented")
    
    def read_temperature(self) -> float:
        """
        Read environment temperature.

        Upon a connection or communication error, an exception shall be raised.
        """
        raise Exception("not implemented")
    
    def read_humidity(self) -> int:
        """
        Read environment *(relative)* humidity.

        Upon a connection or communication error, an exception shall be raised.
        """
        raise Exception("not implemented")
    
    def read_air_pressure(self) -> int:
        """
        Read environment air pressure in hPa. If the sensor does not support this
        feature, `None` shall be returned.

        Upon a connection or communication error, an exception shall be raised.
        """
        raise Exception("not implemented")

class EnvironmentMeasurements:
    def __init__(self, envs: EnvironmentSensor) -> None:
        if not envs.connected():
            raise Exception("Environment sensor is not connected")
        
        self.temperature = envs.read_temperature()
        self.humidity = envs.read_humidity()
        self.air_pressure = envs.read_air_pressure()