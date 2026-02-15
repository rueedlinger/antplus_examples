import sys
import threading
from openant.easy.node import Node
from openant.devices import ANTPLUS_NETWORK_KEY
from openant.devices.bike_speed_cadence import (
    BikeSpeedData,
    BikeCadenceData,
)
from openant.devices.heart_rate import HeartRateData
from openant.devices.power_meter import PowerData
from openant.devices.common import AntPlusDevice, DeviceData
from openant.devices.common import DeviceType
from openant.devices.scanner import Scanner

from openant.devices.utilities import auto_create_device


def fmt(val, decimals=2):
    if val is None:
        return "--"
    return f"{val:.{decimals}f}"


class Monitor:
    def __init__(self, wheel_circumference_m=0.141):
        self.power = 0
        self.speed = 0
        self.cadence = 0
        self.distance = 0
        self.heart_rate = 0
        self.wheel_circumference_m = wheel_circumference_m

    def start(self):
        try:
            self.devices: list[AntPlusDevice] = []
            self.node = Node()
            self.node.set_network_key(0x00, ANTPLUS_NETWORK_KEY)

            self.scanner = Scanner(self.node, device_id=0, device_type=0)
            self.scanner.on_found = self._on_found

        except Exception as e:
            print(f"Error initializing ANT+ node or scanner: {e}")
            self.node.stop() if self.node else None
            raise e

        self.node_thread = threading.Thread(target=self._run_node, daemon=True)
        self.node_thread.start()

    def stop(self):
        self._cleanup_devices()

        try:
            self.node.stop()
        except Exception:
            pass

        if self.node_thread:
            self.node_thread.join()

    def display(self):
        # Clear previous lines (optional: one line for devices, one for stats)
        sys.stdout.write("\033[2J\033[H")  # Clear screen and move cursor to top

        # Print all registered devices
        if self.devices:
            device_names = ", ".join(device.name for device in self.devices)
            print(f"Registered Devices: {device_names}")
        else:
            print("Registered Devices: None")

        # Print live stats on the next line
        sys.stdout.write(
            "\r"  # Carriage return
            f"Power: {self.power or '--'} W | "
            f"Speed: {fmt(self.speed)} km/h | "
            f"Cadence: {fmt(self.cadence)} rpm | "
            f"Distance: {fmt(self.distance)} m | "
            f"Heart Rate: {self.heart_rate or '--'} bpm\n"
        )
        sys.stdout.flush()

    def _on_device_data(self, page: int, page_name: str, data: DeviceData):
        try:
            if isinstance(data, BikeCadenceData):
                self.cadence = data.calculate_cadence()

            if isinstance(data, HeartRateData):
                self.heart_rate = data.heart_rate

            if isinstance(data, BikeSpeedData):
                self.speed = data.calculate_speed(self.wheel_circumference_m)
                self.distance = data.calculate_distance(self.wheel_circumference_m)

            if isinstance(data, PowerData):
                self.power = data.average_power

        except Exception as e:
            print(f"Error processing device data update: {e}")

    def _on_found(self, device_tuple):
        device_id, device_type, device_trans = device_tuple
        if DeviceType(device_type) in (
            DeviceType.BikeCadence,
            DeviceType.BikeSpeed,
            DeviceType.BikeSpeedCadence,
            DeviceType.HeartRate,
            DeviceType.PowerMeter,
        ):
            try:
                # TODO cehck device ids
                dev = auto_create_device(
                    self.node, device_id, device_type, device_trans
                )

                # print(f"Created device {dev}, type {type(dev)}")
                dev.on_device_data = lambda page, page_name, data: self._on_device_data(
                    page, page_name, data
                )
                self.devices.append(dev)
            except Exception as e:
                print(f"Could not auto create device: {e}")

    def _run_node(self):
        try:
            self.node.start()  # blocking
        except Exception as e:
            print("Node error:", e)

    def _cleanup_devices(self):
        for dev in self.devices:
            try:
                dev.close_channel()
            except Exception:
                pass

        self.devices.clear()
