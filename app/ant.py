from dataclasses import dataclass
from enum import Enum
import logging
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


class SensorType(Enum):
    BIKE_SPEED = "BIKE_SPEED"
    BIKE_CADENCE = "BIKE_CADENCE"
    BIKE_SPEED_CADENCE = "BIKE_SPEED_CADENCE"
    HEART_RATE = "HEART_RATE"
    POWER_METER = "POWER_METER"


@dataclass
class Sensor:
    device_id: int = 0
    sensor_type: SensorType = None


class SensorScanner:
    def __init__(self):
        self.device_id = 0
        self.device_type = 0
        self.node = None
        self.node_thread = None
        self.logger = logging.getLogger("app.ant.scanner")
        self.devices: List[Sensor] = []

    def start(self):
        try:
            self.node = Node()
            self.node.set_network_key(0x00, ANTPLUS_NETWORK_KEY)
            self.scanner = Scanner(
                self.node, device_id=self.device_id, device_type=self.device_type
            )
            self.scanner.on_found = self._scanner_on_found
        except Exception as e:
            self.logger.warning(
                "Error initializing ANT+ node or scanner", exc_info=True
            )
            self.node.stop() if self.node else None
            raise e

        self.node_thread = threading.Thread(target=self._run_node, daemon=True)
        self.node_thread.start()

    def stop(self):
        try:
            if self.node:
                self.logger.debug("Stopping ANT+ node")
                self.node.stop()
        except Exception:
            self.logger.warning("Error stopping ANT+ node", exc_info=True)
            pass

    def get_devices(self):
        return self.devices

    def _run_node(self):
        try:
            self.logger.debug("Starting ANT+ node")
            self.node.start()  # blocking
        except Exception:
            self.logger.warning("Node error", exc_info=True)

    def _scanner_on_found(self, device_tuple):
        device_id, device_type, device_trans = device_tuple

        self.logger.debug(
            f"Found device - ID: {device_id}, Type: {device_type}, Trans: {device_trans}"
        )

        if DeviceType(device_type) == DeviceType.BikeCadence:
            self.devices.append(
                Sensor(device_id=device_id, sensor_type=SensorType.BIKE_CADENCE)
            )

        elif DeviceType(device_type) == DeviceType.BikeSpeed:
            self.devices.append(
                Sensor(device_id=device_id, sensor_type=SensorType.BIKE_SPEED)
            )

        elif DeviceType(device_type) == DeviceType.BikeSpeedCadence:
            self.devices.append(
                Sensor(device_id=device_id, sensor_type=SensorType.BIKE_SPEED_CADENCE)
            )

        elif DeviceType(device_type) == DeviceType.HeartRate:
            self.devices.append(
                Sensor(device_id=device_id, sensor_type=SensorType.HEART_RATE)
            )

        elif DeviceType(device_type) == DeviceType.PowerMeter:
            self.devices.append(
                Sensor(device_id=device_id, sensor_type=SensorType.POWER_METER)
            )

        else:
            # Unknown device type, log a warning
            self.logger.warning(f"Unknown device type found: {device_type}")


class Metrics:
    def __init__(self, sensors: List[Sensor] = [], wheel_circumference_m=0.141):
        self.power = None
        self.speed = None
        self.cadence = None
        self.distance = None
        self.heart_rate = None
        self.wheel_circumference_m = wheel_circumference_m
        self.node = None
        self.node_thread = None
        self.sensors = sensors
        self.logger = logging.getLogger("app.ant.metrics")

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

                    elif sensor.sensor_type == SensorType.BIKE_SPEED_CADENCE:
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
                self.logger.debug("Stopping ANT+ node")
                self.node.stop()
        except Exception:
            self.logger.warning("Error stopping ANT+ node", exc_info=True)
            pass

        if self.node_thread:
            self.node_thread.join()

    def get_metrics(self):
        return {
            "power": self.power,
            "speed": self.speed,
            "cadence": self.cadence,
            "distance": self.distance,
            "heart_rate": self.heart_rate,
            "wheel_circumference_m": self.wheel_circumference_m,
        }

    def get_devices(self):
        return [
            {
                "device_id": dev.device_id,
                "device_type": dev.device_type,
                "name": dev.name,
            }
            for dev in self.devices
        ]

    def _on_device_data(self, page: int, page_name: str, data: DeviceData):
        try:
            self.logger.debug(
                "Received data from device - Page: {}, Page Name: {}, Data: {}".format(
                    page, page_name, data
                )
            )

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

        self.logger.debug(
            f"Found device - ID: {device_id}, Type: {device_type}, Trans: {device_trans}"
        )

        if DeviceType(device_type) in (
            DeviceType.BikeCadence,
            DeviceType.BikeSpeed,
            DeviceType.BikeSpeedCadence,
            DeviceType.HeartRate,
            DeviceType.PowerMeter,
        ):
            try:
                self.logger.info(
                    f"Auto-creating device for ID: {device_id}, Type: {device_type}"
                )
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
            self.logger.debug("Starting ANT+ node")
            self.node.start()  # blocking
        except Exception:
            self.logger.warning("Node error", exc_info=True)

    def _cleanup_devices(self):
        for dev in self.devices:
            try:
                self.logger.debug(
                    f"Closing channel for device ID: {dev.device_id}, Type: {dev.device_type}"
                )
                dev.close_channel()
            except Exception:
                self.logger.warning("Could not close device channel", exc_info=True)

        self.devices.clear()
