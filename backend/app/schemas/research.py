from pydantic import BaseModel, Field
from typing import List, Optional

class ResearchRequest(BaseModel):
    company_name: Optional[str] = None
    website_url: Optional[str] = None
    discord_bot_token: Optional[str] = None
    discord_channel_id: Optional[str] = None
    applicant_name: Optional[str] = None
    applicant_email: Optional[str] = None
    
class Competitor(BaseModel):
    name: str
    website: Optional[str] = None
    description: Optional[str] = None

class ResearchResult(BaseModel):
    company_name: str = Field(description="The name of the company")
    website: str = Field(description="The official website of the company")
    phone_number: Optional[str] = Field(None, description="Contact phone number if available")
    address: Optional[str] = Field(None, description="Physical or mailing address if available")
    products_services: List[str] = Field(description="List of products or services offered by the company")
    pain_points: List[str] = Field(description="AI-generated pain points that the company solves or faces")
    competitors: List[Competitor] = Field(description="List of competitors in the same space")
    summary: str = Field(description="A brief summary of what the company does")
