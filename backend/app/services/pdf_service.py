from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from app.schemas.research import ResearchResult

class PDFService:
    def generate_report(self, data: ResearchResult) -> BytesIO:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = styles['Heading1']
        heading_style = styles['Heading2']
        normal_style = styles['Normal']
        
        story = []
        
        # Title
        story.append(Paragraph(f"Research Report: {data.company_name.value}", title_style))
        story.append(Spacer(1, 12))
        
        # Company Info
        story.append(Paragraph("Company Information", heading_style))
        story.append(Paragraph(f"<b>Website:</b> {data.website.value or 'N/A'}", normal_style))
        story.append(Paragraph(f"<b>Phone:</b> {data.phone_number.value or 'N/A'}", normal_style))
        story.append(Paragraph(f"<b>Address:</b> {data.address.value or 'N/A'}", normal_style))
        story.append(Spacer(1, 12))
        
        # Summary
        story.append(Paragraph("Summary", heading_style))
        story.append(Paragraph(data.summary.value, normal_style))
        story.append(Spacer(1, 12))
        
        # Products / Services
        story.append(Paragraph("Products / Services", heading_style))
        for item in data.products_services.value:
            story.append(Paragraph(f"&bull; {item}", normal_style))
        story.append(Spacer(1, 12))
        
        # Pain Points
        story.append(Paragraph("Pain Points Solved", heading_style))
        for item in data.pain_points.value:
            story.append(Paragraph(f"&bull; {item}", normal_style))
        story.append(Spacer(1, 12))
        
        # Competitors
        story.append(Paragraph("Competitors", heading_style))
        for comp in data.competitors.value:
            comp_text = f"<b>{comp.name}</b>"
            if comp.website:
                comp_text += f" ({comp.website})"
            if comp.description:
                comp_text += f": {comp.description}"
            story.append(Paragraph(f"&bull; {comp_text}", normal_style))
            
        doc.build(story)
        buffer.seek(0)
        return buffer

pdf_service = PDFService()
