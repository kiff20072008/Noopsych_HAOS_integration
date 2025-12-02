"""API for Noopsych Lamp."""
import socket
import logging
import time
from homeassistant.core import HomeAssistant

from .const import (
    DEFAULT_PORT,
    PAYLOAD_INIT,
    MANUAL_MODE_TEMPLATE,
    PAYLOAD_AUTO_MODE
)

_LOGGER = logging.getLogger(__name__)


class NoopsychLampApi:
    """Class to control the lamp."""

    def __init__(self, hass: HomeAssistant, host: str):
        """Initialize the API."""
        self._hass = hass
        self._host = host
        self._port = DEFAULT_PORT

    def _execute_full_session(self, command_payload: bytes):
        """
        Execute a full TCP session: connect, init, send command, disconnect.
        This mimics the exact behavior of the successful Scapy script.
        """
        _LOGGER.debug(f"Starting full session with {self._host}:{self._port}")
        return
        s = None
        try:
            # Создаем сокет
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)

            # ВАЖНО: Отключаем алгоритм Нейгла. Это заставит ОС отправлять
            # маленькие пакеты немедленно, не дожидаясь и не группируя их.
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

            # Шаг 1: Подключение (SYN -> SYN, ACK -> ACK)
            s.connect((self._host, self._port))
            _LOGGER.debug("Socket connected.")

            # Шаг 2: Отправка пакета инициализации
            init_bytes = bytes.fromhex(PAYLOAD_INIT)
            _LOGGER.debug(f"Sending INIT payload: {init_bytes.hex()}")
            s.sendall(init_bytes)

            # Шаг 3: Получение ответа от сервера
            # Это заставит наш TCP стек отправить пустой ACK в ответ
            response = s.recv(1024)
            _LOGGER.debug(f"Received response after INIT: {response.hex()}")

            # Небольшая пауза, чтобы дать стеку TCP гарантированно отправить ACK
            # перед отправкой следующих данных. Иногда это помогает.
            time.sleep(0.05)

            # Шаг 4: Отправка основной команды
            _LOGGER.debug(f"Sending COMMAND payload: {command_payload.hex()}")
            s.sendall(command_payload)

            # Шаг 5: Получение финального ответа
            final_response = s.recv(1024)
            _LOGGER.debug(f"Received final response: {final_response.hex()}")

        except socket.timeout:
            _LOGGER.error(f"Timeout communicating with lamp at {self._host}")
            #raise ConnectionError("Timeout communicating with lamp")
        except Exception as e:
            _LOGGER.error(f"Error communicating with lamp: {e}")
            #raise ConnectionError(f"Failed to communicate with lamp: {e}")
        finally:
            if s:
                # Шаг 6: Закрытие соединения (FIN -> FIN, ACK -> ACK)
                s.close()
                _LOGGER.debug("Socket closed.")

    async def set_manual_channels(self, channel_values: list[int]):
        """Build and send a command to set manual channel levels."""
        if len(channel_values) != 6:
            _LOGGER.error(f"Invalid channel values provided: {channel_values}")
            return

        # Преобразуем каждое значение (0-100) в HEX-строку из 2 символов (00-64)
        # f'{v:02x}' -> 100 станет '64', а 5 станет '05'
        channels_hex = "".join([f'{v:02x}' for v in channel_values])

        # Подставляем HEX-строку в наш шаблон
        payload_str = MANUAL_MODE_TEMPLATE.format(channels=channels_hex)

        payload = bytes.fromhex(payload_str)
        await self._hass.async_add_executor_job(self._execute_full_session, payload)

    async def set_auto_mode(self):
        """Switch the lamp to automatic mode."""
        payload = bytes.fromhex(PAYLOAD_AUTO_MODE)
        await self._hass.async_add_executor_job(self._execute_full_session, payload)