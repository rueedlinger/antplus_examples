from dataclasses import dataclass
from enum import Enum
import logging
import sys
import threading
from typing import List
from openant.easy.node import Node
from openant.devices import ANTPLUS_NETWORK_KEY
from openant.devices.bike_speed_cadence import (
    BikeSpeedData,
    BikeSpeed,
    BikeCadenceData,
    BikeCadence,
    BikeSpeedCadence,
)
from openant.devices.heart_rate import HeartRateData, HeartRate
from openant.devices.power_meter import PowerData, PowerMeter
from openant.devices.common import AntPlusDevice, DeviceData
from openant.devices.common import DeviceType
from openant.devices.scanner import Scanner

from openant.devices.utilities import auto_create_device


def fmt(val, decimals=2):
    if val is None:
        return "--"
    return f"{val:.{decimals}f}"


class SensorType(Enum):
    BIKE_SPEED = "BIKE_SPEED"
    BIKE_CADENCE = "BIKE_CADENCE"
    BIKE_CADENCE_SPEED = "BIKE_CADENCE_SPEED"
    HEART_RATE = "HEART_RATE"
    POWER_METER = "POWER_METER"


@dataclass
class Sensor:
    device_id: int = 0
    sensor_type: SensorType = None


class Metrics:
    def __init__(self, sensors: List[Sensor] = [], wheel_circumference_m=0.141):
        self.power = 0
        self.speed = 0
        self.cadence = 0
        self.distance = 0
        self.heart_rate = 0
        self.wheel_circumference_m = wheel_circumference_m
        self.node = None
        self.node_thread = None
        self.sensors = sensors
        self.logger = logging.getLogger("app.metrics")

    def start(self):
        try:
            self.devices: list[AntPlusDevice] = []
            self.node = Node()
            self.node.set_network_key(0x00, ANTPLUS_NETWORK_KEY)

            if self.sensors is None or len(self.sensors) == 0:
                self.logger.info(
                    "No sensors specified, starting scanner for all devices"
                )
                self.scanner = Scanner(self.node, device_id=0, device_type=0)
                self.scanner.on_found = self._scanner_on_found
            else:
                self.logger.info(
                    f"Custom sensors specified: {[sensor.sensor_type for sensor in self.sensors]}"
                )
                for sensor in self.sensors:
                    self.logger.debug(f"Starting with specified sensor: {sensor}")

                    if sensor.sensor_type == SensorType.BIKE_SPEED:
                        dev = BikeSpeed(self.node, device_id=sensor.device_id)
                        dev.on_device_data = lambda page, page_name, data: (
                            self._on_device_data(page, page_name, data)
                        )
                        dev.on_found = lambda: self._on_device_found()
                        self.devices.append(dev)

                    elif sensor.sensor_type == SensorType.BIKE_CADENCE:
                        dev = BikeCadence(self.node, device_id=sensor.device_id)
                        dev.on_device_data = lambda page, page_name, data: (
                            self._on_device_data(page, page_name, data)
                        )
                        dev.on_found = lambda: self._on_device_found()
                        self.devices.append(dev)

                    elif sensor.sensor_type == SensorType.BIKE_CADENCE_SPEED:
                        dev = BikeSpeedCadence(self.node, device_id=sensor.device_id)
                        dev.on_device_data = lambda page, page_name, data: (
                            self._on_device_data(page, page_name, data)
                        )
                        dev.on_found = lambda: self._on_device_found()
                        self.devices.append(dev)

                    elif sensor.sensor_type == SensorType.HEART_RATE:
                        dev = HeartRate(self.node, device_id=sensor.device_id)
                        dev.on_device_data = lambda page, page_name, data: (
                            self._on_device_data(page, page_name, data)
                        )
                        dev.on_found = lambda: self._on_device_found()
                        self.devices.append(dev)

                    elif sensor.sensor_type == SensorType.POWER_METER:
                        dev = PowerMeter(self.node, device_id=sensor.device_id)
                        dev.on_device_data = lambda page, page_name, data: (
                            self._on_device_data(page, page_name, data)
                        )
                        dev.on_found = lambda: self._on_device_found()
                        self.devices.append(dev)

                    else:
                        # Unknown sensor type, log a warning
                        self.logger.warning(
                            f"Unknown sensor type: {sensor.sensor_type}"
                        )

        except Exception as e:
            self.logger.warning(
                "Error initializing ANT+ node or scanner", exc_info=True
            )
            self.node.stop() if self.node else None
            raise e

        self.node_thread = threading.Thread(target=self._run_node, daemon=True)
        self.node_thread.start()

    def stop(self):
        self._cleanup_devices()

        try:
            if self.node:
                self.node.stop()
        except Exception:
            self.logger.warning("Error stopping ANT+ node", exc_info=True)
            pass

        if self.node_thread:
            self.node_thread.join()

    def to_dict(self):
        return {
            "power": self.power,
            "speed": self.speed,
            "cadence": self.cadence,
            "distance": self.distance,
            "heart_rate": self.heart_rate,
        }

    def display(self):
        # Clear previous lines (optional: one line for devices, one for stats)
        sys.stdout.write("\033[2J\033[H")  # Clear screen and move cursor to top

        # Print all registered devices
        if self.devices:
            devices_info = ", ".join(
                f"{device.name} ({device.device_id})" for device in self.devices
            )
            print(f"Registered Devices: {devices_info}")
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

        except Exception:
            self.logger.warning("Error processing device data update", exc_info=True)

    def _scanner_on_found(self, device_tuple):
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
                dev: AntPlusDevice = auto_create_device(
                    self.node, device_id, device_type, device_trans
                )

                # print(f"Created device {dev}, type {type(dev)}")
                dev.on_device_data = lambda page, page_name, data: self._on_device_data(
                    page, page_name, data
                )
                self.devices.append(dev)
            except Exception:
                self.logger.warning("Could not auto create device", exc_info=True)

    def _on_device_found(self):
        self.logger.debug("Found new device")

    def _run_node(self):
        try:
            self.node.start()  # blocking
        except Exception:
            self.logger.warning("Node error", exc_info=True)

    def _cleanup_devices(self):
        for dev in self.devices:
            try:
                dev.close_channel()
            except Exception:
                self.logger.warning("Could not close device channel", exc_info=True)

        self.devices.clear()
