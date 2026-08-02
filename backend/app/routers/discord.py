from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.discord_service import discord_service
from app.services.pdf_service import pdf_service
from app.routers.research import load_research
from app.schemas.research import ResearchResult

router = APIRouter(prefix="/discord", tags=["Discord"])

class DiscordSendRequest(BaseModel):
    discord_bot_token: str
    discord_channel_id: str
    applicant_name: str = ""
    applicant_email: str = ""

@router.post("/send/{company_name}")
async def send_to_discord(company_name: str, config: DiscordSendRequest):
    # 1. Load history
    data = load_research(company_name)
    if not data:
        raise HTTPException(status_code=404, detail="Company research not found.")
        
    data.pop("_created_at", None)
    result = ResearchResult(**data)
    
    # 2. Generate PDF
    pdf_bytes = pdf_service.generate_report(result).getvalue()
    
    # 3. Send
    await discord_service.send_research_completed(
        data=result,
        pdf_bytes=pdf_bytes,
        bot_token=config.discord_bot_token,
        channel_id=config.discord_channel_id,
        applicant_name=config.applicant_name,
        applicant_email=config.applicant_email
    )
    
    return {"message": "Sent to Discord successfully."}
