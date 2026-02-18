import logging
import threading
from typing import List
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


class Metrics:
    def __init__(self, filter_device_ids: List[int] = [], wheel_circumference_m=0.141):
        self.power = None
        self.speed = None
        self.cadence = None
        self.distance = None
        self.heart_rate = None
        self.wheel_circumference_m = wheel_circumference_m
        self.node = None
        self.node_thread = None
        self.filter_device_ids = filter_device_ids
        self.logger = logging.getLogger("app.ant.metrics")
        self.is_running = False
        self.lock = threading.Lock()
        self.devices: List[AntPlusDevice] = []

    def set_wheel_circumference(self, circumference_m):
        if circumference_m <= 0:
            self.logger.warning(
                f"Invalid wheel circumference value: {circumference_m}. Must be > 0."
            )
            return
        self.logger.debug(f"Wheel circumference updated to {circumference_m} m")
        self.wheel_circumference_m = circumference_m

    def start(self):
        with self.lock:  # acquire and release automatically
            if self.is_running:
                self.logger.warning("Metrics collection already running")
                return

            try:
                self.devices: list[AntPlusDevice] = []
                self.node = Node()
                self.node.set_network_key(0x00, ANTPLUS_NETWORK_KEY)

                self.scanner = Scanner(self.node, device_id=0, device_type=0)
                self.scanner.on_found = self._scanner_on_found

            except Exception as e:
                self.logger.warning(
                    "Error initializing ANT+ node or scanner", exc_info=True
                )
                self.node.stop() if self.node else None
                raise e

            self.node_thread = threading.Thread(target=self._run_node, daemon=True)
            self.node_thread.start()
            self.is_running = True

    def stop(self):
        with self.lock:
            if not self.is_running:
                self.logger.warning("Metrics collection already stopped")
                return

            self.is_running = False
            self._cleanup_devices()

            try:
                if self.node:
                    self.logger.debug("Stopping ANT+ node")
                    self.node.stop()
            except Exception:
                self.logger.warning("Error stopping ANT+ node", exc_info=True)

            if self.node_thread:
                self.node_thread.join(timeout=5)

            self._reset_metrics()

    def get_metrics(self, round_values=True):
        metrics = {
            "power": self.power,
            "speed": self.speed,
            "cadence": self.cadence,
            "distance": self.distance,
            "heart_rate": self.heart_rate,
            "wheel_circumference_m": self.wheel_circumference_m,
            "is_running": self.is_running,
        }
        if round_values:
            for key in ["power", "speed", "cadence", "distance"]:
                if metrics[key] is not None:
                    metrics[key] = round(metrics[key], 2)
        return metrics

    def _reset_metrics(self):
        self.power = None
        self.speed = None
        self.cadence = None
        self.distance = None
        self.heart_rate = None

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

        if self.filter_device_ids is None or len(self.filter_device_ids) == 0:
            self.logger.debug(
                "No device ID filter set, accepting all devices. Found ID: {}, Type: {}".format(
                    device_id, device_type
                )
            )
            self._create_sensor_device(device_id, device_type, device_trans)
        else:
            if device_id in self.filter_device_ids:
                self.logger.debug(
                    f"Device ID {device_id} matches filter, creating sensor"
                )
                self._create_sensor_device(device_id, device_type, device_trans)

    def _create_sensor_device(self, device_id, device_type, device_trans):
        if DeviceType(device_type) in (
            DeviceType.BikeCadence,
            DeviceType.BikeSpeed,
            DeviceType.BikeSpeedCadence,
            DeviceType.HeartRate,
            DeviceType.PowerMeter,
        ):
            try:
                self.logger.info(
                    f"Creating device for ID: {device_id}, Type: {device_type}"
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
            self.is_running = True
            self.node.start()  # blocking
        except Exception:
            self.logger.warning("Node error", exc_info=True)
        finally:
            self.is_running = False

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
