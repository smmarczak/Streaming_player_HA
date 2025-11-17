# Streaming Player

Stream video content from private websites to Samsung TVs through Home Assistant.

## Features

- 🎬 **Automatic Video Extraction** - Intelligently finds and extracts video streams from web pages
- 🚫 **Popup Handling** - Automatically closes popups and overlays
- 📺 **Samsung TV Casting** - Cast directly to Samsung TVs via Chromecast
- ⚙️ **Configurable** - Customize selectors for different websites
- 🤖 **Selenium Support** - Optional JavaScript execution for dynamic sites
- 📱 **Home Assistant UI** - Easy setup through the UI

## Perfect For

- Local sports events streaming
- Private video servers
- Authorized institutional content
- Personal media sources

## Supported Formats

- MP4, WebM video files
- HLS (.m3u8) streams
- Embedded video players
- iframe-based players

## Requirements

- Home Assistant 2023.1+
- Samsung TV with Chromecast built-in (2016+ models)
- Network connectivity between HA and TV

## Quick Start

1. Install via HACS
2. Restart Home Assistant
3. Add integration: Settings → Devices & Services → Add Integration → "Streaming Player"
4. Configure with your stream URL and Samsung TV IP
5. Use the media player entity to control playback

## Documentation

Full documentation available in the [README](https://github.com/smmarczak/Streaming_player_HA/blob/main/README.md).

For troubleshooting, see the [Troubleshooting Guide](https://github.com/smmarczak/Streaming_player_HA/blob/main/TROUBLESHOOTING.md).
