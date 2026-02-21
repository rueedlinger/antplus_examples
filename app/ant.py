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

from app.model import MetricsModel, MetricsSettingsModel


class Metrics:
    def __init__(
        self,
        filter_device_ids: List[int] = [],
        metrics_settings: MetricsSettingsModel = MetricsSettingsModel(),
    ):
        self.logger = logging.getLogger("app.ant.metrics")

        self.node = None
        self.node_thread = None
        self.lock = threading.Lock()
        self.devices: List[AntPlusDevice] = []

        if metrics_settings is None:
            self.metrics_settings: MetricsSettingsModel = MetricsSettingsModel()
        else:
            self.metrics_settings = metrics_settings
        self.filter_device_ids = self.set_filter_device_ids(filter_device_ids)
        self._reset_metrics()
        self.is_running = False

    def set_metrics_settings(self, metrics_settings: MetricsSettingsModel):
        self.logger.debug(f"Setting metrics settings: {metrics_settings}")
        if metrics_settings is None:
            self.logger.warning("Received None for metrics settings, ignoring update")
            raise ValueError(
                "Metrics settings must be a valid MetricsSettingsModel object"
            )
        self.metrics_settings = metrics_settings

    def get_metrics_settings(self) -> MetricsSettingsModel:
        self.logger.debug(f"Getting metrics settings: {self.metrics_settings}")
        return self.metrics_settings

    def set_filter_device_ids(self, filter_device_ids: List[int]):

        # Validate that all entries are integers
        if not all(isinstance(id, int) for id in filter_device_ids):
            self.logger.warning(
                f"Invalid filter_device_ids: {filter_device_ids}. All entries must be integers."
            )
            raise ValueError("All device IDs in filter_device_ids must be integers")

        if filter_device_ids is None:
            filter_device_ids = []

        self.filter_device_ids = filter_device_ids
        self.logger.debug(f"Device ID filter updated: {filter_device_ids}")

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

            if self.node:
                try:                
                    self.logger.debug("Stopping ANT+ node")
                    self.node.stop()
                except Exception:
                    self.logger.warning("Error stopping ANT+ node", exc_info=True)


              # Wait for thread but don’t block forever
            if self.node_thread and self.node_thread.is_alive():
                self.node_thread.join(timeout=1)  # short timeout
            
            self._reset_metrics()

    def get_metrics(self, round_values=False) -> MetricsModel:
        metrics = {
            "power": self.power,
            "speed": self.speed,
            "cadence": self.cadence,
            "distance": self.distance,
            "heart_rate": self.heart_rate,
            "is_running": self.is_running,
            "heart_rate_percent": self.heart_rate_percent,
            "zone_name": self.zone_name,
            "zone_value": self.zone_value,
        }
        if round_values:
            for key in ["power", "speed", "cadence", "distance", "heart_rate"]:
                if metrics[key] is not None:
                    metrics[key] = round(metrics[key], 2)

        return MetricsModel(**metrics)

    def _reset_metrics(self):
        self.power = None
        self.speed = None
        self.cadence = None
        self.distance = None
        self.heart_rate = None
        self.heart_rate_percent = None
        self.zone_name = None
        self.zone_value = None
        self.zone = None

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
                speed_wheel_circumference = (
                    self.metrics_settings.speed_wheel_circumference_m
                )
                if (
                    speed_wheel_circumference is not None
                    and speed_wheel_circumference > 0
                ):
                    self.speed = data.calculate_speed(speed_wheel_circumference)

                distance_wheel_circumference = (
                    self.metrics_settings.distance_wheel_circumference_m
                )
                if (
                    distance_wheel_circumference is not None
                    and distance_wheel_circumference > 0
                ):
                    self.distance = data.calculate_distance(
                        distance_wheel_circumference
                    )

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
