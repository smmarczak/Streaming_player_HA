# ChromeDriver Installation Guide

The Streaming Player integration now automatically manages ChromeDriver installation using `webdriver-manager`. However, if you encounter issues, this guide will help you troubleshoot and manually install if needed.

## Automatic Installation (Recommended)

The integration will automatically download and manage ChromeDriver when you restart Home Assistant after installation. No manual steps required!

The `webdriver-manager` package handles:
- Downloading the correct ChromeDriver version for your Chrome/Chromium
- Managing driver updates
- Platform-specific configurations

## Troubleshooting ChromeDriver Issues

###Error: "ChromeDriver not found"

If you see this error, follow these steps:

#### Step 1: Verify Dependencies

Check that webdriver-manager is installed:

```bash
# For Home Assistant Core (venv)
source /srv/homeassistant/bin/activate
pip show webdriver-manager

# For Docker
docker exec -it homeassistant pip show webdriver-manager
```

#### Step 2: Restart Home Assistant

After confirming the package is installed:
1. Go to **Settings → System → Restart**
2. Wait for restart to complete
3. Try using the integration again

#### Step 3: Check Logs

Enable debug logging to see what's happening:

```yaml
# configuration.yaml
logger:
  logs:
    custom_components.streaming_player: debug
    custom_components.streaming_player.video_scraper: debug
    custom_components.streaming_player.browser_controller: debug
```

Check logs at: **Settings → System → Logs**

### Manual ChromeDriver Installation (If Automatic Fails)

If automatic installation doesn't work, you can install manually:

#### Option 1: Install Chromium/Chrome

**Home Assistant OS / Supervised:**
```bash
# SSH or Terminal add-on
apk add chromium chromium-chromedriver
```

**Docker:**
```bash
docker exec -it homeassistant apk add chromium chromium-chromedriver
```

**Home Assistant Core (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install chromium-browser chromium-chromedriver
```

**Home Assistant Core (macOS):**
```bash
brew install chromium chromedriver
```

#### Option 2: Download ChromeDriver Manually

1. **Check your Chrome version:**
   - Run: `chromium --version` or `google-chrome --version`

2. **Download matching ChromeDriver:**
   - Visit: https://chromedriver.chromium.org/downloads
   - Download version matching your Chrome

3. **Install ChromeDriver:**

**Linux:**
```bash
# Extract and move to PATH
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
```

**macOS:**
```bash
# Extract and move to PATH
unzip chromedriver_mac64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
```

4. **Verify installation:**
```bash
chromedriver --version
```

### Disable Selenium (Workaround)

If you can't get ChromeDriver working, you can disable Selenium:

1. Go to **Settings → Devices & Services**
2. Find your **Streaming Player** integration
3. Click **Configure**
4. Uncheck **"Use Selenium"**
5. Click **Submit**

**Note:** This will disable:
- Browser navigation features
- Clicking on elements
- JavaScript execution
- Advanced popup handling

The integration will still work for:
- Basic video extraction (static HTML only)
- Casting to Samsung TV
- URL changes

### Common Issues

#### Issue: "Session not created: This version of ChromeDriver only supports Chrome version XX"

**Solution:** Update Chrome/Chromium or ChromeDriver to matching versions

```bash
# Update Chromium (Home Assistant OS/Docker)
apk upgrade chromium chromium-chromedriver

# Update Chrome (Ubuntu/Debian)
sudo apt-get update && sudo apt-get upgrade google-chrome-stable

# With webdriver-manager (auto-updates)
pip install --upgrade webdriver-manager
```

#### Issue: "WebDriverException: chrome not reachable"

**Solution:** Chrome/Chromium is not installed

```bash
# Install Chromium
# See "Install Chromium/Chrome" section above
```

#### Issue: "Permission denied: /root/.cache/selenium"

**Solution:** Fix permissions

```bash
# For Docker/Home Assistant OS
chmod -R 777 /root/.cache/selenium

# Or set environment variable
export WDM_LOCAL=1
```

#### Issue: Integration works but browser navigation doesn't

**Solution:** Check that:
1. Selenium is enabled in configuration
2. ChromeDriver is installed and accessible
3. Check logs for specific error messages

## Verifying Installation

Test if everything works:

1. Enable debug logging
2. Use the `navigate_url` service:

```yaml
service: streaming_player.navigate_url
target:
  entity_id: media_player.streaming_player
data:
  url: "https://www.google.com"
```

3. Check logs for success message:
   - "Browser controller initialized with webdriver-manager" ✅
   - "Browser controller initialized with system chromedriver" ✅
   - "ChromeDriver not found" ❌

## Alternative: Use Without Selenium

You can still use the integration without Selenium for basic video extraction:

**Pros:**
- No ChromeDriver needed
- Faster and lighter
- Works for simple sites

**Cons:**
- Can't handle JavaScript
- No browser navigation
- Limited popup handling

To disable Selenium:
- During setup: Uncheck "Use Selenium"
- After setup: Configure integration and uncheck the option

## Getting Help

If you're still having issues:

1. **Check the logs** with debug logging enabled
2. **Verify Chrome version** matches ChromeDriver version
3. **Try webdriver-manager first** - it usually "just works"
4. **Open an issue** on GitHub with:
   - Home Assistant version
   - Installation method (OS/Supervised/Core/Docker)
   - Chrome/Chromium version
   - Error messages from logs
   - Steps you've tried

GitHub Issues: https://github.com/smmarczak/Streaming_player_HA/issues

## Summary

**Best practice:**
1. Let `webdriver-manager` handle it automatically (default)
2. If that fails, install Chromium/Chrome from package manager
3. As last resort, disable Selenium in configuration

The integration will automatically fall back to basic extraction if Selenium fails, so you'll always have some functionality even if ChromeDriver isn't working.
