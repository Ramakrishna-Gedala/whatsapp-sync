import json
from openai import AsyncOpenAI
from app.config import settings
from app.schemas.event import ParsedEventData
from app.utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """
You are an AI assistant for a US residential property management company.
Your job is to parse WhatsApp messages from tenants and staff in rental property group chats.
Extract structured information from each message and return ONLY valid JSON.

US Real Estate Terminology:
- Unit/Apt/Suite = individual rental unit (e.g., "Unit 4B", "Apt 12", "Suite 201")
- Community/Complex/Property = the apartment complex or community name
- HOA = Homeowners Association
- Common Area = shared spaces (lobby, gym, pool, parking)
- Lease = rental agreement
- Move-in/Move-out = tenant arrival/departure
- Work Order = maintenance request

Always return a JSON object with these exact fields:
{
  "event_type": one of ["maintenance_request","lease_inquiry","payment_issue","move_in","move_out","noise_complaint","safety_concern","amenity_request","general_inquiry","other"],
  "priority": one of ["low","medium","high","urgent"],
  "title": "concise 1-line summary (max 100 chars)",
  "description": "full structured description of the issue",
  "tenant_id": "extracted resident ID or null",
  "tenant_name": "tenant full name or null",
  "property_id": "unit identifier like 'Unit 4B' or null",
  "community_id": "community/complex name or null",
  "address": "full US address if mentioned or null",
  "confidence": 0.0 to 1.0 float representing how confident you are in the extraction
}
"""


class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def parse_message(self, raw_text: str, source: str = "whatsapp_group") -> dict:
        """Parse a raw message text into structured event data."""
        logger.info(f"Parsing message via OpenAI (source={source}), length={len(raw_text)}")

        user_prompt = f"""Parse this property management message and extract structured event data:

Message: {raw_text}

Return ONLY valid JSON with no markdown, no code blocks, just the raw JSON object."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                temperature=0.1,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
            )

            raw_content = response.choices[0].message.content
            logger.debug(f"OpenAI raw response: {raw_content}")

            parsed = json.loads(raw_content)

            # Validate with Pydantic
            validated = ParsedEventData(**parsed)

            return {
                "event_type": validated.event_type,
                "priority": validated.priority,
                "title": validated.title,
                "description": validated.description,
                "tenant_id": validated.tenant_id,
                "tenant_name": validated.tenant_name,
                "property_id": validated.property_id,
                "community_id": validated.community_id,
                "address": validated.address,
                "confidence": validated.confidence,
                "raw_response": parsed,
            }

        except Exception as e:
            logger.error(f"OpenAI parsing error: {e}")
            # Return a fallback with low confidence rather than failing hard
            return {
                "event_type": "other",
                "priority": "medium",
                "title": raw_text[:100] if raw_text else "Unknown event",
                "description": raw_text or "No description available",
                "tenant_id": None,
                "tenant_name": None,
                "property_id": None,
                "community_id": None,
                "address": None,
                "confidence": 0.1,
                "raw_response": {"error": str(e)},
            }

    # Future extensibility hooks
    async def parse_image(self, image_url: str, caption: str = "") -> dict:
        """Future: parse image messages."""
        raise NotImplementedError("Image parsing not yet implemented")

    async def parse_voice(self, audio_url: str) -> dict:
        """Future: parse voice messages via Whisper."""
        raise NotImplementedError("Voice parsing not yet implemented")

    async def parse_document(self, document_url: str, filename: str = "") -> dict:
        """Future: parse document attachments."""
        raise NotImplementedError("Document parsing not yet implemented")


openai_service = OpenAIService()
