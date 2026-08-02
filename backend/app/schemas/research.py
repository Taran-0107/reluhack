from pydantic import BaseModel, Field
from typing import List, Optional, Generic, TypeVar

T = TypeVar('T')

class FieldMetadata(BaseModel, Generic[T]):
    value: T = Field(description="The actual value extracted")
    source: Optional[str] = Field(default=None, description="The source of the information (e.g., 'JSON-LD', 'Homepage', 'Inferred Insights')")
    confidence: Optional[float] = Field(default=0.0, description="Confidence score between 0 and 1")

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
    company_name: FieldMetadata[str] = Field(description="The name of the company")
    website: FieldMetadata[str] = Field(description="The official website of the company")
    phone_number: FieldMetadata[Optional[str]] = Field(description="Contact phone number if available")
    address: FieldMetadata[Optional[str]] = Field(description="Physical or mailing address if available")
    products_services: FieldMetadata[List[str]] = Field(description="List of products or services offered by the company")
    pain_points: FieldMetadata[List[str]] = Field(description="AI-generated pain points that the company solves or faces")
    competitors: FieldMetadata[List[Competitor]] = Field(description="List of competitors in the same space")
    summary: FieldMetadata[str] = Field(description="A brief summary of what the company does")
