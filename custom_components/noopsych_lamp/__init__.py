"""The Smart TCP Lamp integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, Platform

from .const import DOMAIN
from .api import SmartLampTcpApi

PLATFORMS = [Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Smart TCP Lamp from a config entry."""
    host = entry.data[CONF_HOST]

    # Создаем экземпляр API для общения с лампой
    api = SmartLampTcpApi(hass, host)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = api

    # Перенаправляем настройку на платформу switch
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok