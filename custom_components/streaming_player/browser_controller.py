"""Browser controller for navigating and interacting with web pages."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


class BrowserController:
    """Handle browser navigation and interaction."""

    def __init__(self, use_selenium: bool = True) -> None:
        """Initialize the browser controller."""
        self.use_selenium = use_selenium
        self._driver = None
        self._loop = None
        self._current_url = None

    async def initialize(self) -> bool:
        """Initialize the browser driver."""
        if not self.use_selenium:
            _LOGGER.warning("Browser controller requires Selenium to be enabled")
            return False

        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options

            loop = asyncio.get_event_loop()
            self._loop = loop

            # Initialize in executor to avoid blocking
            await loop.run_in_executor(None, self._init_driver)
            return True

        except ImportError:
            _LOGGER.error("Selenium not available. Install with: pip install selenium")
            return False
        except Exception as e:
            _LOGGER.error("Error initializing browser: %s", e)
            return False

    def _init_driver(self) -> None:
        """Initialize Selenium driver (runs in executor)."""
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )

        self._driver = webdriver.Chrome(options=chrome_options)
        _LOGGER.info("Browser controller initialized successfully")

    async def navigate(self, url: str) -> bool:
        """Navigate to a URL."""
        if not self._driver:
            if not await self.initialize():
                return False

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._driver.get, url)
            self._current_url = url
            _LOGGER.info("Navigated to: %s", url)

            # Wait a moment for page to load
            await asyncio.sleep(2)
            return True

        except Exception as e:
            _LOGGER.error("Error navigating to %s: %s", url, e)
            return False

    async def click_element(self, selector: str, timeout: int = 10) -> bool:
        """Click an element by CSS selector."""
        if not self._driver:
            _LOGGER.error("Browser not initialized")
            return False

        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            loop = asyncio.get_event_loop()

            def _click():
                element = WebDriverWait(self._driver, timeout).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                element.click()
                _LOGGER.info("Clicked element: %s", selector)

            await loop.run_in_executor(None, _click)

            # Wait a moment for any page changes
            await asyncio.sleep(1)
            return True

        except Exception as e:
            _LOGGER.error("Error clicking element %s: %s", selector, e)
            return False

    async def scroll_page(self, direction: str = "down", amount: int = 500) -> bool:
        """Scroll the page."""
        if not self._driver:
            _LOGGER.error("Browser not initialized")
            return False

        try:
            loop = asyncio.get_event_loop()

            def _scroll():
                if direction.lower() == "down":
                    self._driver.execute_script(f"window.scrollBy(0, {amount});")
                elif direction.lower() == "up":
                    self._driver.execute_script(f"window.scrollBy(0, -{amount});")
                elif direction.lower() == "top":
                    self._driver.execute_script("window.scrollTo(0, 0);")
                elif direction.lower() == "bottom":
                    self._driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);"
                    )

            await loop.run_in_executor(None, _scroll)
            _LOGGER.info("Scrolled page: %s", direction)
            return True

        except Exception as e:
            _LOGGER.error("Error scrolling page: %s", e)
            return False

    async def execute_script(self, script: str) -> Any:
        """Execute JavaScript on the page."""
        if not self._driver:
            _LOGGER.error("Browser not initialized")
            return None

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._driver.execute_script, script
            )
            _LOGGER.info("Executed script successfully")
            return result

        except Exception as e:
            _LOGGER.error("Error executing script: %s", e)
            return None

    async def wait_for_element(self, selector: str, timeout: int = 10) -> bool:
        """Wait for an element to appear."""
        if not self._driver:
            _LOGGER.error("Browser not initialized")
            return False

        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            loop = asyncio.get_event_loop()

            def _wait():
                WebDriverWait(self._driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                _LOGGER.info("Element found: %s", selector)

            await loop.run_in_executor(None, _wait)
            return True

        except Exception as e:
            _LOGGER.error("Error waiting for element %s: %s", selector, e)
            return False

    async def get_page_source(self) -> str | None:
        """Get the current page source."""
        if not self._driver:
            _LOGGER.error("Browser not initialized")
            return None

        try:
            loop = asyncio.get_event_loop()
            source = await loop.run_in_executor(None, lambda: self._driver.page_source)
            return source

        except Exception as e:
            _LOGGER.error("Error getting page source: %s", e)
            return None

    async def get_current_url(self) -> str | None:
        """Get the current URL."""
        if not self._driver:
            return self._current_url

        try:
            loop = asyncio.get_event_loop()
            url = await loop.run_in_executor(None, lambda: self._driver.current_url)
            self._current_url = url
            return url

        except Exception as e:
            _LOGGER.error("Error getting current URL: %s", e)
            return self._current_url

    async def take_screenshot(self, file_path: str) -> bool:
        """Take a screenshot of the current page."""
        if not self._driver:
            _LOGGER.error("Browser not initialized")
            return False

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._driver.save_screenshot, file_path)
            _LOGGER.info("Screenshot saved to: %s", file_path)
            return True

        except Exception as e:
            _LOGGER.error("Error taking screenshot: %s", e)
            return False

    async def get_elements(self, selector: str) -> list[dict[str, Any]]:
        """Get information about all matching elements."""
        if not self._driver:
            _LOGGER.error("Browser not initialized")
            return []

        try:
            from selenium.webdriver.common.by import By

            loop = asyncio.get_event_loop()

            def _get_elements():
                elements = self._driver.find_elements(By.CSS_SELECTOR, selector)
                return [
                    {
                        "text": elem.text,
                        "tag": elem.tag_name,
                        "href": elem.get_attribute("href"),
                        "src": elem.get_attribute("src"),
                        "class": elem.get_attribute("class"),
                        "id": elem.get_attribute("id"),
                    }
                    for elem in elements
                ]

            elements_info = await loop.run_in_executor(None, _get_elements)
            _LOGGER.info("Found %d elements matching: %s", len(elements_info), selector)
            return elements_info

        except Exception as e:
            _LOGGER.error("Error getting elements %s: %s", selector, e)
            return []

    async def close(self) -> None:
        """Close the browser."""
        if self._driver:
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self._driver.quit)
                _LOGGER.info("Browser closed")
            except Exception as e:
                _LOGGER.error("Error closing browser: %s", e)
            finally:
                self._driver = None
