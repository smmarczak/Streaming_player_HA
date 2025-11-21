"""Constants for the Streaming Player integration."""
from typing import Final

DOMAIN: Final = "streaming_player"

# Configuration keys
CONF_STREAM_URL: Final = "stream_url"
CONF_SAMSUNG_TV_IP: Final = "samsung_tv_ip"
CONF_SAMSUNG_TV_NAME: Final = "samsung_tv_name"
CONF_USE_SELENIUM: Final = "use_selenium"
CONF_EXTRACTION_METHOD: Final = "extraction_method"
CONF_POPUP_SELECTORS: Final = "popup_selectors"
CONF_VIDEO_SELECTORS: Final = "video_selectors"

# Navidrome/Subsonic configuration
CONF_NAVIDROME_URL: Final = "navidrome_url"
CONF_NAVIDROME_USERNAME: Final = "navidrome_username"
CONF_NAVIDROME_PASSWORD: Final = "navidrome_password"
CONF_DEFAULT_MEDIA_PLAYER: Final = "default_media_player"

# Extraction methods
EXTRACTION_YTDLP: Final = "yt-dlp"
EXTRACTION_SELENIUM: Final = "selenium"
EXTRACTION_AIOHTTP: Final = "aiohttp"

# Default values
DEFAULT_NAME: Final = "Streaming Player"
DEFAULT_USE_SELENIUM: Final = True
DEFAULT_EXTRACTION_METHOD: Final = EXTRACTION_YTDLP
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
SERVICE_CLICK_ELEMENT: Final = "click_element"
SERVICE_NAVIGATE_URL: Final = "navigate_url"
SERVICE_SCROLL_PAGE: Final = "scroll_page"
SERVICE_EXECUTE_SCRIPT: Final = "execute_script"
SERVICE_WAIT_FOR_ELEMENT: Final = "wait_for_element"
SERVICE_GET_PAGE_SOURCE: Final = "get_page_source"
SERVICE_SET_STREAM_URL: Final = "set_stream_url"
SERVICE_SET_TV: Final = "set_tv"

# Music services
SERVICE_GET_GENRES: Final = "get_genres"
SERVICE_PLAY_GENRE: Final = "play_genre"
SERVICE_PLAY_RANDOM: Final = "play_random"
SERVICE_PLAY_SONG: Final = "play_song"
SERVICE_SEARCH_MUSIC: Final = "search_music"
SERVICE_GET_PLAYLISTS: Final = "get_playlists"
SERVICE_PLAY_PLAYLIST: Final = "play_playlist"

# Attributes
ATTR_STREAM_URL: Final = "stream_url"
ATTR_VIDEO_URL: Final = "video_url"
ATTR_STATUS: Final = "status"
ATTR_SELECTOR: Final = "selector"
ATTR_URL: Final = "url"
ATTR_SCRIPT: Final = "script"
ATTR_DIRECTION: Final = "direction"
ATTR_TIMEOUT: Final = "timeout"
ATTR_PAGE_SOURCE: Final = "page_source"
ATTR_TV_IP: Final = "tv_ip"
ATTR_TV_NAME: Final = "tv_name"

# Music attributes
ATTR_GENRE: Final = "genre"
ATTR_SONG_ID: Final = "song_id"
ATTR_PLAYLIST_ID: Final = "playlist_id"
ATTR_QUERY: Final = "query"
ATTR_COUNT: Final = "count"
ATTR_SHUFFLE: Final = "shuffle"
ATTR_CAST_TARGET: Final = "cast_target"
