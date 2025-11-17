# Navigation Guide - Streaming Player

This guide explains how to use the browser navigation features to interact with streaming websites and click on videos before playing them.

## Overview

The Streaming Player integration includes a browser controller that allows you to:
- Navigate to different URLs
- Click on elements (links, buttons, video thumbnails)
- Scroll pages
- Execute JavaScript
- Wait for elements to load
- Inspect page content

## Prerequisites

- Selenium must be enabled in your configuration
- Chrome/Chromium must be installed on your system
- Debug logging enabled (recommended): see configuration below

## Services Available

### 1. Navigate to URL
Navigate the browser to a specific page.

```yaml
service: streaming_player.navigate_url
target:
  entity_id: media_player.streaming_player
data:
  url: "https://your-streaming-site.com/videos"
```

### 2. Click Element
Click an element on the current page using a CSS selector.

```yaml
service: streaming_player.click_element
target:
  entity_id: media_player.streaming_player
data:
  selector: "a.video-link"  # CSS selector
  timeout: 10  # Optional, default 10 seconds
```

### 3. Scroll Page
Scroll the page to reveal more content.

```yaml
service: streaming_player.scroll_page
target:
  entity_id: media_player.streaming_player
data:
  direction: "down"  # Options: down, up, top, bottom
```

### 4. Wait for Element
Wait for an element to appear (useful after clicking).

```yaml
service: streaming_player.wait_for_element
target:
  entity_id: media_player.streaming_player
data:
  selector: "video"
  timeout: 15
```

### 5. Execute JavaScript
Run custom JavaScript on the page.

```yaml
service: streaming_player.execute_script
target:
  entity_id: media_player.streaming_player
data:
  script: |
    document.querySelector('.video-player').play();
```

### 6. Get Page Source
Inspect the page and log available elements (check logs).

```yaml
service: streaming_player.get_page_source
target:
  entity_id: media_player.streaming_player
```

## Practical Examples

### Example 1: Navigate and Click a Video

This example navigates to a video list page and clicks the first video.

```yaml
# Step 1: Navigate to the videos page
service: streaming_player.navigate_url
target:
  entity_id: media_player.streaming_player
data:
  url: "https://your-site.com/videos"

# Step 2: Wait a moment for page to load (use script or automation delay)

# Step 3: Click the first video thumbnail
service: streaming_player.click_element
target:
  entity_id: media_player.streaming_player
data:
  selector: ".video-thumbnail:first-child"
  timeout: 10

# Step 4: Play the stream
service: media_player.media_play
target:
  entity_id: media_player.streaming_player
```

### Example 2: Complete Automation Script

Create a script that does everything automatically:

```yaml
script:
  play_specific_video:
    alias: "Play Specific Video"
    sequence:
      # Navigate to the site
      - service: streaming_player.navigate_url
        target:
          entity_id: media_player.streaming_player
        data:
          url: "https://your-site.com/streams"

      # Wait for page to load
      - delay:
          seconds: 3

      # Scroll down to see more videos
      - service: streaming_player.scroll_page
        target:
          entity_id: media_player.streaming_player
        data:
          direction: "down"

      # Click on the specific video (adjust selector as needed)
      - service: streaming_player.click_element
        target:
          entity_id: media_player.streaming_player
        data:
          selector: 'a[href*="game-123"]'
          timeout: 15

      # Wait for video player to load
      - service: streaming_player.wait_for_element
        target:
          entity_id: media_player.streaming_player
        data:
          selector: "video, iframe"
          timeout: 20

      # Extract and play the video
      - service: media_player.media_play
        target:
          entity_id: media_player.streaming_player
```

### Example 3: Browse Multiple Videos

Create an automation to browse through video options:

```yaml
automation:
  - alias: "Browse and Select Sports Video"
    trigger:
      - platform: state
        entity_id: input_select.video_choice
    action:
      # Navigate to base URL
      - service: streaming_player.navigate_url
        target:
          entity_id: media_player.streaming_player
        data:
          url: "https://your-site.com/sports"

      - delay:
          seconds: 2

      # Click based on selection
      - choose:
          - conditions:
              - condition: state
                entity_id: input_select.video_choice
                state: "Game 1"
            sequence:
              - service: streaming_player.click_element
                target:
                  entity_id: media_player.streaming_player
                data:
                  selector: ".video-item:nth-child(1)"

          - conditions:
              - condition: state
                entity_id: input_select.video_choice
                state: "Game 2"
            sequence:
              - service: streaming_player.click_element
                target:
                  entity_id: media_player.streaming_player
                data:
                  selector: ".video-item:nth-child(2)"

      # Play the selected video
      - delay:
          seconds: 2
      - service: media_player.media_play
        target:
          entity_id: media_player.streaming_player
```

## Finding CSS Selectors

To find the correct CSS selector for an element:

1. **Open your streaming site in Chrome/Firefox**
2. **Right-click on the element** you want to click (video thumbnail, play button, etc.)
3. **Select "Inspect" or "Inspect Element"**
4. **In the Developer Tools:**
   - The element will be highlighted in the HTML
   - Right-click on the highlighted element
   - Select: Copy → Copy selector

### Common CSS Selector Patterns

```css
/* By class */
.video-thumbnail
button.play-button

/* By ID */
#video-player
#main-video

/* By attribute */
a[href*="video"]
button[data-video-id="123"]

/* Nth child */
.video-list .item:nth-child(1)  /* First item */
.video-list .item:nth-child(2)  /* Second item */
.video-list .item:last-child    /* Last item */

/* Complex selectors */
div.container > a.video-link
.sidebar .video-list li:first-child a
```

## Debugging Tips

### Enable Debug Logging

Add to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.streaming_player: debug
    custom_components.streaming_player.browser_controller: debug
```

### Use Get Page Source

Inspect what's on the page:

```yaml
service: streaming_player.get_page_source
target:
  entity_id: media_player.streaming_player
```

Then check your Home Assistant logs for:
- List of clickable elements
- Element attributes (href, src, class, id)
- Page structure

### Test Selectors in Browser Console

Before using a selector in Home Assistant, test it in your browser:

1. Open browser Developer Tools (F12)
2. Go to Console tab
3. Type: `document.querySelector("YOUR_SELECTOR")`
4. If it returns an element, your selector works!

Example:
```javascript
// Test if selector finds an element
document.querySelector(".video-thumbnail")

// Get all matching elements
document.querySelectorAll("a.video-link")
```

## Advanced: Execute JavaScript

For complex interactions, use JavaScript:

```yaml
# Click using JavaScript
service: streaming_player.execute_script
target:
  entity_id: media_player.streaming_player
data:
  script: |
    document.querySelector('.video-item:nth-child(3)').click();

# Modify page before extracting video
service: streaming_player.execute_script
target:
  entity_id: media_player.streaming_player
data:
  script: |
    // Remove overlays
    document.querySelectorAll('.overlay').forEach(el => el.remove());

    // Force video quality
    if (window.player) {
      window.player.setQuality('1080p');
    }
```

## Entity Attributes

The media player exposes these attributes:

```yaml
# Check current page
{{ state_attr('media_player.streaming_player', 'current_page_url') }}

# Check if browser is active
{{ state_attr('media_player.streaming_player', 'browser_active') }}

# Get video URL
{{ state_attr('media_player.streaming_player', 'video_url') }}
```

## Dashboard Card Example

Create a dashboard with navigation controls:

```yaml
type: entities
title: Video Browser
entities:
  - entity: media_player.streaming_player

  - type: button
    name: Navigate to Videos
    icon: mdi:web
    tap_action:
      action: call-service
      service: streaming_player.navigate_url
      target:
        entity_id: media_player.streaming_player
      data:
        url: "https://your-site.com/videos"

  - type: button
    name: Click First Video
    icon: mdi:play-circle
    tap_action:
      action: call-service
      service: streaming_player.click_element
      target:
        entity_id: media_player.streaming_player
      data:
        selector: ".video-item:first-child"

  - type: button
    name: Scroll Down
    icon: mdi:arrow-down
    tap_action:
      action: call-service
      service: streaming_player.scroll_page
      target:
        entity_id: media_player.streaming_player
      data:
        direction: "down"

  - type: button
    name: Play Stream
    icon: mdi:cast
    tap_action:
      action: call-service
      service: media_player.media_play
      target:
        entity_id: media_player.streaming_player
```

## Workflow: Typical Usage

Here's the typical workflow for using the navigation features:

1. **Navigate** to the page with videos
   ```yaml
   service: streaming_player.navigate_url
   data:
     url: "https://your-site.com"
   ```

2. **Inspect** the page (optional, for debugging)
   ```yaml
   service: streaming_player.get_page_source
   ```

3. **Scroll** if needed to reveal videos
   ```yaml
   service: streaming_player.scroll_page
   data:
     direction: "down"
   ```

4. **Click** on the video you want
   ```yaml
   service: streaming_player.click_element
   data:
     selector: ".video-link"
   ```

5. **Wait** for video player to load
   ```yaml
   service: streaming_player.wait_for_element
   data:
     selector: "video"
   ```

6. **Play** the stream
   ```yaml
   service: media_player.media_play
   ```

## Troubleshooting

### Element Not Found
- Use `get_page_source` to see what elements are available
- Try a more general selector (e.g., just `a` or `button`)
- Check if element loads with JavaScript (wait longer)
- Try `wait_for_element` first

### Click Not Working
- Element might not be clickable (covered by overlay)
- Try scrolling to element first
- Use JavaScript click instead: `element.click()`
- Increase timeout

### Browser Not Starting
- Check Chrome/Chromium is installed
- Check logs for Selenium errors
- Ensure Selenium is enabled in configuration
- Try restarting Home Assistant

### Page Not Loading
- Check URL is accessible
- Verify network connectivity
- Look for redirects or authentication
- Check page load timeout (default 30s)

## Performance Tips

- **Reuse browser sessions**: The browser stays open between commands
- **Use delays between actions**: Give pages time to load
- **Close browser when done**: Stops playback to free resources
- **Use specific selectors**: More efficient than broad searches

## Security Note

The browser runs in headless mode and doesn't save cookies or credentials between sessions. Always ensure you have authorization to access the content you're streaming.

## Support

For issues or questions about navigation features:
- Check Home Assistant logs with debug logging enabled
- Open an issue on [GitHub](https://github.com/smmarczak/Streaming_player_HA/issues)
- Include the selector you're trying to use and any error messages
