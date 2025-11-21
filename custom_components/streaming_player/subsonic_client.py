"""Subsonic API client for Navidrome integration."""
from __future__ import annotations

import hashlib
import logging
import random
import string
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)


class SubsonicClient:
    """Client for Subsonic/Navidrome API."""

    def __init__(
        self,
        server_url: str,
        username: str,
        password: str,
    ) -> None:
        """Initialize the Subsonic client."""
        self._server_url = server_url.rstrip("/")
        self._username = username
        self._password = password
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    def _generate_auth_params(self) -> dict[str, str]:
        """Generate authentication parameters for Subsonic API."""
        # Generate random salt
        salt = "".join(random.choices(string.ascii_letters + string.digits, k=12))
        # Create token: md5(password + salt)
        token = hashlib.md5((self._password + salt).encode()).hexdigest()

        return {
            "u": self._username,
            "t": token,
            "s": salt,
            "v": "1.16.1",
            "c": "HomeAssistant",
            "f": "json",
        }

    async def _api_request(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
        """Make API request to Subsonic server."""
        try:
            session = await self._get_session()
            url = f"{self._server_url}/rest/{endpoint}"

            request_params = self._generate_auth_params()
            if params:
                request_params.update(params)

            async with session.get(url, params=request_params) as response:
                if response.status != 200:
                    _LOGGER.error("Subsonic API error: %s", response.status)
                    return None

                data = await response.json()

                if "subsonic-response" not in data:
                    _LOGGER.error("Invalid Subsonic response")
                    return None

                resp = data["subsonic-response"]
                if resp.get("status") != "ok":
                    error = resp.get("error", {})
                    _LOGGER.error("Subsonic error: %s", error.get("message", "Unknown"))
                    return None

                return resp

        except Exception as e:
            _LOGGER.error("Subsonic API request failed: %s", e)
            return None

    async def ping(self) -> bool:
        """Test connection to Subsonic server."""
        result = await self._api_request("ping")
        return result is not None

    async def get_genres(self) -> list[dict[str, Any]]:
        """Get list of all genres."""
        result = await self._api_request("getGenres")
        if not result:
            return []

        genres = result.get("genres", {}).get("genre", [])
        # Ensure it's a list
        if isinstance(genres, dict):
            genres = [genres]

        return genres

    async def get_songs_by_genre(
        self,
        genre: str,
        count: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Get songs by genre."""
        result = await self._api_request(
            "getSongsByGenre",
            {"genre": genre, "count": count, "offset": offset},
        )
        if not result:
            return []

        songs = result.get("songsByGenre", {}).get("song", [])
        if isinstance(songs, dict):
            songs = [songs]

        return songs

    async def get_random_songs(
        self,
        size: int = 20,
        genre: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get random songs, optionally filtered by genre."""
        params = {"size": size}
        if genre:
            params["genre"] = genre

        result = await self._api_request("getRandomSongs", params)
        if not result:
            return []

        songs = result.get("randomSongs", {}).get("song", [])
        if isinstance(songs, dict):
            songs = [songs]

        return songs

    async def get_artists(self) -> list[dict[str, Any]]:
        """Get all artists."""
        result = await self._api_request("getArtists")
        if not result:
            return []

        artists = []
        indexes = result.get("artists", {}).get("index", [])
        if isinstance(indexes, dict):
            indexes = [indexes]

        for index in indexes:
            artist_list = index.get("artist", [])
            if isinstance(artist_list, dict):
                artist_list = [artist_list]
            artists.extend(artist_list)

        return artists

    async def get_albums(self, artist_id: str | None = None) -> list[dict[str, Any]]:
        """Get albums, optionally filtered by artist."""
        if artist_id:
            result = await self._api_request("getArtist", {"id": artist_id})
            if not result:
                return []
            albums = result.get("artist", {}).get("album", [])
        else:
            result = await self._api_request("getAlbumList2", {"type": "alphabeticalByName", "size": 500})
            if not result:
                return []
            albums = result.get("albumList2", {}).get("album", [])

        if isinstance(albums, dict):
            albums = [albums]

        return albums

    async def get_album_songs(self, album_id: str) -> list[dict[str, Any]]:
        """Get songs from an album."""
        result = await self._api_request("getAlbum", {"id": album_id})
        if not result:
            return []

        songs = result.get("album", {}).get("song", [])
        if isinstance(songs, dict):
            songs = [songs]

        return songs

    async def get_playlists(self) -> list[dict[str, Any]]:
        """Get all playlists."""
        result = await self._api_request("getPlaylists")
        if not result:
            return []

        playlists = result.get("playlists", {}).get("playlist", [])
        if isinstance(playlists, dict):
            playlists = [playlists]

        return playlists

    async def get_playlist_songs(self, playlist_id: str) -> list[dict[str, Any]]:
        """Get songs from a playlist."""
        result = await self._api_request("getPlaylist", {"id": playlist_id})
        if not result:
            return []

        songs = result.get("playlist", {}).get("entry", [])
        if isinstance(songs, dict):
            songs = [songs]

        return songs

    def get_stream_url(self, song_id: str, format: str = "mp3") -> str:
        """Get streaming URL for a song."""
        params = self._generate_auth_params()
        params["id"] = song_id
        params["format"] = format

        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self._server_url}/rest/stream?{query}"

    def get_cover_art_url(self, cover_id: str, size: int = 300) -> str:
        """Get cover art URL."""
        params = self._generate_auth_params()
        params["id"] = cover_id
        params["size"] = str(size)

        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self._server_url}/rest/getCoverArt?{query}"

    async def search(self, query: str) -> dict[str, list]:
        """Search for artists, albums, and songs."""
        result = await self._api_request("search3", {"query": query})
        if not result:
            return {"artists": [], "albums": [], "songs": []}

        search_result = result.get("searchResult3", {})

        artists = search_result.get("artist", [])
        if isinstance(artists, dict):
            artists = [artists]

        albums = search_result.get("album", [])
        if isinstance(albums, dict):
            albums = [albums]

        songs = search_result.get("song", [])
        if isinstance(songs, dict):
            songs = [songs]

        return {
            "artists": artists,
            "albums": albums,
            "songs": songs,
        }

    async def close(self) -> None:
        """Close the client session."""
        if self._session and not self._session.closed:
            await self._session.close()
