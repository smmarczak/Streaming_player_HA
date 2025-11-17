"""Constants for the Streaming Player integration."""
from typing import Final

DOMAIN: Final = "streaming_player"

# Configuration keys
CONF_STREAM_URL: Final = "stream_url"
CONF_SAMSUNG_TV_IP: Final = "samsung_tv_ip"
CONF_SAMSUNG_TV_NAME: Final = "samsung_tv_name"
CONF_USE_SELENIUM: Final = "use_selenium"
CONF_POPUP_SELECTORS: Final = "popup_selectors"
CONF_VIDEO_SELECTORS: Final = "video_selectors"

# Default values
DEFAULT_NAME: Final = "Streaming Player"
DEFAULT_USE_SELENIUM: Final = True
DEFAULT_POPUP_SELECTORS: Final = [
    "button[class*='close']",
    "div[class*='popup'] button",
    "a[class*='close']",
    "[id*='close']",
    ".modal-close",
    ".popup-close",
    "[aria-label*='close' i]"
]
DEFAULT_VIDEO_SELECTORS: Final = [
    "video",
    "iframe[src*='player']",
    "iframe[src*='embed']",
    "[class*='player']",
    "[id*='player']"
]

# Service names
SERVICE_PLAY_STREAM: Final = "play_stream"
SERVICE_STOP_STREAM: Final = "stop_stream"

# Attributes
ATTR_STREAM_URL: Final = "stream_url"
ATTR_VIDEO_URL: Final = "video_url"
ATTR_STATUS: Final = "status"
