"""Select entity for Streaming Player integration."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import DOMAIN, CONF_DEFAULT_MEDIA_PLAYER

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select entity."""
    config = hass.data[DOMAIN][config_entry.entry_id]

    select = MediaPlayerSelect(
        hass,
        config_entry,
        config.get(CONF_DEFAULT_MEDIA_PLAYER, ""),
    )

    async_add_entities([select], True)


class MediaPlayerSelect(SelectEntity):
    """Select entity for choosing target media player."""

    _attr_has_entity_name = True
    _attr_name = "Target Media Player"
    _attr_icon = "mdi:speaker"

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        default_player: str,
    ) -> None:
        """Initialize the select entity."""
        self.hass = hass
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_target_media_player"
        self._attr_current_option = default_player if default_player else None
        self._attr_options = []

    async def async_added_to_hass(self) -> None:
        """Run when entity is added to hass."""
        await super().async_added_to_hass()

        # Update options list
        self._update_options()

        # Track media player changes to update options
        @callback
        def _async_update_options(event) -> None:
            self._update_options()
            self.async_write_ha_state()

        # Listen for new media players being added
        self.async_on_remove(
            self.hass.bus.async_listen(
                "state_changed",
                _async_update_options,
            )
        )

    @callback
    def _update_options(self) -> None:
        """Update the list of available media players."""
        media_players = []

        for state in self.hass.states.async_all("media_player"):
            # Skip our own media player
            if "streaming_player" in state.entity_id:
                continue

            # Get friendly name
            friendly_name = state.attributes.get("friendly_name", state.entity_id)
            media_players.append(state.entity_id)

        self._attr_options = sorted(media_players)

        # Ensure current option is valid
        if self._attr_current_option and self._attr_current_option not in self._attr_options:
            if self._attr_options:
                self._attr_current_option = self._attr_options[0]
            else:
                self._attr_current_option = None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        self._attr_current_option = option
        self.async_write_ha_state()

        # Store in hass.data for the media player to access
        if DOMAIN in self.hass.data and self._config_entry.entry_id in self.hass.data[DOMAIN]:
            self.hass.data[DOMAIN][self._config_entry.entry_id]["selected_media_player"] = option

        _LOGGER.info("Target media player changed to: %s", option)

    @property
    def current_option(self) -> str | None:
        """Return the current option."""
        return self._attr_current_option
