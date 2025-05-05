import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
from datetime import datetime
import re
import base64
import matplotlib
matplotlib.use('Agg')  # Set non-interactive backend for matplotlib

def extract_data_from_text(text):
    """
    Extract data from text for visualization.
    This is a simple implementation that looks for patterns like "Category: Value"
    """
    data = {}
    
    # Simple pattern matching for "Category: Value" or "Category - Value"
    patterns = [
        r'([A-Za-z\s]+):\s*(\d+\.?\d*)',  # Category: 123
        r'([A-Za-z\s]+)-\s*(\d+\.?\d*)',   # Category - 123
        r'([A-Za-z\s]+)\s+(\d+\.?\d*)'     # Category 123
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            category = match[0].strip()
            try:
                value = float(match[1])
                data[category] = value
            except ValueError:
                continue
    
    # If no data found, create sample data
    if not data:
        data = {
            'Category A': 65, 
            'Category B': 85, 
            'Category C': 45, 
            'Category D': 75, 
            'Category E': 55
        }
    
    return data

def create_streamlit_chart(data, theme_color='#2c3e50'):
    """Create and display a chart directly in Streamlit"""
    # Convert dict to DataFrame for plotting
    df = pd.DataFrame(list(data.items()), columns=['Category', 'Value'])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create a professional color palette
    colors = plt.cm.viridis(np.linspace(0, 0.8, len(data.keys())))
    
    # Plot the data
    bars = ax.bar(df['Category'], df['Value'], color=colors)
    
    # Enhanced styling
    ax.set_xlabel("Categories", fontsize=14, fontweight='bold', color=theme_color)
    ax.set_ylabel("Values", fontsize=14, fontweight='bold', color=theme_color)
    plt.title("Data Analysis Overview", fontsize=18, fontweight='bold', color=theme_color, pad=15)
    
    # Add value labels
    for i, v in enumerate(data.values()):
        ax.text(i, v, f'{v:,.0f}', ha='center', va='bottom', 
                fontsize=12, fontweight='bold', color=theme_color)
    
    # Customize grid and spines
    plt.grid(True, linestyle='--', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(theme_color)
    ax.spines['bottom'].set_color(theme_color)
    
    # Background colors
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#ffffff')
    
    plt.xticks(rotation=45, ha='right', color=theme_color)
    plt.tight_layout()
    
    return fig

def create_chart_for_pdf(data, filename='temp_chart.png', dpi=150):
    """Create a chart and save it as an image for PDF embedding"""
    fig = create_streamlit_chart(data)
    plt.savefig(filename, format='png', dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    return filename

def create_data_table(data, theme_color='#2c3e50'):
    """Create a ReportLab table from chart data"""
    # Prepare data for table format
    table_data = [['Category', 'Value']]  # Header row
    
    for category, value in data.items():
        table_data.append([category, f"{value:,.0f}"])
    
    # Create table style
    style = TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor(theme_color)),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
    ])
    
    # Add alternating row colors for better readability
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f2f2f2'))
    
    table = Table(table_data, colWidths=[300, 200])
    table.setStyle(style)
    
    return table

def create_pdf(content, data, output_pdf='output.pdf', company_name="", report_title=""):
    """Create PDF report with embedded chart and data from analysis text"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        rightMargin=72, 
        leftMargin=72, 
        topMargin=72, 
        bottomMargin=72
    )
    story = []
    styles = getSampleStyleSheet()
    theme_color = '#2c3e50'
    
    # Enhanced styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        spaceAfter=30,
        textColor=colors.HexColor(theme_color),
        alignment=1,
        fontName='Helvetica-Bold',
        leading=34
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=20,
        textColor=colors.HexColor('#34495e'),
        alignment=1,
        fontName='Helvetica-Bold',
        spaceAfter=20
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        spaceAfter=12,
        textColor=colors.HexColor(theme_color),
        fontName='Helvetica',
        alignment=0
    )
    
    # Add company name if provided
    if company_name:
        company = Paragraph(company_name, title_style)
        story.append(company)
        story.append(Spacer(1, 20))
    
    # Report title with enhanced styling
    title = Paragraph(report_title if report_title else "Professional Analysis Report", title_style)
    story.append(title)
    
    # Add date with styled format
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#7f8c8d'),
        alignment=1,
        fontName='Helvetica-Oblique'
    )
    date_text = Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M')}", date_style)
    story.append(date_text)
    story.append(Spacer(1, 30))
    
    # Executive Summary section
    story.append(Paragraph("Executive Summary", subtitle_style))
    
    # Process and format the input text
    sections = re.split(r'\n\s*\n', content)
    for section in sections:
        if section.strip():
            p = Paragraph(section.strip(), body_style)
            story.append(p)
            story.append(Spacer(1, 15))
    
    # Add visualization section
    story.append(Spacer(1, 20))
    story.append(Paragraph("Data Visualization", subtitle_style))
    
    # Add explanatory text for the chart
    data_intro = Paragraph(
        "Below is a visual representation of the key data points analyzed in this report:", 
        body_style
    )
    story.append(data_intro)
    story.append(Spacer(1, 15))
    
    # Create chart and add it to the PDF
    chart_file = create_chart_for_pdf(data)
    img = Image(chart_file, width=450, height=250)
    story.append(img)
    story.append(Spacer(1, 20))
    
    # Add data table
    table = create_data_table(data, theme_color)
    story.append(table)
    
    # Add data interpretation section
    interpretation_style = ParagraphStyle(
        'Interpretation',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        spaceAfter=12,
        textColor=colors.HexColor('#34495e'),
        fontName='Helvetica',
        alignment=0
    )
    
    # Create data interpretation text
    highest_cat = max(data.items(), key=lambda x: x[1])
    lowest_cat = min(data.items(), key=lambda x: x[1])
    avg_value = sum(data.values()) / len(data)
    
    interpretation = Paragraph(
        f"<b>Data Interpretation:</b> The analysis above displays the values across {len(data)} key categories. "
        f"<b>{highest_cat[0]}</b> shows the highest value at {highest_cat[1]:,.0f} points, while "
        f"<b>{lowest_cat[0]}</b> has the lowest at {lowest_cat[1]:,.0f} points. "
        f"The average value across all categories is {avg_value:,.1f} points.",
        interpretation_style
    )
    story.append(Spacer(1, 15))
    story.append(interpretation)
    
    # Add footer with styling
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#95a5a6'),
        alignment=1,
        fontName='Helvetica'
    )
    footer = Paragraph(
        f" {company_name if company_name else ''}  "
        f"Generated on {datetime.now().strftime('%Y-%m-%d')}",
        footer_style
    )
    story.append(Spacer(1, 30))
    story.append(footer)
    
    # Build the PDF
    doc.build(story)
    
    # Get the PDF data and return
    pdf_data = buffer.getvalue()
    buffer.close()
    
    # Save the buffer to a file
    with open(output_pdf, 'wb') as f:
        f.write(pdf_data)
    
    return pdf_data

def get_download_link(pdf_bytes, filename="report.pdf"):
    """Generate a download link for the PDF"""
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Download PDF Report</a>'
    return href

def main():
    st.set_page_config(page_title="Analysis Report Generator", layout="wide")
    
    # Enhanced UI styling
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
            background-color: #ffffff;
        }
        .stTitle {
            color: #2c3e50;
            font-size: 2.8rem;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: 700;
        }
        .stButton>button {
            background-color: #3498db;
            color: white;
            padding: 0.6rem 2rem;
            border-radius: 8px;
            font-weight: 600;
            border: none;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #2980b9;
            transform: translateY(-2px);
        }
        .report-header {
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;
            border-left: 5px solid #3498db;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🚀 Professional Analysis Report Generator")
    
    with st.container():
        st.markdown('<div class="report-header">', unsafe_allow_html=True)
        st.info("💫 Transform your analysis text into a professional client-ready PDF report with embedded data visualization")
        st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("📝 Input Your Analysis")
        text_input = st.text_area("Enter your analysis text here (or upload a file below)", 
                                 height=250, 
                                 help="Enter any analysis text. The system will automatically extract numeric data for visualization.")
        
        uploaded_file = st.file_uploader("📄 Or Upload Analysis Text File", type=["txt"])
        
        # Get content from either text area or uploaded file
        content = ""
        if uploaded_file is not None:
            content = uploaded_file.getvalue().decode("utf-8")
            st.success("✅ Analysis file uploaded successfully!")
            # Show the content in the text area for editing
            text_input = st.text_area("Edit your analysis text if needed:", 
                                     value=content, 
                                     height=250)
            content = text_input
        else:
            content = text_input
        
        # Company and report details
        st.subheader("📊 Report Details")
        company_name = st.text_input("🏢 Company Name")
        report_title = st.text_input("📑 Report Title")
        
    with col2:
        st.subheader("⚙️ Features")
        st.markdown("""
        - ✨ Professional Layout & Design
        - 📊 Auto-generated Charts from Text
        - 📋 Data Tables with Analysis
        - 🎨 Custom Branding Options
        - 📱 Mobile-friendly PDF Reports
        """)
        
        st.subheader("ℹ️ How It Works")
        st.markdown("""
        1. Enter your analysis text or upload a file
        2. Our system automatically extracts any numeric data
        3. Preview the generated chart visualization
        4. Generate a professional PDF report
        5. Download and share with clients
        """)
    
    # Only proceed if there's content
    if content:
        # Extract data from the text
        data = extract_data_from_text(content)
        
        # Display data preview
        st.subheader("📊 Data Extracted for Visualization")
        df = pd.DataFrame(list(data.items()), columns=['Category', 'Value'])
        st.dataframe(df)
        
        # Show a live chart preview in Streamlit
        st.subheader("📈 Chart Preview")
        fig = create_streamlit_chart(data)
        st.pyplot(fig)
        
        if st.button("🎯 Generate Professional Report", key="generate_report"):
            with st.spinner("🔄 Creating your professional report..."):
                output_pdf = f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                
                try:
                    # Generate the PDF with the chart embedded
                    pdf_data = create_pdf(content, data, output_pdf, company_name, report_title)
                    
                    st.success("🎉 Your professional report is ready!")
                    
                    # Provide download button for the report
                    st.download_button(
                        label="📥 Download Report PDF",
                        data=pdf_data,
                        file_name=output_pdf,
                        mime="application/pdf",
                        key="download_report"
                    )
                    
                    # Show a success message with additional instructions
                    st.info("Your PDF report includes the analysis text, data visualization, and a data table. Share it with your team or clients!")
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")
                    st.info("Please check your input data and try again.")

if __name__ == "__main__":
    main()