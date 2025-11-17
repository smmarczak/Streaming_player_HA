# Streaming Player - Home Assistant Integration

A custom Home Assistant integration for streaming video content from private websites to Samsung TVs. This integration automatically handles popups, extracts video URLs, and casts content to your Samsung TV.

## Features

- **Automatic Video Extraction**: Intelligently extracts video streams from web pages
- **Browser Navigation & Control**: Navigate pages, click videos, and interact with websites
- **Popup Handling**: Automatically closes popups and overlays using configurable selectors
- **Samsung TV Casting**: Cast directly to Samsung TVs via Chromecast protocol
- **Selenium Support**: Optional Selenium-based extraction for JavaScript-heavy sites
- **Multiple Video Formats**: Supports MP4, WebM, HLS (.m3u8) streams
- **Home Assistant UI**: Full configuration through Home Assistant UI
- **Customizable**: Configure popup selectors and video element selectors
- **JavaScript Execution**: Run custom JavaScript on pages for advanced control

## Requirements

- Home Assistant 2023.1 or newer
- Samsung TV with Chromecast built-in (or Samsung SmartThings integration)
- Python packages (automatically installed):
  - `aiohttp>=3.8.0`
  - `beautifulsoup4>=4.11.0`
  - `selenium>=4.0.0` (optional, for JavaScript-heavy sites)
  - `pychromecast>=13.0.0`

## Installation

### Method 1: Manual Installation

1. Copy the `custom_components/streaming_player` folder to your Home Assistant `config/custom_components/` directory:

```bash
cd /config
mkdir -p custom_components
cp -r /path/to/Streaming_player_HA/custom_components/streaming_player custom_components/
```

2. Restart Home Assistant

3. Go to **Settings** → **Devices & Services** → **Add Integration**

4. Search for "Streaming Player" and click to add

### Method 2: HACS (Home Assistant Community Store)

_Coming soon - not yet available in HACS_

## Configuration

### Basic Setup

1. Navigate to **Settings** → **Devices & Services**
2. Click **Add Integration** and search for "Streaming Player"
3. Fill in the required information:
   - **Name**: Friendly name for your streaming player
   - **Stream URL**: The URL of your private video streaming site
   - **Samsung TV IP Address**: Local IP address of your Samsung TV
   - **Samsung TV Name**: Friendly name of your Samsung TV (optional)
   - **Use Selenium**: Enable if your site requires JavaScript execution (default: true)

### Advanced Configuration

You can customize popup and video selectors by editing the configuration after setup or through YAML configuration (advanced users).

#### Custom Popup Selectors

Default popup selectors include:
```python
[
    "button[class*='close']",
    "div[class*='popup'] button",
    "a[class*='close']",
    "[id*='close']",
    ".modal-close",
    ".popup-close",
    "[aria-label*='close' i]"
]
```

#### Custom Video Selectors

Default video selectors include:
```python
[
    "video",
    "iframe[src*='player']",
    "iframe[src*='embed']",
    "[class*='player']",
    "[id*='player']"
]
```

## Usage

### Playing a Stream

Once configured, you can control your streaming player through:

#### 1. Home Assistant UI

- Go to your dashboard
- Find the Streaming Player entity
- Click the play button

#### 2. Automation Example

```yaml
automation:
  - alias: "Start game stream at 7 PM"
    trigger:
      - platform: time
        at: "19:00:00"
    action:
      - service: media_player.media_play
        target:
          entity_id: media_player.streaming_player
```

#### 3. Service Call

```yaml
service: media_player.play_media
target:
  entity_id: media_player.streaming_player
data:
  media_content_id: "https://your-private-site.com/stream/game123"
  media_content_type: "video"
```

#### 4. Script Example

```yaml
script:
  play_local_sports:
    sequence:
      - service: media_player.media_play
        target:
          entity_id: media_player.streaming_player
```

### Stopping a Stream

```yaml
service: media_player.media_stop
target:
  entity_id: media_player.streaming_player
```

## Browser Navigation

The integration includes powerful browser navigation features that allow you to interact with websites, click on videos, and control page navigation.

### Available Navigation Services

- **`streaming_player.navigate_url`** - Navigate to a specific URL
- **`streaming_player.click_element`** - Click on elements (video links, buttons, etc.)
- **`streaming_player.scroll_page`** - Scroll the page up/down
- **`streaming_player.wait_for_element`** - Wait for elements to load
- **`streaming_player.execute_script`** - Run custom JavaScript
- **`streaming_player.get_page_source`** - Inspect page elements

### Quick Example: Click a Video

```yaml
# Navigate to your videos page
service: streaming_player.navigate_url
target:
  entity_id: media_player.streaming_player
data:
  url: "https://your-site.com/videos"

# Wait a moment, then click the first video
service: streaming_player.click_element
target:
  entity_id: media_player.streaming_player
data:
  selector: ".video-thumbnail:first-child"
  timeout: 10

# Play the stream
service: media_player.media_play
target:
  entity_id: media_player.streaming_player
```

For complete navigation documentation with examples, see the [Navigation Guide](NAVIGATION_GUIDE.md).

## Changing Stream URL and TV

You can dynamically change the stream URL and target TV without reconfiguring the integration.

### Change Stream URL

```yaml
service: streaming_player.set_stream_url
target:
  entity_id: media_player.streaming_player
data:
  stream_url: "https://your-site.com/stream/different-game"
```

### Change Target TV

Perfect for multi-room setups! Switch between different Samsung TVs:

```yaml
# Switch to bedroom TV
service: streaming_player.set_tv
target:
  entity_id: media_player.streaming_player
data:
  tv_ip: "192.168.1.101"
  tv_name: "Bedroom TV"

# Switch to living room TV
service: streaming_player.set_tv
target:
  entity_id: media_player.streaming_player
data:
  tv_ip: "192.168.1.100"
  tv_name: "Living Room TV"
```

### Using Options Flow

You can also update settings through the UI:

1. Go to **Settings → Devices & Services**
2. Find **Streaming Player**
3. Click **Configure**
4. Update Stream URL, TV IP, or other settings
5. Click **Submit**

The integration will reload automatically with new settings.

## Samsung TV Setup

### Chromecast Built-in

Most modern Samsung Smart TVs (2016+) have Chromecast built-in:

1. On your Samsung TV, go to **Settings** → **General** → **External Device Manager**
2. Enable **Device Connect Manager**
3. Ensure your TV is on the same network as Home Assistant
4. The integration will automatically discover your TV

### Samsung SmartThings Integration

For better control, you can also install the Samsung SmartThings integration:

1. Install the SmartThings app on your phone
2. Add your Samsung TV to SmartThings
3. In Home Assistant, add the SmartThings integration
4. Your TV will appear as a media player entity

## ChromeDriver Setup

**Good news!** ChromeDriver is now automatically managed by the integration using `webdriver-manager`.

When you restart Home Assistant after installation, the integration will automatically:
- Download the correct ChromeDriver version
- Keep it updated
- Handle platform-specific configurations

### If You Encounter Issues

If you see errors like "ChromeDriver not found" or "Session not created":

1. **Restart Home Assistant** - The integration auto-installs on first run
2. **Check the logs** - Enable debug logging to see what's happening
3. **See the installation guide** - [ChromeDriver Installation Guide](CHROMEDRIVER_INSTALL.md)

### Quick Troubleshooting

If automatic installation doesn't work, you can manually install Chromium:

**Home Assistant OS / Docker:**
```bash
apk add chromium chromium-chromedriver
```

**Ubuntu/Debian:**
```bash
sudo apt-get install chromium-browser chromium-chromedriver
```

**macOS:**
```bash
brew install chromium chromedriver
```

For complete troubleshooting steps, see [CHROMEDRIVER_INSTALL.md](CHROMEDRIVER_INSTALL.md).

## Troubleshooting

### Video URL Not Found

If the integration can't find the video URL:

1. **Enable Selenium**: Toggle "Use Selenium" in the configuration
2. **Check Selectors**: Your site may use different CSS selectors
3. **Check Logs**: Look in Home Assistant logs for extraction attempts
4. **Manual Test**: Use browser developer tools to find video element selectors

### Samsung TV Not Found

1. **Check Network**: Ensure TV and HA are on same network/subnet
2. **Enable Chromecast**: Check Samsung TV settings for Device Connect Manager
3. **Check IP**: Verify the TV's IP address hasn't changed
4. **Firewall**: Ensure ports 8008-8009 are not blocked

### Popups Not Closing

1. **Custom Selectors**: Add site-specific popup selectors to configuration
2. **Enable Selenium**: Some popups require JavaScript interaction
3. **Timing**: The integration waits 3 seconds after page load - adjust if needed

### Stream Playback Issues

1. **Format Support**: Ensure your Samsung TV supports the video format
2. **Network Speed**: Check bandwidth for streaming
3. **CORS Issues**: Some video URLs may have CORS restrictions
4. **DRM Content**: This integration cannot handle DRM-protected content

## Logs and Debugging

Enable debug logging in `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.streaming_player: debug
```

Check logs at: **Settings** → **System** → **Logs**

## Privacy and Legal

This integration is designed for streaming from **private, authorized sources** such as:
- Local sports events you have rights to stream
- Private family video servers
- Authorized institutional content
- Your own hosted media

**Important**: Do not use this integration to access copyrighted content without authorization.

## Support

For issues, questions, or feature requests:
- Open an issue on [GitHub](https://github.com/smmarczak/Streaming_player_HA/issues)
- Check Home Assistant Community forums

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Changelog

### Version 1.0.0 (Initial Release)
- Initial release with core functionality
- Video extraction with BeautifulSoup and Selenium
- Samsung TV casting via Chromecast
- Configurable popup and video selectors
- Home Assistant UI configuration

## Credits

Developed for streaming local sports events to Samsung TVs via Home Assistant.

## Related Projects

- [Home Assistant](https://www.home-assistant.io/)
- [pychromecast](https://github.com/home-assistant-libs/pychromecast)
- [Samsung SmartThings](https://www.home-assistant.io/integrations/smartthings/)
