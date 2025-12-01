"""Number platform for Smart TCP Lamp."""
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, CHANNEL_NAMES
from .api import SmartLampTcpApi

# Хранилище для текущих значений каналов, чтобы не запрашивать их постоянно
# Ключ - ID записи конфигурации, значение - список из 6 значений
CHANNEL_STORAGE = {}


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    api = hass.data[DOMAIN][entry.entry_id]

    # Инициализируем хранилище со значениями по умолчанию (например, 100)
    CHANNEL_STORAGE[entry.entry_id] = [100] * 6

    entities = [
        SmartLampChannelNumber(api, entry, channel_index)
        for channel_index in range(len(CHANNEL_NAMES))
    ]
    async_add_entities(entities)


class SmartLampChannelNumber(NumberEntity):
    """Representation of a channel slider."""

    def __init__(self, api: SmartLampTcpApi, entry: ConfigEntry, channel_index: int):
        """Initialize the number entity."""
        self._api = api
        self._entry = entry
        self._channel_index = channel_index

        self._attr_name = CHANNEL_NAMES[channel_index]
        self._attr_unique_id = f"{entry.unique_id}_channel_{channel_index}"

        # Настройки слайдера
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_mode = NumberMode.SLIDER  # Отображать как слайдер

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information to link the entity to the device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.unique_id)},
            name=f"Smart Lamp ({self._entry.data['host']})",
            manufacturer="Unknown",
            model="TCP Controlled Lamp"
        )

    @property
    def native_value(self) -> float:
        """Return the current value."""
        return CHANNEL_STORAGE[self._entry.entry_id][self._channel_index]

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        new_value = int(value)

        # Обновляем значение в нашем временном хранилище
        stored_values = CHANNEL_STORAGE[self._entry.entry_id]
        stored_values[self._channel_index] = new_value

        # Отправляем команду на лампу со ВСЕМИ 6 значениями
        await self._api.set_manual_channels(stored_values)

        # Обновляем состояние этого слайдера в HA
        self.async_write_ha_state()