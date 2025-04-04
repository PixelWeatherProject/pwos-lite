from sysc.logging import os_info, os_debug, os_error
from sysc.battery import Battery
from sysc.boardled import BoardLed
from firmware import fw_main
from machine import I2C, Pin, deepsleep, freq
from sysc.config import sys as sysconfig
from sysc.config.app import AppConfig
from time import time_ns
from sys import print_exception

os_info("pwos", "PixelWeatherOS Lite")
os_info("pwos", "(C) Fábián Varga 2025")

# Overclock to 240MHz
freq(240_000_000)

os_debug("pwos", "Initializing system LED")
led = BoardLed(sysconfig.ONBOARD_LED_PIN, sysconfig.ONBOARD_LED_INVERT)
led.on()

os_debug("pwos", "Initializing system Battery")
battery = Battery(2)

os_debug("pwos", "Initializing I2C bus")
i2c = I2C(1, scl = 8, sda = 5, freq = 100000)

os_debug("pwos", "Initializing app configuration")
appcfg = AppConfig()

start = time_ns()

os_info("pwos", "Starting firmware")
try:
    fw_main(battery, i2c, led, appcfg)
    os_info("pwos", "Tasks completed successfully")
except Exception as ex:
    os_error("pwos", "Firmware failed: " + repr(ex))
    print_exception(ex)

elapsed = ((time_ns() - start) / 1000000) / 1000 # convert ns to secs
os_info("pwos", "Tasks completed in %.02fs" % elapsed)

#os_debug("pwos", "Sleeping for " + str(appcfg.sleep_time) + "s")
#deepsleep(appcfg.sleep_time * 1000)