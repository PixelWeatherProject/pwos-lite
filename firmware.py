from sysc.logging import os_debug, os_error, os_warn, os_info
from sysc.pwmp_client import PwmpClient
import network
from time import time
from sysc.config import sys as sysconfig
from sysc.config.app import AppConfig
from machine import deepsleep
from sysc.drivers import htu21d
from sysc.envsensor import EnvironmentMeasurements

SBOP_SLEEP_TIME = 2_629_746_000 # 1 month

def fw_main(battery, i2c, led, appcfg) -> None:
    fw_debug("Running firmware")

    fw_debug("Starting WiFi setup")
    wifi = setup_wifi()
    fw_debug("Connecting to PWMP")
    pws = PwmpClient(sysconfig.PWMP_HOST, sysconfig.PWMP_PORT, 10)

    fw_debug("Sending handshake request")
    pws.perform_handshake(wifi.config("mac"))

    fw_debug("Requesting app configuration")
    appcfg = read_appcfg(pws) or appcfg
    fw_debug("Settings updated")

    bat_voltage = battery.read(64)
    fw_info("Battery: %.02f" % bat_voltage)
    if (bat_voltage <= battery.CRITICAL_VOLTAGE) and (appcfg.sbop):
        fw_warn("Battery voltage too low, activating sBOP")
        pws.send_notification("Battery voltage too low, activating sBOP")
        #deepsleep()
    
    envsensor = setup_envsensor(i2c)
    results = EnvironmentMeasurements(envsensor)
    fw_info("%.02f*C / %.00f%%" % (results.temperature, results.humidity))
    fw_debug("Posting measurements")
    pws.post_measurements(results)

def setup_wifi() -> network.WLAN:
    ### Initialization

    fw_debug("Initializing WiFi")
    wlan = network.WLAN()
    wlan.active(True)
    wlan.disconnect() # Disconnect from previous network

    ### Scanning

    fw_debug("Starting WiFi scan")
    start = time()
    networks = wlan.scan()
    elapsed = time() - start
    fw_debug("Found networks: " + repr(networks) + " in " + str(elapsed) + "s")

    ### Filtering

    # filter out unknown APs
    known_ap_names = map(lambda entry: entry[0], sysconfig.WIFI_NETWORKS)
    networks = filter(lambda ap: ap[0] in known_ap_names, networks)
    # filter out APs with RSSI >= -90
    networks = filter(lambda ap: ap[3] >= -85, networks)
    # sort by signal strength
    networks = sorted(networks, key = lambda ap: ap[3], reverse = True)

    if len(networks) == 0:
        fw_error("No usable networks found")
        raise Exception("offline")
    
    for ap in networks:
        name = ap[0].decode("utf-8")
        psk = next(filter(lambda entry: entry[0] == ap[0], sysconfig.WIFI_NETWORKS))[1]
        fw_debug("Connecting to " + name + " (" + str(ap[3]) + "dBm)")

        start = time()
        try:
            wlan.connect(name, psk)

            while wlan.status() != network.STAT_GOT_IP:
                if (time() - start) >= sysconfig.WIFI_CONNECT_TIMEOUT:
                    raise Exception("connect() timed out")
            
        except Exception as ex:
            fw_error("Failed to connect: " + repr(ex))
        
        fw_debug("Connected in " + str(time() - start) + "s")
        fw_debug("IP: " + wlan.ifconfig()[0])
        
    if wlan.status() != network.STAT_GOT_IP:
        raise Exception("offline")
    
    return wlan

def read_appcfg(pws: PwmpClient) -> AppConfig:
    fw_debug("Reading settings")
    cfg = pws.get_settings()

    if cfg == None:
        fw_warn("Got empty node settings, using defaults")

    return cfg

def setup_envsensor(i2c) -> None:
    devices = i2c.scan()

    for device in devices:
        if device == htu21d.HTU21D.ADDRESS:
            fw_debug("Detected HTU-compatible sensor")
            return htu21d.HTU21D(i2c)
        else:
            fw_warn("Unrecognised device @ I2C/" + hex(device))
    
    raise Exception("No environment sensor found")

def fw_info(msg: str) -> None:
    os_info("pwos::firmware", msg)

def fw_warn(msg: str) -> None:
    os_warn("pwos::firmware", msg)

def fw_error(msg: str) -> None:
    os_error("pwos::firmware", msg)

def fw_debug(msg: str) -> None:
    os_debug("pwos::firmware", msg)