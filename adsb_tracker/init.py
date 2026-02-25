"""ADSB Tracker integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN, SCAN_INTERVAL
import asyncio
from aiohttp import ClientSession

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = AdsbCoordinator(hass, entry)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

class AdsbCoordinator:
    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        self._aircraft_entities = {}
  
    async def poll_aircraft(self):
        """Poll ADS-B server and manage entities."""
        host = self.entry.data["host"]
        url = f"http://{host}:{self.entry.data.get('port', 8080)}{self.entry.data.get('path', '/aircraft.json')}"

        async with ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                aircraft_list = data.get("aircraft", [])

        # Track current hex IDs
        current_hexes = {ac.get("hex") for ac in aircraft_list if ac.get("hex")}

        # Remove stale entities
        stale = set(self._aircraft_entities) - current_hexes
        for hex_id in stale:
            entity_id = f"sensor.adsb_{hex_id}"
            await self.hass.services.async_call(
                "homeassistant", "remove_entity", {"entity_id": entity_id}
            )
            del self._aircraft_entities[hex_id]

        # Update/create entities
        for aircraft in aircraft_list:
            hex_id = aircraft.get("hex")
            if not hex_id:
                continue

            entity_id = f"sensor.adsb_{hex_id}"
            self._aircraft_entities[hex_id] = aircraft

            # Update state via hass.states.set (fake state) or emit event
            state_data = {
                "state": aircraft.get("alt_baro", "unknown"),
                "attributes": {
                    "flight": aircraft.get("flight", "N/A"),
                    "speed": aircraft.get("gs", 0),
                    "lat": aircraft.get("lat"),
                    "lon": aircraft.get("lon"),
                    "track": aircraft.get("track"),
                    "friendly_name": f"ADSB {aircraft.get('flight', hex_id)}"
                }
            }
            self.hass.states.async_set(entity_id, state_data["state"], state_data["attributes"])

        # Schedule next poll
        asyncio.create_task(asyncio.sleep(SCAN_INTERVAL).then(lambda: self.poll_aircraft()))
