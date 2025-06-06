# backend/app/services/pdf_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, inch
from reportlab.lib.colors import HexColor, white, black, grey
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, KeepTogether, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Circle, Line, Rect
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF
from io import BytesIO
import os
import requests
from typing import Dict, List, Any
from PIL import Image as PILImage

class DatasheetGenerator:
    def __init__(self):
        self.width, self.height = A4
        self.margin = 15 * mm
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles matching the target design"""
        
        # Product title style
        self.styles.add(ParagraphStyle(
            name='ProductTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=black,
            spaceAfter=8,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            leftIndent=0
        ))
        
        # Section headers (dark grey background)
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=white,
            backColor=HexColor('#505050'),
            fontName='Helvetica-Bold',
            leftIndent=8,
            rightIndent=8,
            spaceBefore=2,
            spaceAfter=2,
            leading=16
        ))
        
        # Clean section headers (enhanced from first snippet)
        self.styles.add(ParagraphStyle(
            name='CleanSectionHeader',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=white,
            backColor=HexColor('#424242'),
            fontName='Helvetica-Bold',
            leftIndent=10,
            rightIndent=10,
            spaceBefore=3,
            spaceAfter=3,
            leading=18
        ))
        
        # Subsection headers (black background)
        self.styles.add(ParagraphStyle(
            name='SubSectionHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=white,
            backColor=HexColor('#2C2C2C'),
            fontName='Helvetica-Bold',
            leftIndent=6,
            rightIndent=6,
            spaceBefore=2,
            spaceAfter=2,
            leading=14
        ))
        
        # Small text for certifications
        self.styles.add(ParagraphStyle(
            name='SmallText',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=black,
            fontName='Helvetica',
            leading=10
        ))
        
        # Checkbox style
        self.styles.add(ParagraphStyle(
            name='CheckboxText',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=black,
            fontName='Helvetica',
            leading=12
        ))
    
    def generate_datasheet(self, product_data: Dict[str, Any]) -> BytesIO:
        """Generate optimized single-page datasheet"""
        print(f"=== PDF GENERATOR DEBUG ===")
        print(f"Product data keys: {list(product_data.keys())}")
        
        # Debug visual assets thoroughly
        visual_assets = product_data.get('visual_assets', {})
        print(f"Visual assets type: {type(visual_assets)}")
        print(f"Visual assets: {visual_assets}")
        
        if visual_assets:
            certifications = visual_assets.get('certifications', [])
            print(f"Certifications in generator: {len(certifications)} items")
            for i, cert in enumerate(certifications):
                print(f"  Generator cert {i}: {cert}")
        else:
            print("ERROR: No visual_assets in PDF generator!")
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=15*mm  # Reduced bottom margin for more space
        )
        
        story = []
        
        # SINGLE PAGE - All content optimized for one page
        story.extend(self._create_single_page_layout(product_data))
        
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        buffer.seek(0)
        return buffer

    def _create_single_page_layout(self, product_data: Dict[str, Any]) -> List:
        """Create optimized single page layout with all content fitting properly"""
        elements = []
        
        # Top header with LYLUX and DOWNLIGHT
        elements.extend(self._create_exact_header())
        
        # Product name with less spacing
        product_name = product_data.get('product_name', 'Regulus Alpha')
        elements.append(Paragraph(product_name, self.styles['ProductTitle']))
        elements.append(Spacer(1, 4*mm))  # Reduced spacing
        
        # Three column section - Product info | Certifications | Dimensions (using enhanced version)
        elements.extend(self._create_main_info_section_with_images(product_data))
        
        # SPECIFICATIONS section with compact layout
        elements.extend(self._create_compact_specifications_section(product_data))
        
        # CUSTOMIZABLE SPECIFICATIONS section (only selected items) - more compact
        elements.extend(self._create_compact_customizable_section(product_data))
        
        # LIGHT DISTRIBUTION section - compact version
        elements.extend(self._create_compact_light_distribution_section())
        
        # Only add accessories if they exist and space permits
        accessories = product_data.get('accessories', [])
        if accessories and len(accessories) <= 3:  # Only show if few accessories
            elements.extend(self._create_compact_accessories_section(accessories))
        
        return elements
    
    def _create_exact_header(self) -> List:
        """Create exact header matching target design with better proportions"""
        elements = []
        
        # Header table with LYLUX logo and DOWNLIGHT badge
        header_data = [
            [
                # LYLUX logo section (black background)
                Paragraph('<b><font size="14" color="white">LYLUX</font></b><br/>'
                         '<font size="7" color="white">LIGHTING YOUR FUTURE</font>', 
                         self.styles['Normal']),
                
                # Empty spacer
                '',
                
                # DOWNLIGHT badge (green background)
                Paragraph('<b><font size="11">DOWNLIGHT</font></b>', 
                         ParagraphStyle(
                             name='DownlightBadge',
                             fontSize=11,
                             textColor=white,
                             backColor=HexColor('#8BC34A'),
                             alignment=TA_CENTER,
                             fontName='Helvetica-Bold',
                             leftIndent=6,
                             rightIndent=6,
                             spaceBefore=4,
                             spaceAfter=4,
                             leading=16,
                             wordWrap='LTR'
                         ))
            ]
        ]
        
        header_table = Table(header_data, colWidths=[70*mm, 85*mm, 45*mm])
        header_table.setStyle(TableStyle([
            # LYLUX section styling
            ('BACKGROUND', (0, 0), (0, 0), HexColor('#2C2C2C')),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
            
            # DOWNLIGHT section styling  
            ('BACKGROUND', (2, 0), (2, 0), HexColor('#8BC34A')),
            ('ALIGN', (2, 0), (2, 0), 'CENTER'),
            ('VALIGN', (2, 0), (2, 0), 'MIDDLE'),
            
            # General styling
            ('PADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(header_table)
        elements.append(Spacer(1, 8*mm))  # Reduced spacing
        
        return elements
    
    def _create_main_info_section_with_images(self, product_data: Dict[str, Any]) -> List:
        """Create clean, professional main section with properly organized images (enhanced version)"""
        elements = []
        
        print(f"=== MAIN INFO SECTION DEBUG ===")
        
        # Get product data
        product = product_data.get('product', {})
        product_image_url = product.get('product_image_url', '')
        print(f"Product image URL: {product_image_url}")
        
        # Get visual assets
        visual_assets = product_data.get('visual_assets', {})
        print(f"Visual assets in main section: {visual_assets}")
        
        certifications = visual_assets.get('certifications', [])
        print(f"Certifications in main section: {len(certifications)} items")
        
        # Create three well-organized columns
        main_data = [
            [
                # Column 1: Product image - clean and centered
                self._create_clean_product_image_cell(product_image_url),
                
                # Column 2: Certifications - organized in a clean grid
                self._create_clean_certifications_cell(certifications),
                
                # Column 3: Dimensions - clean technical drawing
                self._create_clean_dimensions_cell(product_data)
            ]
        ]
        
        main_table = Table(main_data, colWidths=[60*mm, 70*mm, 55*mm])
        main_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#DDDDDD')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#FAFAFA')),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        elements.append(main_table)
        elements.append(Spacer(1, 6*mm))
        
        return elements

    def _create_clean_product_image_cell(self, image_url: str):
        """Create a clean, centered product image cell"""
        if image_url and image_url.startswith(('http://', 'https://')):
            try:
                # Try to download and embed the actual image with better sizing
                img = self._download_image(image_url, max_width=50*mm, max_height=40*mm)
                if img:
                    # Center the image in a clean layout
                    img_data = [
                        [Paragraph('<b>PRODUCT</b>', ParagraphStyle(
                            name='ProductHeader',
                            fontSize=9,
                            textColor=HexColor('#333333'),
                            fontName='Helvetica-Bold',
                            alignment=TA_CENTER,
                            spaceAfter=4
                        ))],
                        [img],
                        [Paragraph('<i>High-efficiency LED downlight</i>', ParagraphStyle(
                            name='ProductCaption',
                            fontSize=7,
                            textColor=HexColor('#666666'),
                            fontName='Helvetica',
                            alignment=TA_CENTER,
                            leading=8
                        ))]
                    ]
                    
                    img_table = Table(img_data, colWidths=[50*mm])
                    img_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('PADDING', (0, 0), (-1, -1), 2),
                    ]))
                    return img_table
                else:
                    return self._create_fallback_product_cell()
            except Exception as e:
                print(f"Error processing product image: {e}")
                return self._create_fallback_product_cell()
        else:
            return self._create_fallback_product_cell()

    def _create_fallback_product_cell(self):
        """Create fallback product cell with clean text"""
        return Paragraph('<b>PRODUCT</b><br/><br/>'
                       'High-efficiency LED downlight<br/>'
                       'Premium aluminium construction<br/>'
                       'Advanced thermal management<br/>'
                       'Multiple beam options available', 
                       ParagraphStyle(
                           name='ProductFallback',
                           fontSize=8,
                           textColor=HexColor('#333333'),
                           fontName='Helvetica',
                           alignment=TA_CENTER,
                           leading=10
                       ))

    def _create_clean_certifications_cell(self, certifications: List[Dict]) -> object:
        """Create clean, organized certifications cell"""
        print(f"=== CLEAN CERTIFICATIONS CELL ===")
        print(f"Received certifications: {len(certifications) if certifications else 0}")
        
        if not certifications:
            return self._create_fallback_certifications_cell()
        
        try:
            # Create header
            cert_elements = []
            cert_elements.append([Paragraph('<b>CERTIFICATIONS</b>', ParagraphStyle(
                name='CertHeader',
                fontSize=9,
                textColor=HexColor('#333333'),
                fontName='Helvetica-Bold',
                alignment=TA_CENTER,
                spaceAfter=4
            ))])
            
            # Create a 2x2 grid for certification images (max 4 certs)
            cert_images = []
            cert_names = []
            
            for i, cert in enumerate(certifications[:4]):  # Limit to 4 for clean layout
                cert_url = cert.get('file_url', '')
                cert_name = cert.get('file_name', f'Cert_{i}')
                
                if cert_url and cert_url.startswith(('http://', 'https://')):
                    cert_img = self._download_image(cert_url, max_width=20*mm, max_height=15*mm)
                    if cert_img:
                        cert_images.append(cert_img)
                        continue
                
                # Fallback to clean text badge
                cert_display_name = cert_name.replace('-', '').replace('.png', '').upper()
                cert_badge = Paragraph(f'<b>{cert_display_name[:4]}</b>', ParagraphStyle(
                    name='CertBadge',
                    fontSize=7,
                    textColor=white,
                    fontName='Helvetica-Bold',
                    alignment=TA_CENTER,
                    backColor=HexColor('#4CAF50'),
                    leftIndent=2,
                    rightIndent=2,
                    spaceBefore=2,
                    spaceAfter=2
                ))
                cert_images.append(cert_badge)
            
            # Arrange certifications in a clean 2x2 grid
            if len(cert_images) >= 2:
                # First row
                row1 = cert_images[:2]
                if len(row1) == 1:
                    row1.append('')  # Fill empty cell
                cert_elements.append(row1)
                
                # Second row if needed
                if len(cert_images) > 2:
                    row2 = cert_images[2:4]
                    if len(row2) == 1:
                        row2.append('')  # Fill empty cell
                    cert_elements.append(row2)
            else:
                # Single certification centered
                cert_elements.append([cert_images[0] if cert_images else '', ''])
            
            # Add footer text
            cert_elements.append(['', ''])  # Spacer row
            cert_elements.append([Paragraph('<b>Rated Life:</b> 50,000 Hrs<br/>'
                                          '<b>Operating Temp:</b> -20°C to 50°C<br/>'
                                          '<b>Material:</b> Aluminium Body', 
                                          ParagraphStyle(
                                              name='CertDetails',
                                              fontSize=7,
                                              textColor=HexColor('#666666'),
                                              fontName='Helvetica',
                                              alignment=TA_LEFT,
                                              leading=8
                                          )), ''])
            
            cert_table = Table(cert_elements, colWidths=[35*mm, 35*mm])
            cert_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 2),
                ('SPAN', (0, 0), (1, 0)),  # Span header across both columns
                ('SPAN', (0, -1), (1, -1)),  # Span footer across both columns
            ]))
            
            return cert_table
            
        except Exception as e:
            print(f"Error creating clean certifications: {e}")
            return self._create_fallback_certifications_cell()

    def _create_fallback_certifications_cell(self):
        """Create fallback certifications cell"""
        return Paragraph('<b>CERTIFICATIONS</b><br/><br/>'
                       '<b>CE</b> ✓ | <b>RoHS</b> ✓<br/><br/>'
                       '<b>Rated Life:</b> 50,000 Hrs<br/>'
                       '<b>Operating Temp:</b> -20°C to 50°C<br/>'
                       '<b>Material:</b> Aluminium Body',
                       ParagraphStyle(
                           name='CertFallback',
                           fontSize=8,
                           textColor=HexColor('#333333'),
                           fontName='Helvetica',
                           alignment=TA_CENTER,
                           leading=10
                       ))

    def _create_clean_dimensions_cell(self, product_data: Dict[str, Any]):
        """Create clean dimensions cell with technical drawing"""
        product = product_data.get('product', {})
        dimension_image_url = product.get('dimension_image_url', '')
        
        if dimension_image_url and dimension_image_url.startswith(('http://', 'https://')):
            try:
                dim_img = self._download_image(dimension_image_url, max_width=45*mm, max_height=35*mm)
                if dim_img:
                    # Clean layout with header, image, and specs
                    dim_data = [
                        [Paragraph('<b>DIMENSIONS (MM)</b>', ParagraphStyle(
                            name='DimHeader',
                            fontSize=9,
                            textColor=HexColor('#333333'),
                            fontName='Helvetica-Bold',
                            alignment=TA_CENTER,
                            spaceAfter=4
                        ))],
                        [dim_img],
                        [Paragraph('Diameter: <b>Ø50</b><br/>Height: <b>52.8</b>', ParagraphStyle(
                            name='DimSpecs',
                            fontSize=8,
                            textColor=HexColor('#666666'),
                            fontName='Helvetica',
                            alignment=TA_CENTER,
                            leading=10
                        ))]
                    ]
                    
                    dim_table = Table(dim_data, colWidths=[45*mm])
                    dim_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('PADDING', (0, 0), (-1, -1), 3),
                    ]))
                    return dim_table
                else:
                    return self._create_fallback_dimensions_cell()
            except Exception as e:
                print(f"Error loading dimension image: {e}")
                return self._create_fallback_dimensions_cell()
        else:
            return self._create_fallback_dimensions_cell()

    def _create_fallback_dimensions_cell(self):
        """Create fallback dimensions cell"""
        return Paragraph('<b>DIMENSIONS (MM)</b><br/><br/>'
                       'Diameter: <b>Ø50</b><br/>'
                       'Height: <b>52.8</b><br/><br/>'
                       '[Technical drawing]<br/>'
                       'Compact profile design',
                       ParagraphStyle(
                           name='DimFallback',
                           fontSize=8,
                           textColor=HexColor('#333333'),
                           fontName='Helvetica',
                           alignment=TA_CENTER,
                           leading=10
                       ))

    def _create_compact_specifications_section(self, product_data: Dict[str, Any]) -> List:
        """Create clean, professional specifications table"""
        elements = []
        
        # Clean section header
        elements.append(Paragraph('SPECIFICATIONS', ParagraphStyle(
            name='CleanSectionHeader',
            fontSize=12,
            textColor=white,
            backColor=HexColor('#424242'),
            fontName='Helvetica-Bold',
            leftIndent=10,
            rightIndent=10,
            spaceBefore=3,
            spaceAfter=3,
            leading=18
        )))
        elements.append(Spacer(1, 3*mm))
        
        # Clean table headers
        headers = [
            'Product Code', 
            'Output\n(lm)', 
            'Power\n(W)', 
            'Efficiency\n(lm/W)', 
            'Tunable Range'
        ]
        
        table_data = [headers]
        
        # Add variants with clean formatting
        selected_variant_id = product_data.get('selected_variant_id')
        base_code = product_data.get('base_part_code', 'LY-DL-RUA')
        
        for variant in product_data.get('variants', []):
            power = variant.get('system_power', 'N/A')
            product_code = f"{base_code}-{power}W-①-②-③"
            
            row = [
                product_code,
                str(variant.get('system_output', 'N/A')),
                str(power),
                str(variant.get('efficiency', 105)),
                '1800K~6000K'
            ]
            table_data.append(row)
        
        # Create clean specs table
        specs_table = Table(table_data, colWidths=[52*mm, 20*mm, 18*mm, 22*mm, 23*mm])
        
        # Clean table styling
        table_style = [
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#424242')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Data rows styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#CCCCCC')),
            ('PADDING', (0, 0), (-1, -1), 4),
            
            # Clean alternating colors
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#FAFAFA')),
            ('BACKGROUND', (0, 2), (-1, 2), white),
            ('BACKGROUND', (0, 4), (-1, 4), white),
        ]
        
        # Highlight selected variant with subtle color
        for i, variant in enumerate(product_data.get('variants', [])):
            if variant.get('id') == selected_variant_id:
                table_style.append(('BACKGROUND', (0, i+1), (-1, i+1), HexColor('#E8F5E8')))
                break
        
        specs_table.setStyle(TableStyle(table_style))
        elements.append(specs_table)
        elements.append(Spacer(1, 5*mm))
        
        return elements

    def _create_compact_customizable_section(self, product_data: Dict[str, Any]) -> List:
        """Create clean customizable specifications"""
        elements = []
        
        # Clean section header
        elements.append(Paragraph('CUSTOMIZABLE SPECIFICATIONS', ParagraphStyle(
            name='CleanSectionHeader',
            fontSize=12,
            textColor=white,
            backColor=HexColor('#424242'),
            fontName='Helvetica-Bold',
            leftIndent=10,
            rightIndent=10,
            spaceBefore=3,
            spaceAfter=3,
            leading=18
        )))
        elements.append(Spacer(1, 3*mm))
        
        # Get selected options
        selected_options = product_data.get('selected_options', {})
        
        if selected_options:
            # Create clean two-column layout
            col1_items = []
            col2_items = []
            
            item_count = 0
            for category_name, option_data in selected_options.items():
                if isinstance(option_data, dict):
                    option_label = option_data.get('option_label', 'Not specified')
                else:
                    option_label = str(option_data)
                
                # Clean display names with numbers
                display_name = category_name
                if category_name == "Beam Angle":
                    display_name = "① Beam Angle"
                elif category_name == "Colour Temperature": 
                    display_name = "② Colour Temperature"
                elif category_name == "IP Rating":
                    display_name = "③ IP Rating"
                
                formatted_item = f"<b>{display_name}:</b> ■ {option_label}"
                
                # Distribute items across columns
                if item_count % 2 == 0:
                    col1_items.append(formatted_item)
                else:
                    col2_items.append(formatted_item)
                item_count += 1
            
            # Create balanced columns
            config_data = [
                [
                    Paragraph('<br/>'.join(col1_items), ParagraphStyle(
                        name='ConfigCol1',
                        fontSize=8,
                        textColor=HexColor('#333333'),
                        fontName='Helvetica',
                        alignment=TA_LEFT,
                        leading=12
                    )),
                    Paragraph('<br/>'.join(col2_items), ParagraphStyle(
                        name='ConfigCol2',
                        fontSize=8,
                        textColor=HexColor('#333333'),
                        fontName='Helvetica',
                        alignment=TA_LEFT,
                        leading=12
                    )) if col2_items else ''
                ]
            ]
            
            config_table = Table(config_data, colWidths=[90*mm, 90*mm])
            config_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('BACKGROUND', (0, 0), (-1, -1), HexColor('#FAFAFA')),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#E0E0E0')),
            ]))
            elements.append(config_table)
        else:
            elements.append(Paragraph('No customizations selected', self.styles['Normal']))
        
        elements.append(Spacer(1, 5*mm))
        return elements

    def _create_compact_light_distribution_section(self) -> List:
        """Create clean light distribution section"""
        elements = []
        
        # Clean section header
        elements.append(Paragraph('LIGHT DISTRIBUTION', ParagraphStyle(
            name='CleanSectionHeader',
            fontSize=12,
            textColor=white,
            backColor=HexColor('#424242'),
            fontName='Helvetica-Bold',
            leftIndent=10,
            rightIndent=10,
            spaceBefore=3,
            spaceAfter=3,
            leading=18
        )))
        elements.append(Spacer(1, 3*mm))
        
        # Clean, organized light distribution data
        light_data = [
            [
                Paragraph('<b>Polar Distribution:</b><br/>'
                         'Photometric data available<br/>'
                         'Beam characteristics optimized<br/>'
                         'IES files available on request', 
                         ParagraphStyle(
                             name='LightDistCol1',
                             fontSize=8,
                             textColor=HexColor('#333333'),
                             fontName='Helvetica',
                             alignment=TA_LEFT,
                             leading=10
                         )),
                
                Paragraph('<b>Performance Data:</b><br/>'
                         '1m: 2,500 lx | Ø0.35m<br/>'
                         '2m: 625 lx | Ø0.70m<br/>'
                         '3m: 278 lx | Ø1.05m', 
                         ParagraphStyle(
                             name='LightDistCol2',
                             fontSize=8,
                             textColor=HexColor('#333333'),
                             fontName='Helvetica',
                             alignment=TA_LEFT,
                             leading=10
                         ))
            ]
        ]
        
        light_table = Table(light_data, colWidths=[90*mm, 90*mm])
        light_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#FAFAFA')),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#E0E0E0')),
        ]))
        
        elements.append(light_table)
        elements.append(Spacer(1, 3*mm))
        
        return elements

    def _create_compact_accessories_section(self, accessories: List[Dict]) -> List:
        """Create compact accessories section with images"""
        elements = []
        
        # Section header
        elements.append(Paragraph('AVAILABLE ACCESSORIES', ParagraphStyle(
            name='CleanSectionHeader',
            fontSize=12,
            textColor=white,
            backColor=HexColor('#424242'),
            fontName='Helvetica-Bold',
            leftIndent=10,
            rightIndent=10,
            spaceBefore=3,
            spaceAfter=3,
            leading=18
        )))
        elements.append(Spacer(1, 3*mm))
        
        if accessories:
            # Create accessories grid with images
            acc_data = []
            
            # Process accessories in rows of 2-3 items
            for i in range(0, len(accessories), 3):  # 3 accessories per row
                row_accessories = accessories[i:i+3]
                acc_row = []
                
                for accessory in row_accessories:
                    acc_cell = self._create_accessory_cell(accessory)
                    acc_row.append(acc_cell)
                
                # Fill empty cells if needed
                while len(acc_row) < 3:
                    acc_row.append('')
                
                acc_data.append(acc_row)
            
            # Create accessories table
            acc_table = Table(acc_data, colWidths=[60*mm, 60*mm, 60*mm])
            acc_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('BACKGROUND', (0, 0), (-1, -1), HexColor('#FAFAFA')),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#E0E0E0')),
            ]))
            
            elements.append(acc_table)
            elements.append(Spacer(1, 4*mm))
        
        return elements

    def _create_accessory_cell(self, accessory: Dict) -> object:
        """Create individual accessory cell with image and details"""
        try:
            acc_elements = []
            
            # Accessory name header
            acc_elements.append([Paragraph(f'<b>{accessory.get("name", "Accessory")}</b>', 
                                         ParagraphStyle(
                                             name='AccHeader',
                                             fontSize=8,
                                             textColor=HexColor('#333333'),
                                             fontName='Helvetica-Bold',
                                             alignment=TA_CENTER,
                                             spaceAfter=2
                                         ))])
            
            # Accessory image
            acc_image_url = accessory.get('image_url', '')
            if acc_image_url and acc_image_url.startswith(('http://', 'https://')):
                acc_img = self._download_image(acc_image_url, max_width=25*mm, max_height=20*mm)
                if acc_img:
                    acc_elements.append([acc_img])
                else:
                    # Fallback to icon/text
                    acc_elements.append([Paragraph('[Image]', ParagraphStyle(
                        name='AccImageFallback',
                        fontSize=7,
                        textColor=HexColor('#999999'),
                        fontName='Helvetica',
                        alignment=TA_CENTER
                    ))])
            else:
                # No image - show icon
                acc_elements.append([Paragraph('📦', ParagraphStyle(
                    name='AccIcon',
                    fontSize=16,
                    textColor=HexColor('#666666'),
                    fontName='Helvetica',
                    alignment=TA_CENTER
                ))])
            
            # Accessory details
            part_code = accessory.get('part_code', 'N/A')
            description = accessory.get('description', '')[:50] + ('...' if len(accessory.get('description', '')) > 50 else '')
            
            acc_elements.append([Paragraph(f'<b>Part:</b> {part_code}<br/>{description}', 
                                         ParagraphStyle(
                                             name='AccDetails',
                                             fontSize=6,
                                             textColor=HexColor('#666666'),
                                             fontName='Helvetica',
                                             alignment=TA_CENTER,
                                             leading=7
                                         ))])
            
            # Create accessory table
            acc_table = Table(acc_elements, colWidths=[55*mm])
            acc_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 2),
            ]))
            
            return acc_table
            
        except Exception as e:
            print(f"Error creating accessory cell: {e}")
            # Fallback to text-only
            return Paragraph(f'<b>{accessory.get("name", "Accessory")}</b><br/>'
                            f'Part: {accessory.get("part_code", "N/A")}', 
                            ParagraphStyle(
                                name='AccFallback',
                                fontSize=7,
                                textColor=HexColor('#333333'),
                                fontName='Helvetica',
                                alignment=TA_CENTER,
                                leading=8
                            ))

    def _download_image(self, url: str, max_width: float = 50*mm, max_height: float = 40*mm):
        """Download image from URL and return ReportLab Image object"""
        try:
            print(f"DEBUG: Attempting to download image from: {url[:100]}...")
            
            # Add headers for better compatibility with signed URLs
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'image/*,*/*;q=0.8'
            }
            
            response = requests.get(url, timeout=15, headers=headers)
            response.raise_for_status()
            
            print(f"DEBUG: Successfully downloaded image, size: {len(response.content)} bytes")
            
            # Create a BytesIO object from the image data
            image_data = BytesIO(response.content)
            
            # Create ReportLab Image object
            img = Image(image_data)
            
            # Scale image to fit within max dimensions while maintaining aspect ratio
            img_width, img_height = img.imageWidth, img.imageHeight
            print(f"DEBUG: Original image size: {img_width}x{img_height}")
            
            aspect_ratio = img_width / img_height
            
            if img_width > max_width:
                img_width = max_width
                img_height = img_width / aspect_ratio
            
            if img_height > max_height:
                img_height = max_height
                img_width = img_height * aspect_ratio
                
            img.drawWidth = img_width
            img.drawHeight = img_height
            
            print(f"DEBUG: Scaled image size: {img_width}x{img_height}")
            return img
            
        except requests.exceptions.RequestException as e:
            print(f"DEBUG: Network error downloading image: {e}")
            return None
        except Exception as e:
            print(f"DEBUG: Error processing image: {e}")
            return None

    def _add_header_footer(self, canvas, doc):
        """Add professional header and footer with better spacing"""
        canvas.saveState()
        
        # Footer with adjusted positioning
        footer_y = 10*mm  # Moved up slightly
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(grey)
        
        # Left side: Copyright text
        canvas.drawString(self.margin, footer_y, 'All rights reserved Lylux 2024 | www.lylux-group.com')
        
        # Right side: LYLUX logo and page number
        logo_width = 35*mm
        logo_height = 8*mm
        logo_x = self.width - self.margin - logo_width
        
        # LYLUX logo background
        canvas.setFillColor(HexColor('#2C2C2C'))
        canvas.rect(logo_x, footer_y - 2*mm, logo_width, logo_height, fill=1)
        
        # LYLUX text
        canvas.setFillColor(white)
        canvas.setFont('Helvetica-Bold', 10)
        canvas.drawString(logo_x + 5*mm, footer_y + 1*mm, 'LYLUX')
        canvas.setFont('Helvetica', 6)
        canvas.drawString(logo_x + 5*mm, footer_y - 1*mm, 'LIGHTING YOUR FUTURE')
        
        # Page number
        canvas.setFillColor(grey)
        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(logo_x - 5*mm, footer_y, str(doc.page))
        
        canvas.restoreState()

    # Legacy/compatibility methods for backwards compatibility
    def _create_page1_exact_layout(self, product_data: Dict[str, Any]) -> List:
        """Fallback method - redirect to single page layout"""
        return self._create_single_page_layout(product_data)
    
    def _create_main_info_section(self, product_data: Dict[str, Any]) -> List:
        """Fallback method - redirect to new method"""
        return self._create_main_info_section_with_images(product_data)
    
    def _create_customizable_section(self, product_data: Dict[str, Any]) -> List:
        """Legacy method - redirect to selected only version"""
        return self._create_compact_customizable_section(product_data)
    
    def _create_specifications_section(self, product_data: Dict[str, Any]) -> List:
        """Legacy method - redirect to compact version"""
        return self._create_compact_specifications_section(product_data)
    
    def _create_light_distribution_section(self) -> List:
        """Legacy method - redirect to compact version"""
        return self._create_compact_light_distribution_section()
    
    def _create_accessories_section(self, accessories: List[Dict]) -> List:
        """Legacy method - redirect to compact version"""
        return self._create_compact_accessories_section(accessories)
    
    def _create_customizable_section_selected_only(self, product_data: Dict[str, Any]) -> List:
        """Legacy method - redirect to compact version"""
        return self._create_compact_customizable_section(product_data)

    # Additional legacy methods for broader compatibility
    def _create_image_cell(self, image_url: str, fallback_text: str):
        """Create image cell with actual image download or fallback text (legacy compatibility)"""
        if image_url and image_url.startswith(('http://', 'https://')):
            try:
                # Try to download and embed the actual image
                img = self._download_image(image_url, max_width=55*mm, max_height=45*mm)
                if img:
                    return img
                else:
                    # If image download fails, show fallback
                    return Paragraph(f'<b>{fallback_text}</b><br/><br/>'
                                   f'[Image could not be loaded]<br/>'
                                   f'<i>High-quality product visualization</i>', 
                                   self.styles['SmallText'])
            except Exception as e:
                print(f"Error processing image: {e}")
                return Paragraph(f'<b>{fallback_text}</b><br/><br/>'
                               f'[Image error: {str(e)[:50]}]', 
                               self.styles['SmallText'])
        else:
            return Paragraph(f'<b>{fallback_text}</b><br/><br/>'
                           f'High-efficiency LED downlight<br/>'
                           f'Premium aluminium construction<br/>'
                           f'Advanced thermal management', 
                           self.styles['SmallText'])
    
    def _create_dimensions_cell(self, product_data: Dict[str, Any]):
        """Create dimensions cell with product-specific technical drawing (legacy compatibility)"""
        # Get product-specific dimension image from products table
        product = product_data.get('product', {})
        dimension_image_url = product.get('dimension_image_url', '')
        
        if dimension_image_url and dimension_image_url.startswith(('http://', 'https://')):
            try:
                # Try to download the product-specific dimension image
                dim_img = self._download_image(dimension_image_url, max_width=55*mm, max_height=45*mm)
                if dim_img:
                    # Create a table with text above and image below
                    dim_data = [
                        [Paragraph('<b>DIMENSIONS (MM)</b><br/>Diameter: Ø50<br/>Height: 52.8', self.styles['SmallText'])],
                        [dim_img]
                    ]
                    dim_table = Table(dim_data, colWidths=[55*mm])
                    dim_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('PADDING', (0, 0), (-1, -1), 2),
                    ]))
                    return dim_table
                else:
                    return Paragraph('<b>DIMENSIONS (MM)</b><br/><br/>Diameter: Ø50<br/>Height: 52.8<br/><br/>[Technical drawing could not load]', self.styles['SmallText'])
            except Exception as e:
                print(f"Error loading dimension image: {e}")
                return Paragraph('<b>DIMENSIONS (MM)</b><br/><br/>Diameter: Ø50<br/>Height: 52.8<br/><br/>[Technical drawing error]', self.styles['SmallText'])
        else:
            return Paragraph('<b>DIMENSIONS (MM)</b><br/><br/>Diameter: Ø50<br/>Height: 52.8<br/><br/>[Technical drawing]', self.styles['SmallText'])

    def _create_certifications_cell_with_images(self, certifications: List[Dict]) -> object:
        """Create certifications cell with actual certification images (legacy compatibility)"""
        print(f"=== CERTIFICATIONS CELL DEBUG ===")
        print(f"Received certifications: {certifications}")
        print(f"Type: {type(certifications)}")
        print(f"Length: {len(certifications) if certifications else 'None'}")
        
        if not certifications:
            print("No certifications provided, using fallback")
            return Paragraph('<b>Certifications:</b><br/>'
                           'CE ✓ | RoHS ✓<br/><br/>'
                           '<b>IP65</b> (Optional)<br/><br/>'
                           '<b>Rated Life:</b> 50,000 Hrs<br/>'
                           '<b>Operating Temp:</b> -20°C~50°C<br/>'
                           '<b>Material:</b> Aluminium Body', self.styles['SmallText'])
        
        try:
            print("Creating certification images...")
            cert_data = []
            cert_data.append([Paragraph('<b>Certifications:</b>', self.styles['SmallText'])])
            
            # Process each certification
            for i, cert in enumerate(certifications):
                print(f"Processing cert {i}: {cert}")
                cert_url = cert.get('file_url', '')
                cert_name = cert.get('file_name', f'Cert_{i}')
                
                if cert_url and cert_url.startswith(('http://', 'https://')):
                    print(f"Downloading image from: {cert_url[:50]}...")
                    cert_img = self._download_image(cert_url, max_width=25*mm, max_height=20*mm)
                    if cert_img:
                        print(f"Successfully downloaded cert {i}")
                        cert_data.append([cert_img])
                        continue
                
                # Fallback to text
                print(f"Using text fallback for cert {i}")
                display_name = cert_name.replace('-', ' ').replace('.png', '').title()
                cert_data.append([Paragraph(f'{display_name} ✓', self.styles['SmallText'])])
            
            # Add additional info
            cert_data.append([Paragraph('<b>Rated Life:</b> 50,000 Hrs<br/>'
                                      '<b>Operating Temp:</b> -20°C~50°C<br/>'
                                      '<b>Material:</b> Aluminium Body', self.styles['SmallText'])])
            
            # Create table
            cert_table = Table(cert_data, colWidths=[60*mm])
            cert_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('PADDING', (0, 0), (-1, -1), 2),
            ]))
            
            print("Successfully created certification table")
            return cert_table
            
        except Exception as e:
            print(f"Error creating certifications: {e}")
            import traceback
            traceback.print_exc()
            return Paragraph('<b>Certifications:</b><br/>'
                           'CE ✓ | RoHS ✓<br/><br/>'
                           '<b>Rated Life:</b> 50,000 Hrs<br/>'
                           '<b>Operating Temp:</b> -20°C~50°C', self.styles['SmallText'])

    def _create_option_section(self, number: str, title: str, options: List[str], selected_option: Dict) -> Paragraph:
        """Create individual option section showing only selected items"""
        content = f'<b>{number} {title}</b><br/>' if number else f'<b>{title}</b><br/>'
        
        selected_label = selected_option.get('option_label', '') if isinstance(selected_option, dict) else str(selected_option)
        
        # Only show the selected option with a checkmark, not all options
        if selected_label and selected_label != '':
            # Find the matching option and show only that one
            for option in options:
                if option == selected_label or option in selected_label or selected_label in option:
                    content += f'☑ {option}<br/>'
                    break
            else:
                # If no exact match found, show the selected_label as is
                content += f'☑ {selected_label}<br/>'
        else:
            # If nothing selected, show first option unchecked
            content += f'☐ {options[0]}<br/>' if options else ''
        
        return Paragraph(content, self.styles['CheckboxText'])