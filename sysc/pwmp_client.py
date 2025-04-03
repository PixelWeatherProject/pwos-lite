from .logging import os_info, os_debug
from random import randint
from sysc.config.app import AppConfig
import socket
import struct
import json

ID_CACHE_SIZE = 8

class PwmpClient:
    def __init__(self, host: str, port: int, timeout: int) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(timeout) # seconds
        self.socket.connect((host, port))

        self.id_cache = []
    
    def perform_handshake(self, mac: bytes) -> None:
        self.send_request({ "Handshake": { "mac": tuple(mac) } })
        msg = self.receive_message()

        if msg["content"]["Response"] == "Reject":
            raise Exception("Handshake rejected")
        elif msg["content"]["Response"] != "Ok":
            raise Exception("Unexpected handshake response: " + str(msg["content"]))
    
    def get_settings(self) -> AppConfig:
        self.send_request("GetSettings")
        response = self.receive_message()
        raw_settings = response["content"]["Response"]["Settings"]

        if raw_settings == None:
            return None
        
        new_config = AppConfig()
        new_config.battery_ignore = raw_settings["battery_ignore"]
        new_config.ota = raw_settings["ota"]
        new_config.sleep_time = raw_settings["sleep_time"]
        new_config.sbop = raw_settings["sbop"]
        new_config.mute_notifications = raw_settings["mute_notifications"]

        return new_config
    
    def send_notification(self, msg: str) -> None:
        self.send_request({ "SendNotification": msg })
        self.await_ok()
    
    def post_measurements(self, results) -> None:
        self.send_request({
            "PostResults": {
                "temperature": str(results.temperature),
                "humidity": results.humidity,
                "air_pressure": results.air_pressure
            }
        })
        self.await_ok()
    
    def post_stats(self, battery: float, ssid: str, rssi: int) -> None:
        self.send_request({
            "PostStats": {
                "battery": str(battery),
                "wifi_ssid": ssid,
                "wifi_rssi": rssi
            }
        })
        self.await_ok()
    
    def send_bye(self) -> None:
        self.send_request("Bye")

        try:
            while self.socket.recv(1):
                pass
        except:
            pass
    
    def await_ok(self) -> None:
        msg = self.receive_message()
        assert msg["content"]["Response"] == "Ok", "Expected `Ok` response, got: " + msg["content"]
    
    def send_request(self, req: dict) -> None:
        msg = self._construct_msg({ "Request": req })
        self.send_message(msg)

    def receive_message(self) -> dict:
        # First read the message size.
        msg_len_bytes = self._read_exact(4)

        # Parse the length.
        msg_len = int.from_bytes(msg_len_bytes, "big", False)

        # Verify the length
        if msg_len == 0:
            raise ValueError("Message length is zero")
        
        # Read the actual message.
        raw_msg = self._read_exact(msg_len)
        assert len(raw_msg) == msg_len, "Message length mismatch"

        # Parse the message.
        message = json.loads(raw_msg)

        # Check if it's not a duplicate.
        if self.is_id_cached(message["id"]):
            raise ValueError("Duplicate message")
        
        # Cache the ID.
        self.cache_id(message["id"])

        # Done.
        return message

    def send_message(self, msg: dict) -> None:
        # Make a copy of the message ID to use later.
        msg_id = msg["id"]

        # Serialize the message.
        raw = json.dumps(msg).encode("utf-8")

        # Get the length.
        msg_len = len(raw)

        # Check if the length is representable using a 32-bit integer.
        if msg_len > 2**32:
            raise ValueError("message length is too large")
        
        # Serialize the length into a series of big-endian bytes.
        msg_len_bytes = struct.pack(">I", msg_len)

        # Send the length first as big/network endian.
        self.socket.sendall(msg_len_bytes)

        # Send the actual message next.
        self.socket.sendall(raw)

        # Cache the ID.
        self.cache_id(msg_id)
    
    def _read_exact(self, n: int) -> bytearray:
        result = bytearray(n)
        read = 0
        
        while read != n:
            try:
                chunk = self.socket.recv(n - read)
                assert chunk, "Connection corrupt"
            except Exception as ex:
                raise Exception("Failed to fill the whole buffer: " + repr(ex))

            result[read:read + len(chunk)] = chunk
            read += len(chunk)
        
        return result
    
    def _construct_msg(self, content: dict) -> dict:
        msg_id = self._gen_msg_id()
        msg = {
            "id": msg_id,
            "content": content,
        }

        return msg

    def cache_id(self, id: int) -> None:
        if len(self.id_cache) == ID_CACHE_SIZE:
            self.id_cache.pop(0)
        
        self.id_cache.append(id)

    def is_id_cached(self, id: int) -> bool:
        # Check if the ID matches any of the cached ones.
        id in self.id_cache

    def _gen_msg_id(self) -> int:
        return randint(1, 1_000_000)