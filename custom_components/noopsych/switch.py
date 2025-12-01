"""Switch platform for Smart TCP Lamp."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .api import SmartLampTcpApi
from .number import CHANNEL_STORAGE # Импортируем наше хранилище

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    api = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SmartLampTCPSwitch(api, entry)])

class SmartLampTCPSwitch(SwitchEntity):
    """Representation of a Smart TCP Lamp switch."""

    def __init__(self, api: SmartLampTcpApi, entry: ConfigEntry):
        """Initialize the switch."""
        self._api = api
        self._entry = entry
        self._attr_is_on = False  # Мы не можем узнать состояние, поэтому начинаем с "выключено"
        self._attr_name = "Lamp Manual Mode"
        self._attr_unique_id = f"{entry.unique_id}-manual-mode"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.unique_id)},
            name=f"Smart Lamp ({self._entry.data['host']})",
            manufacturer="Unknown",
            model="TCP Controlled Lamp"
        )

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the entity on (set to manual mode with current slider values)."""
        # Берем текущие значения из хранилища
        current_channel_values = CHANNEL_STORAGE.get(self._entry.entry_id, [100] * 6)
        await self._api.set_manual_channels(current_channel_values)
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the entity off (set to auto mode)."""
        await self._api.set_auto_mode()
        self._attr_is_on = False
        self.async_write_ha_state()