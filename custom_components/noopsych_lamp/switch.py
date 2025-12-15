"""Switch platform for Noopsych Lamp."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import generate_entity_id

from .const import DOMAIN
from .api import NoopsychLampApi
from .number import CHANNEL_STORAGE # Импортируем наше хранилище

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    api = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NoopsychLampSwitch(api, entry)])

class NoopsychLampSwitch(SwitchEntity):
    """Representation of a Noopsych Lamp switch."""

    def __init__(self, api: NoopsychLampApi, entry: ConfigEntry):
        """Initialize the switch."""
        self._api = api
        self._entry = entry
        self._attr_is_on = False  # Мы не можем узнать состояние, поэтому начинаем с "выключено"
        self._attr_name = "Lamp Manual Mode"
        self._attr_unique_id = f"{entry.unique_id}-manual-mode"
        self.entity_id = f"switch.{DOMAIN}_manual_mode"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.unique_id)},
            name=f"Noopsych Lamp ({self._entry.data['host']})",
            manufacturer="Unknown",
            model="TCP Controlled Noopsych Lamp"
        )

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the entity on (set to manual mode with current slider values)."""
        # Берем текущие значения из хранилища
        await self._api.set_manual_mode()
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the entity off (set to auto mode)."""
        await self._api.set_auto_mode()
        self._attr_is_on = False
        self.async_write_ha_state()