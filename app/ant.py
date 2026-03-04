from datetime import datetime
import logging
import threading
import time
from typing import List
from openant.easy.node import Node
from openant.devices import ANTPLUS_NETWORK_KEY
from openant.devices.bike_speed_cadence import (
    BikeSpeedData,
    BikeCadenceData,
)
from openant.devices.heart_rate import HeartRateData
from openant.devices.power_meter import PowerData
from openant.devices.common import AntPlusDevice, BatteryData, DeviceData
from openant.devices.common import DeviceType
from openant.devices.scanner import Scanner

from openant.devices.utilities import auto_create_device

from app.model import MetricsModel, MetricsSettingsModel, DeviceModel, SportZone
from app.util import CumulativeSumMap, MetricsKey, TimedMap, TimedMovingAverage


class Metrics:
    def __init__(
        self,
        filter_device_ids: List[int] = [],
        metrics_settings: MetricsSettingsModel = MetricsSettingsModel(),
    ):
        self.logger = logging.getLogger("app.metrics")

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
        self.logger.debug(f"Updating metrics_settings: {self.metrics_settings}")

    def get_metrics_settings(self) -> MetricsSettingsModel:
        return self.metrics_settings

    def set_filter_device_ids(self, filter_device_ids: List[int]):

        # Validate that all entries are integers
        if not all(isinstance(id, int) for id in filter_device_ids):
            self.logger.warning(
                "Invalid filter_device_ids: %s. All entries must be integers.",
                filter_device_ids,
            )
            raise ValueError("All device IDs in filter_device_ids must be integers")

        if filter_device_ids is None:
            filter_device_ids = []

        self.filter_device_ids = filter_device_ids
        self.logger.debug("Updating filter_device_ids: %s", filter_device_ids)

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

    def get_metrics(self) -> MetricsModel:

        if self.is_running is False:
            metrics = {
                "is_running": False,
            }
            return MetricsModel(**metrics)

        # power
        power = self.time_map.get(MetricsKey.POWER)
        ma_power = self.timed_moving_average.average(MetricsKey.POWER)

        # speed
        speed = self.time_map.get(MetricsKey.SPEED)
        ma_speed = self.timed_moving_average.average(MetricsKey.SPEED)

        # cadence
        cadence = self.time_map.get(MetricsKey.CADENCE)
        ma_cadence = self.timed_moving_average.average(MetricsKey.CADENCE)

        # distance
        distance = self.time_map.get(MetricsKey.DISTANCE)
        ma_distance = self.sum_map.sum(MetricsKey.DISTANCE)

        # heart rate & zone
        heart_rate = self.time_map.get(MetricsKey.HEART_RATE)
        heart_rate_percent = SportZone.percent_from_age(
            self.metrics_settings.age, heart_rate
        )
        zone = SportZone.from_hr_percent(heart_rate_percent)
        if zone == SportZone.UNKNOWN:
            zone = None

        ma_heart_rate = self.timed_moving_average.average(MetricsKey.HEART_RATE)
        ma_heart_rate_percent = SportZone.percent_from_age(
            self.metrics_settings.age, ma_heart_rate
        )
        ma_zone = SportZone.from_hr_percent(ma_heart_rate_percent)
        if ma_zone == SportZone.UNKNOWN:
            ma_zone = None

        metrics = {
            "power": power,
            "ma_power": ma_power,
            "speed": speed,
            "ma_speed": ma_speed,
            "cadence": cadence,
            "ma_cadence": ma_cadence,
            "distance": distance,
            "ma_distance": ma_distance,
            "heart_rate": heart_rate,
            "ma_heart_rate": ma_heart_rate,
            "heart_rate_percent": heart_rate_percent,
            "ma_heart_rate_percent": ma_heart_rate_percent,
            "zone_name": zone.name if zone else None,
            "ma_zone_name": ma_zone.name if ma_zone else None,
            "zone_description": zone.value if zone else None,
            "ma_zone_description": ma_zone.value if ma_zone else None,
            "is_running": self.is_running,
            "last_sensor_update": self.last_sensor_update,
            "last_sensor_name": self.last_sensor_name,
        }

        return MetricsModel(**metrics)

    def _reset_metrics(self):

        self.time_map = TimedMap(ttl=15)
        self.timed_moving_average = TimedMovingAverage(ttl=40)
        self.sum_map = CumulativeSumMap()

        self.last_sensor_update = None
        self.last_sensor_name = None

    def get_devices(self) -> List[DeviceModel]:

        return [
            DeviceModel(
                device_id=dev.device_id, device_type=dev.device_type, name=dev.name
            )
            for dev in self.devices
        ]

    def _on_device_data(self, page: int, page_name: str, data: DeviceData):
        try:
            if isinstance(data, BikeCadenceData):
                cadence = data.calculate_cadence()
                self.time_map.set(MetricsKey.CADENCE, cadence)
                self.timed_moving_average.add(MetricsKey.CADENCE, cadence)
                self.logger.debug("cadence: %s", cadence)

            if isinstance(data, HeartRateData):
                heart_rate = int(round(data.heart_rate))
                self.time_map.set(MetricsKey.HEART_RATE, heart_rate)
                self.timed_moving_average.add(MetricsKey.HEART_RATE, heart_rate)
                self.logger.debug("heart_rate: %s", heart_rate)

            if isinstance(data, BikeSpeedData):
                speed_wheel_circumference_m = (
                    self.metrics_settings.speed_wheel_circumference_m
                )
                if (
                    speed_wheel_circumference_m is not None
                    and speed_wheel_circumference_m > 0
                ):
                    speed = data.calculate_speed(speed_wheel_circumference_m)
                    self.time_map.set(MetricsKey.SPEED, speed)
                    self.timed_moving_average.add(MetricsKey.SPEED, speed)
                    self.logger.debug("speed: %s", speed)

                distance_wheel_circumference = (
                    self.metrics_settings.distance_wheel_circumference_m
                )
                if (
                    distance_wheel_circumference is not None
                    and distance_wheel_circumference > 0
                ):
                    distance = data.calculate_distance(distance_wheel_circumference)
                    self.time_map.set(MetricsKey.DISTANCE, distance)
                    self.sum_map.add(MetricsKey.DISTANCE, distance)
                    self.logger.debug("distance: %s", distance)

            if isinstance(data, PowerData):
                power = int(round(data.instantaneous_power))
                self.time_map.set(MetricsKey.POWER, power)
                self.timed_moving_average.add(MetricsKey.POWER, power)
                self.logger.debug("power: %s", power)

            self.last_sensor_update = datetime.now().astimezone()
            self.last_sensor_name = page_name

        except Exception:
            self.logger.warning("Error processing device data update", exc_info=True)

    def _scanner_on_found(self, device_tuple):
        device_id, device_type, device_trans = device_tuple

        self.logger.debug(
            "Found new device with device_id: %s, device_type: %s, device_trans:%s, filter_device_ids: %s",
            device_id,
            device_type,
            device_trans,
            self.filter_device_ids,
        )

        if self.filter_device_ids is None or len(self.filter_device_ids) == 0:
            self._create_sensor_device(device_id, device_type, device_trans)
        else:
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
                    "Creating new device with device_id: %s, device_type: %s",
                    device_id,
                    device_type,
                )
                dev: AntPlusDevice = auto_create_device(
                    self.node, device_id, device_type, device_trans
                )

                # print(f"Created device {dev}, type {type(dev)}")
                dev.on_device_data = lambda page, page_name, data: self._on_device_data(
                    page, page_name, data
                )

                # dev.on_battery = lambda data: self._on_device_battery(data)

                self.devices.append(dev)
            except Exception:
                self.logger.warning("Could not auto create device", exc_info=True)

    def _on_device_battery(self, data: BatteryData):
        self.logger.debug("BatteryData: %s", data)

    def _run_node(self):
        retries = 0
        while True:
            try:
                self.logger.debug("Starting ANT+ node")
                self.is_running = True
                self.node.start()  # blocking
                self.logger.debug("Ant+ Node returns from blocking")
                # exit loop
                break
            except Exception:
                self.logger.warning("Node error", exc_info=True)
                retries += 1
                self.logger.warning("Try node restart (retry={retries})")
                time.sleep(1)
            finally:
                self.is_running = False

    def _cleanup_devices(self):
        for dev in self.devices:
            try:
                self.logger.debug(
                    "Closing channel for device_id: %s, device_type: %s",
                    dev.device_id,
                    dev.device_type,
                )
                dev.close_channel()
            except Exception:
                self.logger.warning("Could not close device channel", exc_info=True)

        self.devices.clear()
