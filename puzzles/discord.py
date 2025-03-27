import os
import urllib.parse
from typing import Any

import requests
from django.conf import settings

DISCORD_IMAGE_BASE_URL = "https://cdn.discordapp.com"
DISCORD_API_BASE_URL = "https://discord.com/api/v10"


JsonDict = dict[str, Any]

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
if not DISCORD_TOKEN:
    DISCORD_TOKEN = settings.DISCORD_TOKEN


class DiscordClient:

    @staticmethod
    def _raw_request(method: str, endpoint: str, json: Any = None) -> requests.Response:
        """Send a request to discord and return the response"""
        headers = {
            "Authorization": f"Bot {DISCORD_TOKEN}",
            "X-Audit-Log-Reason": "via MH24-site integration",
        }
        api_url = f"{DISCORD_API_BASE_URL}{endpoint}"
        if method in ["get", "delete"]:
            return requests.request(method, api_url, headers=headers)
        elif method in ["patch", "post", "put"]:
            headers["Content-Type"] = "application/json"
            return requests.request(method, api_url, headers=headers, json=json)
        msg = f"Unknown method {method}"
        raise ValueError(msg)

    @staticmethod
    def _request(method: str, endpoint: str, json: Any = None) -> Any:
        resp = DiscordClient._raw_request(method, endpoint, json)
        if resp.status_code == 204:  # No Content
            return {}
        content = resp.json()
        resp.raise_for_status()
        return content

    @staticmethod
    def post_message(channel_id: str, payload: str | JsonDict) -> JsonDict:
        """Post a message to a channel.

        Messages will be split into chunks of at most 2000 characters.

        Payload can be a dict following the discord API, or a string; a string
        will be treated as dict(content=payload).
        """
        pth = f"/channels/{channel_id}/messages"
        # handle whether it's a string or JsonDict
        message = payload if isinstance(payload, str) else payload.get("content", "")
        offset = 0
        while True:
            chunk = message[offset : offset + 2000]
            # possibly chunk but try to preserve whole words
            # inspiration from https://github.com/fixmyrights/discord-bot/issues/11
            if offset + 2000 < len(message):
                reversed_chunk = chunk[::-1]
                length = min(reversed_chunk.find("\n"), reversed_chunk.find(" "))
                chunk = chunk[: 2000 - length]
                offset += 2000 - length
            else:
                offset = len(message)
            # if it's a JsonDict, try to keep the other attributes around
            if isinstance(payload, str):
                payload = {"content": chunk}
            else:
                payload["content"] = chunk
            if offset == len(message):
                return DiscordClient._request("post", pth, payload)
            else:
                DiscordClient._request("post", pth, payload)

    @staticmethod
    def edit_message(channel_id: str, msg_id: str, payload: str | JsonDict) -> JsonDict:
        pth = f"/channels/{channel_id}/messages/{msg_id}"
        payload = {"content": payload} if isinstance(payload, str) else payload
        return DiscordClient._request("patch", pth, payload)

    @staticmethod
    def search_user(guild_id: str, query: str, limit: int = 1):
        pth = f"/guilds/{guild_id}/members/search?"
        pth += urllib.parse.urlencode({"query": query, "limit": limit})
        return DiscordClient._request("get", pth)
