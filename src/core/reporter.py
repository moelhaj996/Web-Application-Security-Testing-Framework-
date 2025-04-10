from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
import pandas as pd
from typing import Dict, Any
import logging

class SecurityReporter:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='report_generation.log'
        )
        
    def create_pdf_report(self, scan_results: Dict[str, Any], output_file: str):
        """Generate PDF security report"""
        doc = SimpleDocTemplate(
            output_file,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        story.append(Paragraph("Security Assessment Report", title_style))
        
        # Scan Information
        story.append(Paragraph(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Vulnerability Summary
        story.append(Paragraph("Vulnerability Summary", self.styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Create vulnerability table
        data = [['Vulnerability Type', 'Count', 'Severity']]
        for vuln_type, results in scan_results.items():
            count = len(results)
            severity = self._determine_severity(vuln_type, results)
            data.append([vuln_type, str(count), severity])
            
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 12))
        
        # Detailed Findings
        story.append(Paragraph("Detailed Findings", self.styles['Heading2']))
        story.append(Spacer(1, 12))
        
        for vuln_type, results in scan_results.items():
            if results:
                story.append(Paragraph(f"{vuln_type.upper()} Findings", self.styles['Heading3']))
                for result in results:
                    story.append(Paragraph(f"• {result.get('description', 'No description available')}", self.styles['Normal']))
                story.append(Spacer(1, 12))
        
        # Recommendations
        story.append(Paragraph("Recommendations", self.styles['Heading2']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(self._generate_recommendations(scan_results), self.styles['Normal']))
        
        doc.build(story)
        logging.info(f"PDF report generated successfully: {output_file}")
        
    def _determine_severity(self, vuln_type: str, results: list) -> str:
        """Determine the severity level based on vulnerability type and results"""
        if not results:
            return "None"
            
        severity_map = {
            'xss': 'High',
            'sql_injection': 'Critical',
            'csrf': 'Medium'
        }
        return severity_map.get(vuln_type, 'Unknown')
        
    def _generate_recommendations(self, scan_results: Dict[str, Any]) -> str:
        """Generate remediation recommendations based on scan results"""
        recommendations = []
        
        if scan_results.get('xss'):
            recommendations.append(
                "• Implement proper input validation and output encoding\n"
                "• Use Content Security Policy (CSP) headers\n"
                "• Sanitize user input before rendering"
            )
            
        if scan_results.get('sql_injection'):
            recommendations.append(
                "• Use parameterized queries or prepared statements\n"
                "• Implement proper input validation\n"
                "• Apply the principle of least privilege for database access"
            )
            
        if scan_results.get('csrf'):
            recommendations.append(
                "• Implement CSRF tokens\n"
                "• Use SameSite cookie attribute\n"
                "• Validate origin and referer headers"
            )
            
        return "\n\n".join(recommendations) if recommendations else "No specific recommendations based on scan results."
        
    def generate_excel_report(self, scan_results: Dict[str, Any], output_file: str):
        """Generate Excel security report"""
        df = pd.DataFrame()
        
        for vuln_type, results in scan_results.items():
            if results:
                vuln_df = pd.DataFrame(results)
                vuln_df['Vulnerability Type'] = vuln_type
                df = pd.concat([df, vuln_df], ignore_index=True)
                
        df.to_excel(output_file, index=False)
        logging.info(f"Excel report generated successfully: {output_file}") 