"""Media Player platform for Streaming Player integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    CONF_STREAM_URL,
    CONF_SAMSUNG_TV_IP,
    CONF_SAMSUNG_TV_NAME,
    CONF_USE_SELENIUM,
    CONF_POPUP_SELECTORS,
    CONF_VIDEO_SELECTORS,
    DEFAULT_POPUP_SELECTORS,
    DEFAULT_VIDEO_SELECTORS,
    SERVICE_PLAY_STREAM,
    SERVICE_STOP_STREAM,
)
from .video_scraper import VideoScraper

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
        config.get(CONF_USE_SELENIUM, True),
        config.get(CONF_POPUP_SELECTORS, DEFAULT_POPUP_SELECTORS),
        config.get(CONF_VIDEO_SELECTORS, DEFAULT_VIDEO_SELECTORS),
    )

    async_add_entities([player], True)


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
        use_selenium: bool,
        popup_selectors: list[str],
        video_selectors: list[str],
    ) -> None:
        """Initialize the media player."""
        self.hass = hass
        self._attr_name = name
        self._stream_url = stream_url
        self._samsung_tv_ip = samsung_tv_ip
        self._samsung_tv_name = samsung_tv_name
        self._use_selenium = use_selenium
        self._popup_selectors = popup_selectors
        self._video_selectors = video_selectors

        self._attr_state = MediaPlayerState.IDLE
        self._video_url: str | None = None
        self._scraper: VideoScraper | None = None
        self._cast_device = None

        # Generate unique ID
        self._attr_unique_id = f"streaming_player_{samsung_tv_ip}_{stream_url}"

    @property
    def state(self) -> MediaPlayerState:
        """Return the state of the player."""
        return self._attr_state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return {
            "stream_url": self._stream_url,
            "video_url": self._video_url,
            "samsung_tv_ip": self._samsung_tv_ip,
            "samsung_tv_name": self._samsung_tv_name,
        }

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

            # Create scraper and extract video URL
            _LOGGER.info("Extracting video URL from: %s", stream_url)
            self._scraper = VideoScraper(
                stream_url,
                self._popup_selectors,
                self._video_selectors,
                self._use_selenium,
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

    async def async_will_remove_from_hass(self) -> None:
        """Clean up when entity is removed."""
        await self._stop_stream()
