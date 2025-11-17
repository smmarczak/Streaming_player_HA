"""Video scraper for extracting stream URLs from web pages."""
from __future__ import annotations

import asyncio
import logging
import re
from typing import Any
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup

_LOGGER = logging.getLogger(__name__)


class VideoScraper:
    """Handle video URL extraction from web pages."""

    def __init__(
        self,
        stream_url: str,
        popup_selectors: list[str] | None = None,
        video_selectors: list[str] | None = None,
        use_selenium: bool = False,
    ) -> None:
        """Initialize the video scraper."""
        self.stream_url = stream_url
        self.popup_selectors = popup_selectors or []
        self.video_selectors = video_selectors or ["video", "iframe"]
        self.use_selenium = use_selenium
        self._session: aiohttp.ClientSession | None = None

    async def get_video_url(self) -> str | None:
        """Extract video URL from the stream page."""
        if self.use_selenium:
            return await self._get_video_url_selenium()
        else:
            return await self._get_video_url_aiohttp()

    async def _get_video_url_aiohttp(self) -> str | None:
        """Extract video URL using aiohttp and BeautifulSoup."""
        try:
            if self._session is None:
                self._session = aiohttp.ClientSession()

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Referer": self.stream_url,
            }

            async with self._session.get(
                self.stream_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    _LOGGER.error("Failed to fetch page: %s", response.status)
                    return None

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                # Try to find video element
                video_url = await self._extract_video_from_soup(soup)

                if video_url:
                    # Make URL absolute if it's relative
                    return urljoin(self.stream_url, video_url)

                _LOGGER.warning("No video URL found on page")
                return None

        except Exception as e:
            _LOGGER.error("Error extracting video URL: %s", e)
            return None

    async def _extract_video_from_soup(self, soup: BeautifulSoup) -> str | None:
        """Extract video URL from BeautifulSoup object."""
        # Look for video tag with source
        video_tag = soup.find("video")
        if video_tag:
            src = video_tag.get("src")
            if src:
                return src
            # Check for source tag inside video
            source_tag = video_tag.find("source")
            if source_tag and source_tag.get("src"):
                return source_tag.get("src")

        # Look for iframe with video player
        iframes = soup.find_all("iframe")
        for iframe in iframes:
            src = iframe.get("src", "")
            # Common video player patterns
            if any(
                pattern in src.lower()
                for pattern in ["player", "embed", "video", "stream"]
            ):
                return src

        # Look for HLS/m3u8 URLs in script tags
        scripts = soup.find_all("script")
        for script in scripts:
            script_text = script.string or ""
            # Look for .m3u8 or common streaming URLs
            m3u8_match = re.search(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', script_text)
            if m3u8_match:
                return m3u8_match.group(1)

            # Look for video URLs in common video player configs
            video_match = re.search(
                r'(?:file|src|source|url)[\s:=]+["\']([^"\']+\.(?:mp4|webm|m3u8))["\']',
                script_text,
                re.IGNORECASE,
            )
            if video_match:
                return video_match.group(1)

        return None

    async def _get_video_url_selenium(self) -> str | None:
        """Extract video URL using Selenium (for handling JavaScript-heavy sites)."""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import TimeoutException

            # Run Selenium in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._selenium_extract)

        except ImportError:
            _LOGGER.error("Selenium not available. Install with: pip install selenium")
            return None
        except Exception as e:
            _LOGGER.error("Error with Selenium extraction: %s", e)
            return None

    def _selenium_extract(self) -> str | None:
        """Selenium extraction in synchronous context."""
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException, NoSuchElementException

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        driver = None
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(self.stream_url)

            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Try to close popups
            for selector in self.popup_selectors:
                try:
                    # Convert CSS selector to appropriate By strategy
                    if selector.startswith("#"):
                        by = By.ID
                        selector = selector[1:]
                    elif selector.startswith("."):
                        by = By.CLASS_NAME
                        selector = selector[1:]
                    else:
                        by = By.CSS_SELECTOR

                    popup_close = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    popup_close.click()
                    _LOGGER.debug("Closed popup with selector: %s", selector)
                except (TimeoutException, NoSuchElementException):
                    continue

            # Wait a bit for video player to load
            import time
            time.sleep(3)

            # Try to find video element
            for selector in self.video_selectors:
                try:
                    if selector == "video":
                        element = driver.find_element(By.TAG_NAME, "video")
                    elif selector == "iframe":
                        element = driver.find_element(By.TAG_NAME, "iframe")
                    else:
                        element = driver.find_element(By.CSS_SELECTOR, selector)

                    src = element.get_attribute("src")
                    if src:
                        return urljoin(self.stream_url, src)
                except NoSuchElementException:
                    continue

            # Look for m3u8 or video URLs in page source
            page_source = driver.page_source
            m3u8_match = re.search(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', page_source)
            if m3u8_match:
                return m3u8_match.group(1)

            # Check network logs for video requests (if available)
            # This requires additional Chrome options to enable logging

            _LOGGER.warning("Could not find video URL with Selenium")
            return None

        finally:
            if driver:
                driver.quit()

    async def close(self) -> None:
        """Close the scraper and cleanup resources."""
        if self._session:
            await self._session.close()
            self._session = None
