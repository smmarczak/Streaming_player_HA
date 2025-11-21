"""Media Player platform for Streaming Player integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
    async_get_current_platform,
)
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_STREAM_URL,
    CONF_SAMSUNG_TV_IP,
    CONF_SAMSUNG_TV_NAME,
    CONF_USE_SELENIUM,
    CONF_EXTRACTION_METHOD,
    CONF_POPUP_SELECTORS,
    CONF_VIDEO_SELECTORS,
    CONF_NAVIDROME_URL,
    CONF_NAVIDROME_USERNAME,
    CONF_NAVIDROME_PASSWORD,
    DEFAULT_POPUP_SELECTORS,
    DEFAULT_VIDEO_SELECTORS,
    DEFAULT_EXTRACTION_METHOD,
    EXTRACTION_YTDLP,
    EXTRACTION_SELENIUM,
    EXTRACTION_AIOHTTP,
    SERVICE_PLAY_STREAM,
    SERVICE_STOP_STREAM,
    SERVICE_CLICK_ELEMENT,
    SERVICE_NAVIGATE_URL,
    SERVICE_SCROLL_PAGE,
    SERVICE_EXECUTE_SCRIPT,
    SERVICE_WAIT_FOR_ELEMENT,
    SERVICE_GET_PAGE_SOURCE,
    SERVICE_SET_STREAM_URL,
    SERVICE_SET_TV,
    SERVICE_GET_GENRES,
    SERVICE_PLAY_GENRE,
    SERVICE_PLAY_RANDOM,
    SERVICE_PLAY_SONG,
    SERVICE_SEARCH_MUSIC,
    SERVICE_GET_PLAYLISTS,
    SERVICE_PLAY_PLAYLIST,
    ATTR_SELECTOR,
    ATTR_URL,
    ATTR_SCRIPT,
    ATTR_DIRECTION,
    ATTR_TIMEOUT,
    ATTR_STREAM_URL,
    ATTR_TV_IP,
    ATTR_TV_NAME,
    ATTR_GENRE,
    ATTR_SONG_ID,
    ATTR_PLAYLIST_ID,
    ATTR_QUERY,
    ATTR_COUNT,
    ATTR_SHUFFLE,
    ATTR_CAST_TARGET,
)
from .video_scraper import VideoScraper
from .browser_controller import BrowserController
from .ytdlp_extractor import YtdlpExtractor
from .subsonic_client import SubsonicClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Streaming Player media player platform."""
    config = hass.data[DOMAIN][config_entry.entry_id]

    player = StreamingMediaPlayer(
        hass,
        config[CONF_NAME],
        config[CONF_STREAM_URL],
        config[CONF_SAMSUNG_TV_IP],
        config.get(CONF_SAMSUNG_TV_NAME, "Samsung TV"),
        config.get(CONF_EXTRACTION_METHOD, DEFAULT_EXTRACTION_METHOD),
        config.get(CONF_POPUP_SELECTORS, DEFAULT_POPUP_SELECTORS),
        config.get(CONF_VIDEO_SELECTORS, DEFAULT_VIDEO_SELECTORS),
        config.get(CONF_NAVIDROME_URL, ""),
        config.get(CONF_NAVIDROME_USERNAME, ""),
        config.get(CONF_NAVIDROME_PASSWORD, ""),
    )

    async_add_entities([player], True)

    # Register navigation services
    platform = async_get_current_platform()

    platform.async_register_entity_service(
        SERVICE_CLICK_ELEMENT,
        {
            vol.Required(ATTR_SELECTOR): cv.string,
            vol.Optional(ATTR_TIMEOUT, default=10): cv.positive_int,
        },
        "async_click_element",
    )

    platform.async_register_entity_service(
        SERVICE_NAVIGATE_URL,
        {vol.Required(ATTR_URL): cv.string},
        "async_navigate_url",
    )

    platform.async_register_entity_service(
        SERVICE_SCROLL_PAGE,
        {
            vol.Optional(ATTR_DIRECTION, default="down"): cv.string,
        },
        "async_scroll_page",
    )

    platform.async_register_entity_service(
        SERVICE_EXECUTE_SCRIPT,
        {vol.Required(ATTR_SCRIPT): cv.string},
        "async_execute_script",
    )

    platform.async_register_entity_service(
        SERVICE_WAIT_FOR_ELEMENT,
        {
            vol.Required(ATTR_SELECTOR): cv.string,
            vol.Optional(ATTR_TIMEOUT, default=10): cv.positive_int,
        },
        "async_wait_for_element",
    )

    platform.async_register_entity_service(
        SERVICE_GET_PAGE_SOURCE,
        {},
        "async_get_page_source",
    )

    platform.async_register_entity_service(
        SERVICE_SET_STREAM_URL,
        {vol.Required(ATTR_STREAM_URL): cv.string},
        "async_set_stream_url",
    )

    platform.async_register_entity_service(
        SERVICE_SET_TV,
        {
            vol.Required(ATTR_TV_IP): cv.string,
            vol.Optional(ATTR_TV_NAME): cv.string,
        },
        "async_set_tv",
    )

    # Music services
    platform.async_register_entity_service(
        SERVICE_GET_GENRES,
        {},
        "async_get_genres",
    )

    platform.async_register_entity_service(
        SERVICE_PLAY_GENRE,
        {
            vol.Required(ATTR_GENRE): cv.string,
            vol.Optional(ATTR_COUNT, default=20): cv.positive_int,
            vol.Optional(ATTR_SHUFFLE, default=True): cv.boolean,
            vol.Optional(ATTR_CAST_TARGET): cv.string,
        },
        "async_play_genre",
    )

    platform.async_register_entity_service(
        SERVICE_PLAY_RANDOM,
        {
            vol.Optional(ATTR_COUNT, default=20): cv.positive_int,
            vol.Optional(ATTR_GENRE): cv.string,
            vol.Optional(ATTR_CAST_TARGET): cv.string,
        },
        "async_play_random",
    )

    platform.async_register_entity_service(
        SERVICE_PLAY_SONG,
        {
            vol.Required(ATTR_SONG_ID): cv.string,
            vol.Optional(ATTR_CAST_TARGET): cv.string,
        },
        "async_play_song",
    )

    platform.async_register_entity_service(
        SERVICE_SEARCH_MUSIC,
        {vol.Required(ATTR_QUERY): cv.string},
        "async_search_music",
    )

    platform.async_register_entity_service(
        SERVICE_GET_PLAYLISTS,
        {},
        "async_get_playlists",
    )

    platform.async_register_entity_service(
        SERVICE_PLAY_PLAYLIST,
        {
            vol.Required(ATTR_PLAYLIST_ID): cv.string,
            vol.Optional(ATTR_SHUFFLE, default=False): cv.boolean,
            vol.Optional(ATTR_CAST_TARGET): cv.string,
        },
        "async_play_playlist",
    )


class StreamingMediaPlayer(MediaPlayerEntity):
    """Representation of a Streaming Media Player."""

    _attr_has_entity_name = True
    _attr_supported_features = (
        MediaPlayerEntityFeature.PLAY
        | MediaPlayerEntityFeature.STOP
        | MediaPlayerEntityFeature.PLAY_MEDIA
    )

    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        stream_url: str,
        samsung_tv_ip: str,
        samsung_tv_name: str,
        extraction_method: str,
        popup_selectors: list[str],
        video_selectors: list[str],
        navidrome_url: str = "",
        navidrome_username: str = "",
        navidrome_password: str = "",
    ) -> None:
        """Initialize the media player."""
        self.hass = hass
        self._attr_name = name
        self._stream_url = stream_url
        self._samsung_tv_ip = samsung_tv_ip
        self._samsung_tv_name = samsung_tv_name
        self._extraction_method = extraction_method
        self._popup_selectors = popup_selectors
        self._video_selectors = video_selectors

        # Navidrome configuration
        self._navidrome_url = navidrome_url
        self._navidrome_username = navidrome_username
        self._navidrome_password = navidrome_password
        self._subsonic_client: SubsonicClient | None = None

        self._attr_state = MediaPlayerState.IDLE
        self._video_url: str | None = None
        self._scraper: VideoScraper | None = None
        self._cast_device = None
        self._browser: BrowserController | None = None
        self._current_page_url: str | None = None

        # Music state
        self._current_song: dict | None = None
        self._available_genres: list[str] = []

        # Generate unique ID
        self._attr_unique_id = f"streaming_player_{samsung_tv_ip}_{stream_url}"

    @property
    def state(self) -> MediaPlayerState:
        """Return the state of the player."""
        return self._attr_state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = {
            "stream_url": self._stream_url,
            "video_url": self._video_url,
            "samsung_tv_ip": self._samsung_tv_ip,
            "samsung_tv_name": self._samsung_tv_name,
            "extraction_method": self._extraction_method,
            "current_page_url": self._current_page_url,
            "browser_active": self._browser is not None,
            "navidrome_configured": bool(self._navidrome_url),
            "available_genres": self._available_genres,
        }
        if self._current_song:
            attrs["current_song"] = self._current_song.get("title", "")
            attrs["current_artist"] = self._current_song.get("artist", "")
            attrs["current_album"] = self._current_song.get("album", "")
        return attrs

    async def async_play_media(
        self, media_type: str, media_id: str, **kwargs: Any
    ) -> None:
        """Play media."""
        _LOGGER.info("Playing media: %s", media_id)
        await self._play_stream(media_id)

    async def async_media_play(self) -> None:
        """Send play command."""
        _LOGGER.info("Play command received")
        await self._play_stream(self._stream_url)

    async def async_media_stop(self) -> None:
        """Send stop command."""
        _LOGGER.info("Stop command received")
        await self._stop_stream()

    async def _play_stream(self, url: str | None = None) -> None:
        """Play stream on Samsung TV."""
        try:
            self._attr_state = MediaPlayerState.PLAYING
            self.async_write_ha_state()

            stream_url = url or self._stream_url

            # Extract video URL based on configured method
            _LOGGER.info(
                "Extracting video URL from: %s (method: %s)",
                stream_url,
                self._extraction_method
            )

            if self._extraction_method == EXTRACTION_YTDLP:
                # Use yt-dlp (recommended)
                extractor = YtdlpExtractor(stream_url)
                self._video_url = await extractor.get_video_url()
            elif self._extraction_method == EXTRACTION_SELENIUM:
                # Use Selenium-based scraper
                self._scraper = VideoScraper(
                    stream_url,
                    self._popup_selectors,
                    self._video_selectors,
                    use_selenium=True,
                )
                self._video_url = await self._scraper.get_video_url()
            else:
                # Use aiohttp-based scraper (basic)
                self._scraper = VideoScraper(
                    stream_url,
                    self._popup_selectors,
                    self._video_selectors,
                    use_selenium=False,
                )
                self._video_url = await self._scraper.get_video_url()

            if not self._video_url:
                _LOGGER.error("Failed to extract video URL")
                self._attr_state = MediaPlayerState.IDLE
                self.async_write_ha_state()
                return

            _LOGGER.info("Extracted video URL: %s", self._video_url)

            # Cast to Samsung TV
            await self._cast_to_samsung_tv(self._video_url)

        except Exception as e:
            _LOGGER.error("Error playing stream: %s", e)
            self._attr_state = MediaPlayerState.IDLE
            self.async_write_ha_state()

    async def _cast_to_samsung_tv(self, video_url: str) -> None:
        """Cast video to Samsung TV using pychromecast or direct DLNA."""
        try:
            # First, try using pychromecast if Samsung TV supports Chromecast
            try:
                import pychromecast

                _LOGGER.info("Attempting to cast via Chromecast protocol")

                # Discover Chromecasts
                chromecasts, browser = pychromecast.get_listed_chromecasts(
                    friendly_names=[self._samsung_tv_name]
                )

                if not chromecasts:
                    _LOGGER.warning("No Chromecast device found, trying by IP")
                    # Try to connect directly by IP
                    try:
                        cast = pychromecast.Chromecast(self._samsung_tv_ip)
                        cast.wait()
                        chromecasts = [cast]
                    except Exception as e:
                        _LOGGER.error("Failed to connect to Chromecast by IP: %s", e)
                        chromecasts = []

                if chromecasts:
                    cast = chromecasts[0]
                    cast.wait()

                    mc = cast.media_controller
                    mc.play_media(video_url, "video/mp4")
                    mc.block_until_active()

                    _LOGGER.info("Successfully cast to Samsung TV via Chromecast")
                    self._cast_device = cast
                    return

            except ImportError:
                _LOGGER.info("pychromecast not available")
            except Exception as e:
                _LOGGER.warning("Chromecast method failed: %s", e)

            # Fallback: Try Samsung TV API (samsungctl or websocket)
            _LOGGER.info("Attempting Samsung TV direct control")
            await self._samsung_tv_direct_control(video_url)

        except Exception as e:
            _LOGGER.error("Error casting to Samsung TV: %s", e)
            raise

    async def _samsung_tv_direct_control(self, video_url: str) -> None:
        """Control Samsung TV directly using websocket or REST API."""
        try:
            # Samsung TVs can be controlled via their REST API or WebSocket
            # This is a simplified implementation - you may need to adjust based on your TV model

            import aiohttp
            import json

            # Try to open browser on Samsung TV with video URL
            # This requires the Samsung TV to have a browser app

            # Method 1: Use Samsung SmartThings API (requires setup)
            # Method 2: Use Samsung TV REST API (varies by model)
            # Method 3: Send DLNA play command

            _LOGGER.info(
                "Samsung TV direct control not fully implemented. "
                "Please use Chromecast or configure SmartThings integration."
            )

            # For now, log the video URL so users can manually play it
            _LOGGER.info("Video URL to play: %s", video_url)
            _LOGGER.info(
                "To enable casting, either:\n"
                "1. Ensure your Samsung TV has Chromecast built-in enabled\n"
                "2. Install the Samsung SmartThings integration in Home Assistant\n"
                "3. Use DLNA-compatible apps"
            )

            # Store the URL for the user to access
            self._video_url = video_url
            self.async_write_ha_state()

        except Exception as e:
            _LOGGER.error("Samsung TV direct control error: %s", e)
            raise

    async def _stop_stream(self) -> None:
        """Stop the current stream."""
        try:
            if self._cast_device:
                mc = self._cast_device.media_controller
                mc.stop()
                _LOGGER.info("Stopped casting to Samsung TV")

            self._attr_state = MediaPlayerState.IDLE
            self._video_url = None

            if self._scraper:
                await self._scraper.close()
                self._scraper = None

            self.async_write_ha_state()

        except Exception as e:
            _LOGGER.error("Error stopping stream: %s", e)

    async def async_navigate_url(self, url: str) -> None:
        """Navigate to a URL in the browser."""
        _LOGGER.info("Navigating to URL: %s", url)

        if not self._browser:
            self._browser = BrowserController(self._use_selenium)
            await self._browser.initialize()

        success = await self._browser.navigate(url)
        if success:
            self._current_page_url = await self._browser.get_current_url()
            self.async_write_ha_state()

    async def async_click_element(self, selector: str, timeout: int = 10) -> None:
        """Click an element on the current page."""
        _LOGGER.info("Clicking element: %s", selector)

        if not self._browser:
            _LOGGER.error("Browser not initialized. Navigate to a URL first.")
            return

        success = await self._browser.click_element(selector, timeout)
        if success:
            self._current_page_url = await self._browser.get_current_url()
            self.async_write_ha_state()

    async def async_scroll_page(self, direction: str = "down") -> None:
        """Scroll the page in the specified direction."""
        _LOGGER.info("Scrolling page: %s", direction)

        if not self._browser:
            _LOGGER.error("Browser not initialized. Navigate to a URL first.")
            return

        await self._browser.scroll_page(direction)

    async def async_execute_script(self, script: str) -> None:
        """Execute JavaScript on the current page."""
        _LOGGER.info("Executing script")

        if not self._browser:
            _LOGGER.error("Browser not initialized. Navigate to a URL first.")
            return

        result = await self._browser.execute_script(script)
        _LOGGER.info("Script result: %s", result)

    async def async_wait_for_element(self, selector: str, timeout: int = 10) -> None:
        """Wait for an element to appear on the page."""
        _LOGGER.info("Waiting for element: %s", selector)

        if not self._browser:
            _LOGGER.error("Browser not initialized. Navigate to a URL first.")
            return

        await self._browser.wait_for_element(selector, timeout)

    async def async_get_page_source(self) -> None:
        """Get the current page source and log it."""
        _LOGGER.info("Getting page source")

        if not self._browser:
            _LOGGER.error("Browser not initialized. Navigate to a URL first.")
            return

        source = await self._browser.get_page_source()
        if source:
            _LOGGER.info("Page source length: %d characters", len(source))
            # Log a preview of available elements
            elements = await self._browser.get_elements("a, button, video, iframe")
            _LOGGER.info("Found %d interactive elements on page", len(elements))
            for i, elem in enumerate(elements[:10]):  # Log first 10 elements
                _LOGGER.info("Element %d: %s", i + 1, elem)

    async def async_set_stream_url(self, stream_url: str) -> None:
        """Set a new stream URL."""
        _LOGGER.info("Setting new stream URL: %s", stream_url)
        self._stream_url = stream_url
        self.async_write_ha_state()

    async def async_set_tv(self, tv_ip: str, tv_name: str | None = None) -> None:
        """Set a new Samsung TV target."""
        _LOGGER.info("Setting new TV: %s (%s)", tv_ip, tv_name or "Samsung TV")
        self._samsung_tv_ip = tv_ip
        if tv_name:
            self._samsung_tv_name = tv_name

        # Close existing cast device connection
        if self._cast_device:
            try:
                self._cast_device.disconnect()
            except Exception as e:
                _LOGGER.warning("Error disconnecting from old TV: %s", e)
            finally:
                self._cast_device = None

        self.async_write_ha_state()

    async def async_will_remove_from_hass(self) -> None:
        """Clean up when entity is removed."""
        await self._stop_stream()
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._subsonic_client:
            await self._subsonic_client.close()
            self._subsonic_client = None

    # Music service methods

    async def _get_subsonic_client(self) -> SubsonicClient | None:
        """Get or create Subsonic client."""
        if not self._navidrome_url:
            _LOGGER.error("Navidrome not configured")
            return None

        if not self._subsonic_client:
            self._subsonic_client = SubsonicClient(
                self._navidrome_url,
                self._navidrome_username,
                self._navidrome_password,
            )
            # Test connection
            if not await self._subsonic_client.ping():
                _LOGGER.error("Failed to connect to Navidrome")
                self._subsonic_client = None
                return None

        return self._subsonic_client

    async def async_get_genres(self) -> None:
        """Get available music genres from Navidrome."""
        client = await self._get_subsonic_client()
        if not client:
            return

        genres = await client.get_genres()
        self._available_genres = [g.get("value", "") for g in genres if g.get("value")]
        _LOGGER.info("Available genres: %s", self._available_genres)
        self.async_write_ha_state()

    async def async_play_genre(
        self,
        genre: str,
        count: int = 20,
        shuffle: bool = True,
        cast_target: str | None = None,
    ) -> None:
        """Play music from a specific genre."""
        client = await self._get_subsonic_client()
        if not client:
            return

        _LOGGER.info("Playing genre: %s (count=%d, shuffle=%s)", genre, count, shuffle)

        if shuffle:
            songs = await client.get_random_songs(size=count, genre=genre)
        else:
            songs = await client.get_songs_by_genre(genre, count=count)

        if not songs:
            _LOGGER.warning("No songs found for genre: %s", genre)
            return

        # Get first song and cast it
        song = songs[0]
        await self._cast_music(song, cast_target)

    async def async_play_random(
        self,
        count: int = 20,
        genre: str | None = None,
        cast_target: str | None = None,
    ) -> None:
        """Play random music, optionally filtered by genre."""
        client = await self._get_subsonic_client()
        if not client:
            return

        _LOGGER.info("Playing random music (count=%d, genre=%s)", count, genre)

        songs = await client.get_random_songs(size=count, genre=genre)
        if not songs:
            _LOGGER.warning("No songs found")
            return

        song = songs[0]
        await self._cast_music(song, cast_target)

    async def async_play_song(
        self,
        song_id: str,
        cast_target: str | None = None,
    ) -> None:
        """Play a specific song by ID."""
        client = await self._get_subsonic_client()
        if not client:
            return

        _LOGGER.info("Playing song ID: %s", song_id)

        # Create a minimal song dict with the ID
        song = {"id": song_id}
        await self._cast_music(song, cast_target)

    async def async_search_music(self, query: str) -> None:
        """Search for music in Navidrome."""
        client = await self._get_subsonic_client()
        if not client:
            return

        _LOGGER.info("Searching for: %s", query)

        results = await client.search(query)
        artists = results.get("artists", [])
        albums = results.get("albums", [])
        songs = results.get("songs", [])

        _LOGGER.info(
            "Search results - Artists: %d, Albums: %d, Songs: %d",
            len(artists),
            len(albums),
            len(songs),
        )

        # Log first few results
        for artist in artists[:3]:
            _LOGGER.info("Artist: %s (ID: %s)", artist.get("name"), artist.get("id"))
        for album in albums[:3]:
            _LOGGER.info("Album: %s by %s (ID: %s)", album.get("name"), album.get("artist"), album.get("id"))
        for song in songs[:5]:
            _LOGGER.info("Song: %s by %s (ID: %s)", song.get("title"), song.get("artist"), song.get("id"))

    async def async_get_playlists(self) -> None:
        """Get available playlists from Navidrome."""
        client = await self._get_subsonic_client()
        if not client:
            return

        playlists = await client.get_playlists()
        _LOGGER.info("Available playlists:")
        for playlist in playlists:
            _LOGGER.info("  - %s (ID: %s, %d songs)",
                        playlist.get("name"),
                        playlist.get("id"),
                        playlist.get("songCount", 0))

    async def async_play_playlist(
        self,
        playlist_id: str,
        shuffle: bool = False,
        cast_target: str | None = None,
    ) -> None:
        """Play a playlist."""
        client = await self._get_subsonic_client()
        if not client:
            return

        _LOGGER.info("Playing playlist: %s (shuffle=%s)", playlist_id, shuffle)

        songs = await client.get_playlist_songs(playlist_id)
        if not songs:
            _LOGGER.warning("No songs in playlist")
            return

        if shuffle:
            import random
            random.shuffle(songs)

        song = songs[0]
        await self._cast_music(song, cast_target)

    async def _cast_music(self, song: dict, cast_target: str | None = None) -> None:
        """Cast music to a Chromecast device."""
        client = await self._get_subsonic_client()
        if not client:
            return

        self._current_song = song
        song_id = song.get("id")
        stream_url = client.get_stream_url(song_id)

        _LOGGER.info(
            "Casting: %s by %s",
            song.get("title", "Unknown"),
            song.get("artist", "Unknown"),
        )

        try:
            import pychromecast

            self._attr_state = MediaPlayerState.PLAYING
            self.async_write_ha_state()

            # Determine target device
            target_name = cast_target or self._samsung_tv_name
            target_ip = self._samsung_tv_ip

            # Try to find Chromecast by name
            chromecasts, browser = pychromecast.get_listed_chromecasts(
                friendly_names=[target_name]
            )

            if not chromecasts:
                _LOGGER.info("No device found by name '%s', trying IP", target_name)
                try:
                    cast = pychromecast.Chromecast(target_ip)
                    cast.wait()
                    chromecasts = [cast]
                except Exception as e:
                    _LOGGER.error("Failed to connect by IP: %s", e)

            if chromecasts:
                cast = chromecasts[0]
                cast.wait()

                mc = cast.media_controller

                # Get content type based on format
                content_type = "audio/mpeg"  # Default for MP3

                mc.play_media(stream_url, content_type)
                mc.block_until_active()

                _LOGGER.info("Successfully cast music to %s", target_name)
                self._cast_device = cast
            else:
                _LOGGER.error("No Chromecast device found")
                # Still store the URL for manual access
                self._video_url = stream_url
                _LOGGER.info("Music stream URL: %s", stream_url)

        except ImportError:
            _LOGGER.error("pychromecast not available")
            self._video_url = stream_url
        except Exception as e:
            _LOGGER.error("Error casting music: %s", e)
            self._attr_state = MediaPlayerState.IDLE
            self.async_write_ha_state()
