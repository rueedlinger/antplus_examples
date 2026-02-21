from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SportZone(str, Enum):
    """Defines sport zones based on heart rate percentage of HRmax.
    https://www.polar.com/en/guide/heart-rate-zones
    """

    ZONE_UNKNOWN = "Unknown"
    ZONE_1 = "Very Light"
    ZONE_2 = "Light"
    ZONE_3 = "Moderate"
    ZONE_4 = "Hard"
    ZONE_5 = "Maximum"

    @staticmethod
    def hrmax_from_age(age: int) -> float:
        """
        Estimate HRmax using the common formula: 220 - age
        Returns None for invalid age.
        """
        if age is None or age <= 0:
            return None
        return 220 - age

    @staticmethod
    def percent_from_age(age: int, heart_rate: float) -> float:
        """
        Returns heart rate percentage of estimated HRmax.
        Returns None if inputs are invalid.
        """
        if heart_rate is None:
            return None

        hrmax = SportZone.hrmax_from_age(age)
        if hrmax is None or hrmax <= 0:
            return None

        return (heart_rate / hrmax) * 100

    @staticmethod
    def from_hr_percent(percent: float) -> SportZone:
        """
        Returns the sport zone based on percentage of HRmax.
        :param percent: Heart rate as percentage of HRmax (0–100)
        """
        if percent is None:
            return SportZone.ZONE_UNKNOWN

        if 50 <= percent < 60:
            return SportZone.ZONE_1
        elif 60 <= percent < 70:
            return SportZone.ZONE_2
        elif 70 <= percent < 80:
            return SportZone.ZONE_3
        elif 80 <= percent < 90:
            return SportZone.ZONE_4
        elif 90 <= percent <= 100:
            return SportZone.ZONE_5
        else:
            return SportZone.ZONE_UNKNOWN

    @staticmethod
    def from_age_and_hr(age: int, heart_rate: float) -> SportZone:
        """
        Convenience method: calculates percentage and returns zone.
        """
        percent = SportZone.percent_from_age(age, heart_rate)
        return SportZone.from_hr_percent(percent)

    def to_tuple(self) -> tuple[str, str]:
        """
        Returns (formatted_zone_name, zone_value)
        Example: ("ZONE 3", "Moderate")
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


class SensorModel(BaseModel):
    device_id: int
    device_type: int
    name: str


class MetricsModel(BaseModel):
    power: Optional[float] = None
    speed: Optional[float] = None
    cadence: Optional[float] = None
    distance: Optional[float] = None
    heart_rate: Optional[int] = None
    heart_rate_percent: Optional[float] = None
    zone_name: Optional[str] = None
    zone_value: Optional[str] = None
    is_running: Optional[bool] = None
