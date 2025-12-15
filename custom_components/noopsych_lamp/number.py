"""Number platform for Noopsych Lamp."""
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, CHANNEL_NAMES
from .api import NoopsychLampApi

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
    if entry.entry_id not in CHANNEL_STORAGE:
        CHANNEL_STORAGE[entry.entry_id] = [100] * 6

    switch_entity_id = f"switch.{DOMAIN}_manual_mode"

    entities = [
        NoopsychLampChannelNumber(api, entry, channel_index, switch_entity_id)
        for channel_index in range(len(CHANNEL_NAMES))
    ]
    async_add_entities(entities)


class NoopsychLampChannelNumber(NumberEntity):
    """Representation of a channel slider."""

    def __init__(self, api: NoopsychLampApi, entry: ConfigEntry, channel_index: int, switch_entity_id: str):
        """Initialize the number entity."""
        self._api = api
        self._entry = entry
        self._channel_index = channel_index
        self._switch_entity_id = switch_entity_id # Сохраняем ID переключателя
        self._attr_available = True

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
            name=f"Noopsych Lamp ({self._entry.data['host']})",
            manufacturer="Unknown",
            model="TCP Controlled Noopsych Lamp"
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

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()

        # Получаем текущее состояние переключателя при запуске
        switch_state = self.hass.states.get(self._switch_entity_id)
        if switch_state:
        #    self._attr_available = switch_state.state == "on"
            self.async_write_ha_state()
        self._attr_available = True

        # Регистрируем "слушателя", который будет вызывать self._handle_switch_state_change
        # каждый раз, когда состояние переключателя меняется.
        self.async_on_remove(
            async_track_state_change_event(
                self.hass, [self._switch_entity_id], self._handle_switch_state_change
            )
        )

    @callback
    def _handle_switch_state_change(self, event) -> None:
        """Handle the switch state changes."""
        # event.data.get("new_state") может быть None, если сущность удаляется
        new_state = event.data.get("new_state")
        if new_state:
            self._attr_available = new_state.state == "on"
            self.async_write_ha_state()