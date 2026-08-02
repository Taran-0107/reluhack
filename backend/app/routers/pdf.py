from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.routers.research import load_research
from app.services.pdf_service import pdf_service
from app.schemas.research import ResearchResult

router = APIRouter(prefix="/pdf", tags=["PDF"])

@router.get("/{company_name}")
async def download_pdf(company_name: str):
    data = load_research(company_name)
    if not data:
        raise HTTPException(status_code=404, detail="Company research not found. Run research first.")
    
    data.pop("_created_at", None)
    result = ResearchResult(**data)
    pdf_buffer = pdf_service.generate_report(result)
    
    headers = {
        'Content-Disposition': f'attachment; filename="{result.company_name.value.replace(" ", "_")}_report.pdf"'
    }
    
    return StreamingResponse(pdf_buffer, media_type="application/pdf", headers=headers)
