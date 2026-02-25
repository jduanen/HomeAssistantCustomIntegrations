"""Sensor platform for ADSB Tracker."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import Entity

async def async_setup_entry(hass, config_entry, async_add_entities):
    # Entities managed dynamically in coordinator
    pass
