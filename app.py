import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Image, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
from datetime import datetime
import re

def create_bar_chart(data, filename='chart.png', theme_color='#2c3e50'):
    plt.style.use('seaborn-v0_8')
    df = pd.DataFrame(data)
    
    # Create a professional color palette using matplotlib colors instead of seaborn
    colors = plt.cm.hsv(np.linspace(0, 1, len(data.keys())))
    
    fig, ax = plt.subplots(figsize=(15, 10))  # Increased figure size
    bars = df.plot(kind='bar', title="Data Overview", legend=True, ax=ax,
                  color=colors)
    
    # Enhanced styling
    ax.set_xlabel("Categories", fontsize=18, fontweight='bold', color=theme_color)  # Increased font size
    ax.set_ylabel("Values", fontsize=18, fontweight='bold', color=theme_color)  # Increased font size
    plt.title("Data Analysis Overview", fontsize=24, fontweight='bold', color=theme_color, pad=20)  # Increased font size
    
    # Add value labels on top of bars
    for i, v in enumerate(data.values()):
        ax.text(i, v[0], f'{v[0]:,.0f}', ha='center', va='bottom', 
                fontsize=14, fontweight='bold', color=theme_color)  # Increased font size
    
    # Customize grid and spines
    plt.grid(True, linestyle='--', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(theme_color)
    ax.spines['bottom'].set_color(theme_color)
    
    plt.xticks(rotation=45, ha='right', color=theme_color, fontsize=14)  # Increased font size
    plt.yticks(color=theme_color, fontsize=14)  # Increased font size
    
    # Add subtle background color
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#ffffff')
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def create_pdf(input_text, output_pdf='output.pdf', company_name="", report_title=""):
    doc = SimpleDocTemplate(output_pdf, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    story = []
    styles = getSampleStyleSheet()
    
    # Enhanced styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=34,
        spaceAfter=40,
        textColor=colors.HexColor('#2c3e50'),
        alignment=1,
        fontName='Helvetica-Bold',
        leading=40
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=24,  # Increased font size
        textColor=colors.HexColor('#34495e'),
        alignment=1,
        fontName='Helvetica-Bold',
        spaceAfter=30
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=12,
        leading=18,
        spaceAfter=12,
        textColor=colors.HexColor('#2c3e50'),
        fontName='Helvetica',
        alignment=0
    )
    
    # Add company logo placeholder
    if company_name:
        company = Paragraph(company_name, title_style)
        story.append(company)
        story.append(Spacer(1, 30))
    
    # Report title with enhanced styling
    title = Paragraph(report_title if report_title else "Professional Analysis Report", title_style)
    story.append(title)
    
    # Add date with styled format
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#7f8c8d'),
        alignment=1,
        fontName='Helvetica-Oblique'
    )
    date_text = Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M')}", date_style)
    story.append(date_text)
    story.append(Spacer(1, 40))
    
    # Executive Summary section
    story.append(Paragraph("Executive Summary", subtitle_style))
    
    # Process and format the input text
    with open(input_text, 'r') as file:
        content = file.read()
        
    # Split content into sections and format
    sections = re.split(r'\n\s*\n', content)
    for section in sections:
        if section.strip():
            p = Paragraph(section.strip(), body_style)
            story.append(p)
            story.append(Spacer(1, 20))
    
    # Add visualization section
    story.append(Spacer(1, 30))
    story.append(Paragraph("Data Visualization", subtitle_style))
    
    # Create and add charts
    data = {'Category A': [65], 'Category B': [85], 'Category C': [45], 
            'Category D': [75], 'Category E': [55]}
    create_bar_chart(data, 'analysis_chart.png')
    
    img = Image('analysis_chart.png', width=600, height=400)  # Increased image size
    story.append(img)
    story.append(Spacer(1, 30))
    
    # Add footer with styling
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#95a5a6'),
        alignment=1,
        fontName='Helvetica'
    )
    footer = Paragraph(
        f"Confidential Analysis Report | {company_name if company_name else 'Professional Report'} | "
        f"Generated on {datetime.now().strftime('%Y-%m-%d')}",
        footer_style
    )
    story.append(Spacer(1, 30))
    story.append(footer)
    
    # Build the PDF
    doc.build(story)

def main():
    st.set_page_config(page_title="Professional Report Generator", layout="wide")
    
    # Enhanced UI styling
    st.markdown("""
        <style>
        .main {
            padding: 3rem;
            background-color: #ffffff;
        }
        .stTitle {
            color: #2c3e50;
            font-size: 3.2rem;
            text-align: center;
            margin-bottom: 2.5rem;
            font-weight: 700;
        }
        .stButton>button {
            background-color: #3498db;
            color: white;
            padding: 0.7rem 2.5rem;
            border-radius: 8px;
            font-weight: 600;
            border: none;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #2980b9;
            transform: translateY(-2px);
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🚀 Professional Analysis Report Generator")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        uploaded_file = st.file_uploader("📄 Upload Analysis Text File", type=["txt"])
        company_name = st.text_input("🏢 Company Name")
        report_title = st.text_input("📑 Report Title")
        
    with col2:
        st.info("💫 Transform your analysis into a professional client-ready PDF report")
        st.markdown("""
        #### Features:
        ✨ Professional Layout & Design
        📊 Automated Data Visualization
        🎨 Custom Branding Options
        📑 Executive Summary Format
        """)
    
    if uploaded_file is not None:
        with open("analysis_input.txt", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success("✅ Analysis file uploaded successfully!")
        
        if st.button("🎯 Generate Professional Report", key="generate_report"):
            with st.spinner("🔄 Creating your professional report..."):
                output_pdf = f"professional_analysis_report_{datetime.now().strftime('%Y%m%d')}.pdf"
                create_pdf("analysis_input.txt", output_pdf, company_name, report_title)
                
                st.success("🎉 Your professional report is ready!")
                
                with open(output_pdf, "rb") as f:
                    st.download_button(
                        label="📥 Download Report",
                        data=f,
                        file_name=output_pdf,
                        mime="application/pdf",
                        key="download_report"
                    )

if __name__ == "__main__":
    main()