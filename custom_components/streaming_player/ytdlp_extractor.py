"""Video extractor using yt-dlp for reliable stream extraction."""
from __future__ import annotations

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any

_LOGGER = logging.getLogger(__name__)

# Thread pool for blocking operations
_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="ytdlp")


class YtdlpExtractor:
    """Extract video URLs using yt-dlp."""

    def __init__(self, stream_url: str) -> None:
        """Initialize the yt-dlp extractor."""
        self.stream_url = stream_url

    async def get_video_url(self) -> str | None:
        """Extract video URL using yt-dlp."""
        try:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(_executor, self._extract)
        except Exception as e:
            _LOGGER.error("Error with yt-dlp extraction: %s", e)
            return None

    def _extract(self) -> str | None:
        """Extract video URL synchronously."""
        try:
            import yt_dlp
        except ImportError:
            _LOGGER.error(
                "yt-dlp not available. Install with: pip install yt-dlp"
            )
            return None

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'format': 'best[ext=mp4]/best',  # Prefer MP4 for TV compatibility
            'no_color': True,
            # Don't download, just extract info
            'skip_download': True,
            # Handle age-restricted/geo-blocked content
            'geo_bypass': True,
            # Cookie handling (optional)
            'cookiefile': None,
            # User agent
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                _LOGGER.info("Extracting video info from: %s", self.stream_url)

                # Extract info without downloading
                info = ydl.extract_info(self.stream_url, download=False)

                if not info:
                    _LOGGER.warning("No video info extracted")
                    return None

                # Get the direct URL
                video_url = None

                # Check if it's a playlist
                if 'entries' in info:
                    # Get first video from playlist
                    entries = list(info['entries'])
                    if entries:
                        first_entry = entries[0]
                        video_url = first_entry.get('url') or first_entry.get('webpage_url')
                        _LOGGER.info("Extracted from playlist, first entry")
                else:
                    # Single video
                    video_url = info.get('url')

                    # If no direct URL, try formats
                    if not video_url and 'formats' in info:
                        formats = info['formats']
                        # Find best format
                        for fmt in reversed(formats):
                            if fmt.get('url'):
                                video_url = fmt['url']
                                _LOGGER.info(
                                    "Using format: %s (%s)",
                                    fmt.get('format_id', 'unknown'),
                                    fmt.get('ext', 'unknown')
                                )
                                break

                    # Fallback to manifest URL for HLS/DASH
                    if not video_url:
                        video_url = info.get('manifest_url')
                        if video_url:
                            _LOGGER.info("Using manifest URL")

                if video_url:
                    _LOGGER.info("Successfully extracted video URL")
                    _LOGGER.debug("Video URL: %s", video_url)
                    return video_url
                else:
                    _LOGGER.warning("Could not find video URL in extracted info")
                    _LOGGER.debug("Info keys: %s", list(info.keys()))
                    return None

        except Exception as e:
            error_str = str(e)
            if "Unsupported URL" in error_str:
                _LOGGER.error(
                    "yt-dlp: Unsupported URL. This may be a homepage, not a video page. "
                    "Navigate to a specific video first."
                )
            else:
                _LOGGER.error("yt-dlp extraction error: %s", e)
            return None

    async def get_video_info(self) -> dict[str, Any] | None:
        """Get full video information."""
        try:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(_executor, self._get_info)
        except Exception as e:
            _LOGGER.error("Error getting video info: %s", e)
            return None

    def _get_info(self) -> dict[str, Any] | None:
        """Get video info synchronously."""
        try:
            import yt_dlp
        except ImportError:
            return None

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.stream_url, download=False)

                if info:
                    return {
                        'title': info.get('title', 'Unknown'),
                        'duration': info.get('duration'),
                        'thumbnail': info.get('thumbnail'),
                        'description': info.get('description', ''),
                        'uploader': info.get('uploader', ''),
                        'url': info.get('url') or info.get('webpage_url'),
                        'is_live': info.get('is_live', False),
                        'formats': len(info.get('formats', [])),
                    }
                return None

        except Exception as e:
            _LOGGER.error("Error getting video info: %s", e)
            return None


async def extract_with_ytdlp(url: str) -> str | None:
    """Convenience function to extract video URL."""
    extractor = YtdlpExtractor(url)
    return await extractor.get_video_url()
