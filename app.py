
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, PageBreak, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
import os
from PIL import Image as PIL_Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register a custom font
try:
    pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
except:
    # Fallback to default font if Arial not available
    pass

# Ensure matplotlib uses non-GUI backend
import matplotlib
matplotlib.use('Agg')

# --- Helper Functions ---

def parse_text_file(file_path):
    """Improved text file parser with better error handling"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return {'error': f"Error reading file: {str(e)}"}

    data = {'title': 'Analysis Report', 'sections': []}
    current_section = {}
    is_table = False
    table_data = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("---"):
            if current_section:
                if is_table:
                    current_section['content'] = table_data
                    current_section['type'] = 'table'
                data['sections'].append(current_section)
            current_section = {}
            is_table = False
            table_data = []
            continue

        if line.startswith("# "):
            if current_section:
                data['sections'].append(current_section)
            current_section = {'title': line[2:].strip(), 'type': 'header'}
        elif line.startswith("## "):
            if current_section:
                data['sections'].append(current_section)
            current_section = {'title': line[3:].strip(), 'type': 'subheader'}
        elif line.startswith("### "):
            if current_section:
                data['sections'].append(current_section)
            current_section = {'title': line[4:].strip(), 'type': 'subsubsection'}
        elif line.startswith("Image: "):
             if current_section:
                data['sections'].append(current_section)
             current_section = {'title': line[7:].strip(), 'type': 'image'}
        elif line.startswith("Table:"):
            if current_section:
                data['sections'].append(current_section)
            current_section = {'title': line[6:].strip(), 'type': 'table'}
            is_table = True
            table_data = []
        elif is_table:
            row_data = line.split(',')
            table_data.append([item.strip() for item in row_data])
        else:
            if 'content' not in current_section:
                current_section['content'] = line
                current_section['type'] = 'paragraph'
            elif current_section['type'] == 'paragraph':
                current_section['content'] += "\n" + line
            else:
                current_section['content'] = line
                current_section['type'] = 'paragraph'

    if current_section:
        if is_table:
            current_section['content'] = table_data
            current_section['type'] = 'table'
        data['sections'].append(current_section)
    return data

def create_pdf(data, output_path="output.pdf"):
    """Enhanced PDF generator with better formatting"""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Define professional color scheme
    primary_color = '#2563EB'  # Blue
    secondary_color = '#1E40AF'  # Darker Blue
    accent_color = '#DB2777'  # Pink
    text_color = '#1F2937'  # Dark Gray
    light_bg = '#F3F4F6'  # Light Gray

    # Create custom styles without redefining existing ones
    if 'TitleStyle' not in styles:
        styles.add(ParagraphStyle(
            name='TitleStyle',
            fontName='Helvetica-Bold',
            fontSize=28,
            leading=32,
            alignment=1,
            spaceAfter=20,
            textColor=primary_color
        ))
    
    if 'SectionHeader' not in styles:
        styles.add(ParagraphStyle(
            name='SectionHeader',
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            spaceBefore=20,
            spaceAfter=10,
            textColor=secondary_color
        ))
    
    if 'Subheader' not in styles:
        styles.add(ParagraphStyle(
            name='Subheader',
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            spaceBefore=15,
            spaceAfter=8,
            textColor=accent_color
        ))
    
    if 'TableTitle' not in styles:
        styles.add(ParagraphStyle(
            name='TableTitle',
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            spaceBefore=10,
            spaceAfter=5,
            textColor=secondary_color,
            alignment=1
        ))

    # Cover Page
    cover = []
    cover.append(Paragraph(data.get('title', 'Professional Report'), styles['TitleStyle']))
    cover.append(Spacer(1, 20))
    cover.append(Paragraph("Generated on: " + pd.Timestamp.now().strftime("%B %d, %Y"), 
                  ParagraphStyle(
                      name='CoverDate',
                      fontName='Helvetica',
                      fontSize=12,
                      alignment=1,
                      textColor=text_color
                  )))
    cover.append(PageBreak())
    elements.extend(cover)

    # Content
    for section in data['sections']:
        try:
            if section['type'] == 'header':
                elements.append(Paragraph(section['title'], styles['SectionHeader']))
                elements.append(Spacer(1, 12))
            elif section['type'] == 'subheader':
                elements.append(Paragraph(section['title'], styles['Subheader']))
                elements.append(Spacer(1, 8))
            elif section['type'] == 'subsubsection':
                elements.append(Paragraph(section['title'], 
                                       ParagraphStyle(
                                           name='SubSubheader',
                                           parent=styles['Subheader'],
                                           fontSize=14,
                                           textColor=primary_color
                                       )))
                elements.append(Spacer(1, 6))
            elif section['type'] == 'paragraph':
                # Handle multi-line paragraphs
                paragraphs = section['content'].split('\n')
                for para in paragraphs:
                    if para.strip():
                        elements.append(Paragraph(para, styles['Normal']))
                elements.append(Spacer(1, 8))
            elif section['type'] == 'table':
                elements.append(Paragraph(section['title'], styles['TableTitle']))
                table_data = section['content']
                
                if table_data and isinstance(table_data, list) and all(isinstance(row, list) for row in table_data):
                    # Create table with styling
                    table = Table(table_data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
                        ('TEXTCOLOR', (0, 0), (-1, 0), '#FFFFFF'),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), light_bg),
                        ('GRID', (0, 0), (-1, -1), 1, '#E5E7EB'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 5),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                    ]))
                    elements.append(table)
                    elements.append(Spacer(1, 12))
            elif section['type'] == 'image':
                img_path = section['title']
                if os.path.exists(img_path):
                    try:
                        img = PIL_Image.open(img_path)
                        img_width, img_height = img.size
                        max_width = 6 * inch
                        max_height = 7 * inch
                        
                        # Maintain aspect ratio
                        if img_width > max_width:
                            ratio = max_width / float(img_width)
                            img_height = float(img_height) * ratio
                            img_width = max_width
                        if img_height > max_height:
                            ratio = max_height / float(img_height)
                            img_width = float(img_width) * ratio
                            img_height = max_height
                            
                        elements.append(Paragraph(os.path.basename(img_path), 
                                               ParagraphStyle(
                                                   name='ImageTitle',
                                                   parent=styles['Normal'],
                                                   alignment=1
                                               )))
                        elements.append(Image(img_path, width=img_width, height=img_height))
                        elements.append(Spacer(1, 12))
                    except Exception as e:
                        elements.append(Paragraph(f"Error loading image: {str(e)}", styles['Normal']))
        except Exception as e:
            elements.append(Paragraph(f"Error processing section: {str(e)}", styles['Normal']))

    try:
        doc.build(elements)
        return True
    except Exception as e:
        print(f"PDF generation error: {str(e)}")
        return False

# --- Streamlit App with Modern UI and Logo ---
def main():
    st.set_page_config(
        page_title="Text to PDF Converter",
        page_icon="📄",
        layout="centered",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for modern look with logo
    st.markdown("""
    <style>
        /* Main container */
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #2d3748;
        }
        
        /* Header with logo */
        .header-container {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 30px;
        }
        
        .logo {
            height: 60px;
            margin-right: 20px;
        }
        
        .title {
            color: #2563eb;
            margin: 0;
        }
        
        /* File uploader */
        .stFileUploader > label {
            background-color: #2563eb;
            color: white;
            border-radius: 8px;
            padding: 12px 24px;
            transition: all 0.3s;
        }
        
        .stFileUploader > label:hover {
            background-color: #1d4ed8;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 500;
            transition: all 0.3s;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
            background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        }
        
        /* Input fields */
        .stTextInput input {
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            padding: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }
        
        /* Success message */
        .stAlert.stSuccess {
            background-color: #f0fdf4;
            border-left: 4px solid #10b981;
            border-radius: 8px;
        }
        
        /* Error message */
        .stAlert.stError {
            background-color: #fef2f2;
            border-left: 4px solid #ef4444;
            border-radius: 8px;
        }
        
        /* Spinner */
        .stSpinner > div {
            border: 3px solid rgba(37, 99, 235, 0.2);
            border-radius: 50%;
            border-top: 3px solid #2563eb;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="header-container">
        <img src="" class="logo">
        <h1 class="title">Text to PDF Converter</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("Transform your structured text files into professional PDF reports with ease.")

    col1, col2 = st.columns([3, 1])
    with col1:
        uploaded_file = st.file_uploader("Upload your text file", type=["txt"], 
                                        help="Upload a structured text file with headers, paragraphs, and tables")
    # with col2:
    #     st.markdown("""
    #     <div style="background-color: #e0e7ff; padding: 15px; border-radius: 10px; margin-top: 10px;">
    #         <p style="color: #1e40af; font-size: 14px; margin: 0;">Supports:</p>
    #         <ul style="color: #1e40af; font-size: 12px; margin: 5px 0 0 15px; padding: 0;">
    #             <li>Headers (#)</li>
    #             <li>Tables (Table:)</li>
    #             <li>Images (Image:)</li>
    #         </ul>
    #     </div>
    #     """, unsafe_allow_html=True)

    if uploaded_file is not None:
        with st.expander("Advanced Options", expanded=False):
            output_path = st.text_input("Output PDF path", "report.pdf")
            st.markdown("### PDF Settings")
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Report Title", "Analysis Report")
            with col2:
                show_date = st.checkbox("Include date", value=True)

        if st.button("Generate PDF", type="primary"):
            with st.spinner("Creating your professional PDF..."):
                # Save uploaded file
                temp_file = "temp_upload.txt"
                with open(temp_file, "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                # Parse and create PDF
                data = parse_text_file(temp_file)
                if 'error' not in data:
                    data['title'] = title  # Use custom title
                    success = create_pdf(data, output_path)
                    
                    if success:
                        st.success("PDF generated successfully!")
                        with open(output_path, "rb") as f:
                            st.download_button(
                                label="Download PDF",
                                data=f,
                                file_name=os.path.basename(output_path),
                                mime="application/pdf"
                            )
                    else:
                        st.error("Failed to generate PDF. Please check your file format.")
                else:
                    st.error(data['error'])
                
                # Clean up
                if os.path.exists(temp_file):
                    os.remove(temp_file)

if __name__ == "__main__":
    main()