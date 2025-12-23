"""
Configuration loader for Strava to Notion field mappings.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Optional, Any


class ConfigLoader:
    """Loads and manages configuration from config.yml file."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the config loader.

        Args:
            config_path: Path to config.yml file (defaults to ../config.yml)
        """
        if config_path is None:
            # Default to config.yml in the project root
            config_path = Path(__file__).parent.parent / "config.yml"

        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Please create a config.yml file in the project root."
            )

        with open(self.config_path, 'r') as f:
            self._config = yaml.safe_load(f) or {}

    def get_common_fields(self) -> Dict[str, str]:
        """
        Get common field mappings (fields that apply to all activity types).

        Returns:
            Dictionary mapping Strava field names to Notion field names
        """
        common = self._config.get("common_fields", {})
        # Filter out False values and None values
        return {k: v for k, v in common.items() if v}

    def get_sport_fields(self, sport_type: str) -> Dict[str, str]:
        """
        Get sport-specific field mappings.

        Args:
            sport_type: Sport type (Run, Bike, Swim)

        Returns:
            Dictionary mapping Strava field names to Notion field names
        """
        sport_key = f"{sport_type.lower()}_fields"
        sport_fields = self._config.get(sport_key, {})
        # Filter out False values and None values
        return {k: v for k, v in sport_fields.items() if v}

    def get_sport_icon(self, sport_type: str) -> Optional[str]:
        """
        Get emoji icon for a sport type.

        Args:
            sport_type: Sport type (Run, Bike, Swim)

        Returns:
            Emoji character string or None
        """
        icons = self._config.get("sport_icons", {})
        return icons.get(sport_type)

    def is_field_enabled(self, field_name: str, sport_type: Optional[str] = None) -> bool:
        """
        Check if a field is enabled in the configuration.

        Args:
            field_name: Strava field name
            sport_type: Optional sport type (for sport-specific fields)

        Returns:
            True if field is enabled, False otherwise
        """
        # Check common fields
        common = self._config.get("common_fields", {})
        if field_name in common:
            return bool(common[field_name])

        # Check sport-specific fields
        if sport_type:
            sport_key = f"{sport_type.lower()}_fields"
            sport_fields = self._config.get(sport_key, {})
            if field_name in sport_fields:
                return bool(sport_fields[field_name])

        return False

    def get_notion_field_name(self, strava_field: str, sport_type: Optional[str] = None) -> Optional[str]:
        """
        Get the Notion field name for a given Strava field.

        Args:
            strava_field: Strava field name
            sport_type: Optional sport type (for sport-specific fields)

        Returns:
            Notion field name or None if not mapped/disabled
        """
        # Check common fields first
        common = self._config.get("common_fields", {})
        if strava_field in common and common[strava_field]:
            return common[strava_field]

        # Check sport-specific fields
        if sport_type:
            sport_key = f"{sport_type.lower()}_fields"
            sport_fields = self._config.get(sport_key, {})
            if strava_field in sport_fields and sport_fields[strava_field]:
                return sport_fields[strava_field]

        return None

    def get_option(self, option_name: str, default: Any = None) -> Any:
        """
        Get an advanced option value.

        Args:
            option_name: Option name
            default: Default value if option not found

        Returns:
            Option value or default
        """
        options = self._config.get("options", {})
        return options.get(option_name, default)

    def get_distance_divisor(self) -> float:
        """Get the distance unit conversion divisor."""
        return self.get_option("distance_unit_divisor", 1000)

    def get_time_divisor(self) -> float:
        """Get the time unit conversion divisor."""
        return self.get_option("time_unit_divisor", 60)

    def should_include_pace_suffix(self) -> bool:
        """Check if pace suffix (/km) should be included."""
        return self.get_option("include_pace_suffix", True)

    def get_all_config(self) -> Dict[str, Any]:
        """
        Get the entire configuration dictionary.

        Returns:
            Complete configuration dictionary
        """
        return self._config.copy()
