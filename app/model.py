from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SportZone(str, Enum):
    """Defines sport zones based on heart rate percentage of HRmax.
    https://www.polar.com/en/guide/heart-rate-zones
    """

    UNKNOWN = "UNKNOWN"
    RESTING = "Resting Heart Rate"
    ZONE_1 = "Very Light - Recovery"
    ZONE_2 = "Light - Fat Burn"
    ZONE_3 = "Moderate - Cardio"
    ZONE_4 = "Hard - Threshold"
    ZONE_5 = "Maximum - Peak"

    @staticmethod
    def hrmax_from_age(age: int) -> Optional[float]:
        """
        Estimate HRmax using the common formula: 220 - age
        Returns None for invalid age.
        """
        if age is None or age <= 0:
            return None
        return float(220 - age)

    @staticmethod
    def percent_from_age(age: int, heart_rate: float) -> Optional[float]:
        """
        Returns heart rate percentage of estimated HRmax.
        Returns None if inputs are invalid.
        """
        if heart_rate is None or heart_rate <= 0:
            return None

        hrmax = SportZone.hrmax_from_age(age)
        if hrmax is None or hrmax <= 0:
            return None

        return (heart_rate / hrmax) * 100

    @staticmethod
    def from_hr_percent(percent: Optional[float]) -> "SportZone":
        """
        Returns the sport zone based on percentage of HRmax.
        """
        if percent is None or percent < 0:
            return SportZone.UNKNOWN

        if percent < 50:
            return SportZone.RESTING
        if percent < 60:
            return SportZone.ZONE_1
        if percent < 70:
            return SportZone.ZONE_2
        if percent < 80:
            return SportZone.ZONE_3
        if percent < 90:
            return SportZone.ZONE_4
        if percent <= 100:
            return SportZone.ZONE_5

        return SportZone.UNKNOWN

    @staticmethod
    def sport_zone(age: int, heart_rate: float) -> "SportZone":
        """
        Convenience method: calculates percentage and returns zone.
        """
        percent = SportZone.percent_from_age(age, heart_rate)
        return SportZone.from_hr_percent(percent)

    def to_tuple(self) -> tuple[str, str]:
        """
        Returns (formatted_zone_name, zone_value)
        Example: ("ZONE 3", "Moderate - Cardio")
        """
        formatted_name = self.name.replace("_", " ")
        return formatted_name, self.value


class MetricsSettingsModel(BaseModel):
    speed_wheel_circumference_m: Optional[float] = Field(
        None, gt=0, description="Wheel circumference in meters (speed sensor)"
    )
    distance_wheel_circumference_m: Optional[float] = Field(
        None, gt=0, description="Wheel circumference in meters (distance sensor)"
    )
    age: Optional[int] = Field(None, gt=0, description="User age in years")


class DeviceModel(BaseModel):
    device_id: int
    device_type: int
    name: str


class MetricsModel(BaseModel):
    power: Optional[int] = None
    ma_power: Optional[float] = None

    speed: Optional[float] = None
    ma_speed: Optional[float] = None

    cadence: Optional[float] = None
    ma_cadence: Optional[float] = None

    distance: Optional[float] = None
    ma_distance: Optional[float] = None

    heart_rate: Optional[int] = None
    ma_heart_rate: Optional[float] = None

    heart_rate_percent: Optional[float] = None
    ma_heart_rate_percent: Optional[float] = None

    zone_name: Optional[str] = None
    zone_description: Optional[str] = None

    ma_zone_name: Optional[str] = None
    ma_zone_description: Optional[str] = None

    is_running: Optional[bool] = None
    last_sensor_update: Optional[datetime] = None
    last_sensor_name: Optional[str] = None


class IntervalModel(BaseModel):
    seconds: int
    name: str


class IntervalProgressModel(BaseModel):
    interval: Optional[IntervalModel] = None
    time_spent: Optional[float] = None
    time_remaining: Optional[float] = None
    total_time_spent: Optional[float] = None
    round_number: Optional[int] = None
    is_running: Optional[bool] = None
