import httpx
import json
from typing import Optional
from app.utils.logger import logger
from app.schemas.research import ResearchResult

class DiscordService:
    async def send_research_completed(
        self, 
        data: ResearchResult, 
        pdf_bytes: bytes, 
        bot_token: Optional[str] = None, 
        channel_id: Optional[str] = None,
        applicant_name: Optional[str] = None,
        applicant_email: Optional[str] = None
    ):
        if not bot_token or not channel_id:
            logger.info("Discord bot token or channel ID not provided. Skipping message.")
            return

        # Handle case where user pastes full Discord URL instead of just the ID
        if "/" in channel_id:
            channel_id = channel_id.strip("/").split("/")[-1]

        url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
        headers = {
            "Authorization": f"Bot {bot_token}"
            # Do NOT set Content-Type to multipart/form-data manually, httpx will do it and set the boundary.
        }

        embed = {
            "title": f"Research Completed: {data.company_name}",
            "url": data.website if data.website.startswith("http") else f"https://{data.website}",
            "color": 16766720, # Amber-400
            "fields": [
                {
                    "name": "Company Name",
                    "value": data.company_name,
                    "inline": True
                },
                {
                    "name": "Company Website",
                    "value": data.website,
                    "inline": True
                }
            ]
        }

        if applicant_name or applicant_email:
            embed["fields"].insert(0, {
                "name": "Applicant Details",
                "value": f"**Name:** {applicant_name or 'N/A'}\n**Email:** {applicant_email or 'N/A'}",
                "inline": False
            })

        payload_json = {
            "content": "A new Research Report has been generated!",
            "embeds": [embed]
        }

        data_payload = {
            "payload_json": json.dumps(payload_json)
        }

        files = {
            "files[0]": (f"{data.company_name}_Research_Report.pdf", pdf_bytes, "application/pdf")
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, data=data_payload, files=files)
                response.raise_for_status()
                logger.info("Successfully sent research update to Discord via Bot API.")
            except Exception as e:
                logger.error(f"Failed to send Discord message: {e}")
                if hasattr(e, 'response') and e.response:
                    logger.error(f"Response: {e.response.text}")

discord_service = DiscordService()
