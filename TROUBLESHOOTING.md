# Troubleshooting Guide - Streaming Player Integration

## Common Issues and Solutions

### 1. Integration Not Showing in Home Assistant

**Problem**: Can't find "Streaming Player" when adding a new integration.

**Solutions**:
- Ensure the `custom_components/streaming_player` folder is in your Home Assistant config directory
- Restart Home Assistant completely (not just reload)
- Check file permissions: `sudo chown -R homeassistant:homeassistant /config/custom_components`
- Check logs for errors: Settings → System → Logs

### 2. Video URL Not Found

**Problem**: Integration reports "Failed to extract video URL" or "No video URL found on page"

**Solutions**:

#### A. Enable Selenium
- Toggle "Use Selenium" to ON in integration settings
- Ensure Chrome/Chromium is installed (see Installation section in README)
- Restart the integration after enabling Selenium

#### B. Check Video Selectors
Your site may use different CSS selectors. Use browser dev tools to find the correct selectors:

1. Open your stream site in Chrome/Firefox
2. Right-click the video player → Inspect
3. Find the video element or iframe
4. Note the class names, IDs, or tag structure
5. Add custom selectors in integration configuration

Common video element patterns:
```css
video
iframe[src*="embed"]
div[id="player"] video
div.video-container iframe
```

#### C. Check for JavaScript-Loaded Content
If video loads via JavaScript:
- Enable Selenium (required for JS-heavy sites)
- Increase wait time (modify `video_scraper.py` line with `time.sleep(3)` to higher value)

#### D. Manual URL Extraction
For testing, manually extract the video URL:
1. Open browser developer tools (F12)
2. Go to Network tab
3. Filter by "media" or "m3u8"
4. Play the video
5. Find the actual video URL in the network requests
6. Use that URL directly via `media_player.play_media` service

### 3. Popups Not Being Closed

**Problem**: Popups remain on screen, blocking video playback.

**Solutions**:

#### A. Add Custom Popup Selectors
Find the close button selector:
1. Right-click on popup close button → Inspect
2. Note the element's class, ID, or structure
3. Add to configuration

Examples:
```css
button.close
a[onclick*="close"]
div.modal button[aria-label="Close"]
#popup-close
```

#### B. Must Use Selenium
Some popups only work with JavaScript interaction:
- Enable "Use Selenium" in configuration
- Selenium can click elements, while simple scraping cannot

#### C. Wait for Popup to Appear
Some popups appear after a delay. Modify `video_scraper.py`:
```python
# Increase wait time before closing popups
time.sleep(5)  # Was 3 seconds
```

### 4. Samsung TV Not Found / Cannot Connect

**Problem**: "Failed to connect to Samsung TV" error

**Solutions**:

#### A. Verify TV Settings
1. On Samsung TV: Settings → General → External Device Manager
2. Enable "Device Connect Manager"
3. Enable "Access Notification" if available

#### B. Check Network
- Ensure TV and Home Assistant are on same network
- Check TV IP hasn't changed (use DHCP reservation)
- Ping the TV: `ping 192.168.1.xxx`
- Check firewall rules for ports 8008-8009

#### C. Chromecast Built-in
Modern Samsung TVs (2016+) have Chromecast built-in:
- Ensure it's enabled in TV settings
- Update TV firmware to latest version
- Some older TVs may not support this

#### D. Use Samsung SmartThings Instead
Alternative method:
1. Install SmartThings integration in Home Assistant
2. Add your Samsung TV in SmartThings app
3. Control via SmartThings media player entity
4. Use this integration only for video extraction

### 5. Stream Starts But No Video Plays

**Problem**: Integration says "playing" but TV shows no video or black screen.

**Solutions**:

#### A. Check Video Format
- Ensure Samsung TV supports the video format
- Check extracted video URL in logs
- Try URL directly in TV browser or VLC to verify it works

#### B. CORS or Authentication Issues
Some video URLs have restrictions:
- Check if URL requires cookies/authentication
- May need to modify headers in `video_scraper.py`
- Some CDNs block direct URL access

#### C. Network Bandwidth
- Ensure sufficient bandwidth for streaming
- Check if video URL is accessible from TV's network location
- Try lower quality stream

#### D. Check Video URL Type
Different streaming formats need different handling:
- **Direct MP4**: Should work directly
- **HLS (.m3u8)**: Should work on most Samsung TVs
- **DASH**: May need transcoding
- **RTMP**: Not supported, needs conversion

### 6. Selenium Errors

**Problem**: Errors mentioning "chromedriver" or "selenium"

**Solutions**:

#### A. Install Chrome/Chromium
**Home Assistant OS/Supervised**:
```bash
# SSH into HA or use Terminal add-on
apk add chromium chromium-chromedriver
```

**Docker**:
```bash
docker exec -it homeassistant apk add chromium chromium-chromedriver
```

**Home Assistant Core**:
```bash
# Ubuntu/Debian
sudo apt install chromium-browser chromium-chromedriver

# macOS
brew install chromium chromedriver
```

#### B. Check Selenium Version
```bash
pip show selenium
```
Should be version 4.0.0 or higher

#### C. Disable Selenium if Not Needed
If your site doesn't require JavaScript:
- Toggle "Use Selenium" to OFF
- Will use faster aiohttp method instead

### 7. Integration Stops Working After HA Update

**Problem**: Integration breaks after Home Assistant update

**Solutions**:
- Check logs for deprecation warnings
- Update integration to latest version
- Check GitHub for updates or known issues
- Disable and re-enable integration
- Remove and re-add integration (last resort)

### 8. High CPU Usage

**Problem**: Home Assistant uses high CPU when streaming

**Solutions**:
- Disable Selenium if not needed (uses headless Chrome)
- Don't enable debug logging in production
- Check for infinite loops in logs
- Restart Home Assistant

### 9. Integration Configuration Missing

**Problem**: Can't find integration options or settings

**Solutions**:
- Go to: Settings → Devices & Services → Streaming Player
- Click the 3 dots → Configure
- Or delete and re-add the integration with new settings

### 10. Module Import Errors

**Problem**: Errors like "No module named 'selenium'" or "No module named 'pychromecast'"

**Solutions**:

#### A. Restart Home Assistant
Dependencies should auto-install on first load

#### B. Manual Installation
```bash
# SSH or Terminal
pip install -r /config/custom_components/streaming_player/requirements.txt
```

#### C. Check manifest.json
Ensure all requirements are listed in `manifest.json`

## Debugging Tips

### Enable Debug Logging

Add to `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.streaming_player: debug
```

### Check Logs
1. Settings → System → Logs
2. Filter by "streaming_player"
3. Look for error messages

### Test Video Extraction Manually

Create a test script in Home Assistant:
```yaml
service: media_player.play_media
target:
  entity_id: media_player.streaming_player
data:
  media_content_id: "DIRECT_VIDEO_URL_HERE"
  media_content_type: "video"
```

### Verify Network Connectivity
```bash
# SSH into Home Assistant
ping YOUR_SAMSUNG_TV_IP
curl -I YOUR_STREAM_URL
```

### Check Browser Developer Tools
1. Open stream site in browser
2. F12 → Network tab
3. Look for video file requests (.mp4, .m3u8)
4. Right-click → Copy → Copy URL
5. Test that URL in integration

## Getting More Help

If you're still having issues:

1. **Check Logs**: Always include relevant log entries when asking for help
2. **GitHub Issues**: Open an issue at https://github.com/smmarczak/Streaming_player_HA/issues
3. **Home Assistant Community**: Post in the Home Assistant forums
4. **Provide Details**:
   - Home Assistant version
   - Integration version
   - Samsung TV model and year
   - Error messages from logs
   - Steps to reproduce

## Advanced Debugging

### Run Selenium Test Outside Home Assistant

Test if Selenium can extract the video:

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
driver.get('YOUR_STREAM_URL')

# Wait and check page source
import time
time.sleep(5)
print(driver.page_source)

# Look for video elements
videos = driver.find_elements_by_tag_name('video')
print(f"Found {len(videos)} video elements")

driver.quit()
```

### Test Direct Video URL

```bash
# Test if video URL is accessible
curl -I "EXTRACTED_VIDEO_URL"

# Or play in VLC/ffplay
vlc "EXTRACTED_VIDEO_URL"
```

### Test Chromecast Connection

```python
import pychromecast

chromecasts, browser = pychromecast.get_chromecasts()
print("Found chromecasts:", [cc.name for cc in chromecasts])
```
