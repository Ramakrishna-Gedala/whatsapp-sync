import httpx
from fastapi import HTTPException
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_limits = httpx.Limits(max_connections=20, max_keepalive_connections=10)


class GreenAPIService:
    def __init__(self):
        self.base_url = settings.GREEN_API_BASE_URL
        self.instance_id = settings.GREEN_API_INSTANCE_ID
        self.token = settings.GREEN_API_TOKEN

    def _url(self, path: str) -> str:
        return f"{self.base_url}/waInstance{self.instance_id}/{path}/{self.token}"

    async def get_groups(self) -> list[dict]:
        url = self._url("getChats")
        logger.info(f"Fetching WhatsApp groups from Green API: {url}")
        try:
            async with httpx.AsyncClient(limits=_limits, timeout=30) as client:
                response = await client.get(url)
                response.raise_for_status()
                chats = response.json()

            groups = []
            for chat in chats:
                chat_id = chat.get("id", "")
                if chat_id.endswith("@g.us"):
                    groups.append({
                        "id": chat_id,
                        "name": chat.get("name") or chat.get("subject") or chat_id,
                        "description": chat.get("description"),
                        "participants_count": chat.get("participantsCount", 0),
                    })

            logger.info(f"Found {len(groups)} WhatsApp groups")
            return groups

        except httpx.HTTPStatusError as e:
            logger.error(f"Green API HTTP error: {e.response.status_code} - {e.response.text}")
            raise HTTPException(
                status_code=502,
                detail=f"Green API error: {e.response.status_code}",
            )
        except httpx.RequestError as e:
            logger.error(f"Green API request error: {e}")
            raise HTTPException(status_code=502, detail="Could not connect to Green API")

    async def get_chat_history(self, chat_id: str, count: int = 20) -> list[dict]:
        url = self._url("getChatHistory")
        logger.info(f"Fetching chat history for {chat_id}, count={count}")
        logger.info(f"Green API URL: {url}")
        try:
            async with httpx.AsyncClient(limits=_limits, timeout=3000) as client:
                response = await client.post(
                    url, json={"chatId": chat_id, "count": count}
                )
                response.raise_for_status()
                messages = response.json()

            logger.info(f"Retrieved {len(messages)} messages from {chat_id}")
            return messages if isinstance(messages, list) else []

        except httpx.HTTPStatusError as e:
            logger.error(f"Green API HTTP error: {e.response.status_code} - {e.response.text}")
            raise HTTPException(
                status_code=502,
                detail=f"Green API error fetching history: {e.response.status_code}",
            )
        except httpx.RequestError as e:
            logger.error(f"Green API request error: {e}")
            raise HTTPException(status_code=502, detail="Could not connect to Green API")

    async def send_message(self, chat_id: str, message: str) -> dict:
        url = self._url("sendMessage")
        try:
            async with httpx.AsyncClient(limits=_limits, timeout=30) as client:
                response = await client.post(
                    url, json={"chatId": chat_id, "message": message}
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Green API send error: {e.response.status_code}")
            raise HTTPException(
                status_code=502,
                detail=f"Failed to send message: {e.response.status_code}",
            )
        except httpx.RequestError as e:
            logger.error(f"Green API request error: {e}")
            raise HTTPException(status_code=502, detail="Could not connect to Green API")


green_api_service = GreenAPIService()
