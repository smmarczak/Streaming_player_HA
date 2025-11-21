"""Config flow for Streaming Player integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_STREAM_URL,
    CONF_SAMSUNG_TV_IP,
    CONF_SAMSUNG_TV_NAME,
    CONF_USE_SELENIUM,
    CONF_EXTRACTION_METHOD,
    CONF_NAVIDROME_URL,
    CONF_NAVIDROME_USERNAME,
    CONF_NAVIDROME_PASSWORD,
    CONF_DEFAULT_MEDIA_PLAYER,
    DEFAULT_NAME,
    DEFAULT_USE_SELENIUM,
    DEFAULT_EXTRACTION_METHOD,
    EXTRACTION_YTDLP,
    EXTRACTION_SELENIUM,
    EXTRACTION_AIOHTTP,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
        vol.Optional(CONF_STREAM_URL, default=""): str,
        vol.Optional(CONF_SAMSUNG_TV_IP, default=""): str,
        vol.Optional(CONF_SAMSUNG_TV_NAME, default="Samsung TV"): str,
        vol.Optional(
            CONF_EXTRACTION_METHOD, default=DEFAULT_EXTRACTION_METHOD
        ): vol.In([EXTRACTION_YTDLP, EXTRACTION_SELENIUM, EXTRACTION_AIOHTTP]),
        vol.Optional(CONF_NAVIDROME_URL, default=""): str,
        vol.Optional(CONF_NAVIDROME_USERNAME, default=""): str,
        vol.Optional(CONF_NAVIDROME_PASSWORD, default=""): str,
        vol.Optional(CONF_DEFAULT_MEDIA_PLAYER, default=""): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # Validate URL format if provided
    stream_url = data.get(CONF_STREAM_URL, "").strip()
    if stream_url and not stream_url.startswith(("http://", "https://")):
        raise ValueError("Invalid URL format")

    # Validate IP address format if provided
    ip = data.get(CONF_SAMSUNG_TV_IP, "").strip()
    if ip:
        parts = ip.split(".")
        if len(parts) != 4:
            raise ValueError("Invalid IP address")

        try:
            for part in parts:
                if not 0 <= int(part) <= 255:
                    raise ValueError("Invalid IP address")
        except ValueError:
            raise ValueError("Invalid IP address")

    # Validate Navidrome URL if provided
    navidrome_url = data.get(CONF_NAVIDROME_URL, "").strip()
    _LOGGER.debug("Validating Navidrome URL: '%s'", navidrome_url)
    if navidrome_url and not navidrome_url.startswith(("http://", "https://")):
        _LOGGER.error("Invalid Navidrome URL - must start with http:// or https://. Got: '%s'", navidrome_url)
        raise ValueError("Invalid Navidrome URL format")

    # Ensure at least one mode is configured
    if not stream_url and not navidrome_url:
        raise ValueError("Please configure either Stream URL or Navidrome URL")

    # Return info that you want to store in the config entry.
    return {"title": data[CONF_NAME]}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Streaming Player."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except ValueError as err:
                _LOGGER.error("Validation error: %s", err)
                errors["base"] = "invalid_url"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Check if already configured
                await self.async_set_unique_id(
                    f"{user_input[CONF_SAMSUNG_TV_IP]}_{user_input[CONF_STREAM_URL]}"
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Streaming Player."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Update the config entry with new data
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={**self.config_entry.data, **user_input},
            )
            return self.async_create_entry(title="", data={})

        # Get current values
        current_data = self.config_entry.data

        options_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_STREAM_URL,
                    default=current_data.get(CONF_STREAM_URL, ""),
                ): str,
                vol.Optional(
                    CONF_SAMSUNG_TV_IP,
                    default=current_data.get(CONF_SAMSUNG_TV_IP, ""),
                ): str,
                vol.Optional(
                    CONF_SAMSUNG_TV_NAME,
                    default=current_data.get(CONF_SAMSUNG_TV_NAME, "Samsung TV"),
                ): str,
                vol.Optional(
                    CONF_EXTRACTION_METHOD,
                    default=current_data.get(CONF_EXTRACTION_METHOD, DEFAULT_EXTRACTION_METHOD),
                ): vol.In([EXTRACTION_YTDLP, EXTRACTION_SELENIUM, EXTRACTION_AIOHTTP]),
                vol.Optional(
                    CONF_NAVIDROME_URL,
                    default=current_data.get(CONF_NAVIDROME_URL, ""),
                ): str,
                vol.Optional(
                    CONF_NAVIDROME_USERNAME,
                    default=current_data.get(CONF_NAVIDROME_USERNAME, ""),
                ): str,
                vol.Optional(
                    CONF_NAVIDROME_PASSWORD,
                    default=current_data.get(CONF_NAVIDROME_PASSWORD, ""),
                ): str,
                vol.Optional(
                    CONF_DEFAULT_MEDIA_PLAYER,
                    default=current_data.get(CONF_DEFAULT_MEDIA_PLAYER, ""),
                ): str,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            errors=errors,
        )
