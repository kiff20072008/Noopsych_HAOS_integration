"""Constants for the Noopsych Lamp integration."""

DOMAIN = "noopsych_lamp"

DEFAULT_PORT = 8266

CHANNEL_NAMES = [
    "Channel 1",
    "Channel 2",
    "Channel 3",
    "Channel 4",
    "Channel 5",
    "Channel 6",
]

CMD_TEMPLATE = "aaa510{payload}{checksum}bb"
PAYLOAD_SET_MANUAL_MODE = "0400"
PAYLOAD_SET_AUTO_MODE = "0401"
PAYLOAD_APPLY_CHANNELS_TPL = "05{channels}"