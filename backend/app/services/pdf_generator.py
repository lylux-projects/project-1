# backend/app/services/pdf_generator.py
import subprocess
import tempfile
import os
import shutil
from io import BytesIO
from typing import Dict, Any
from datetime import datetime

class DatasheetGenerator:
    def __init__(self):  # FIXED: Changed from _init_ to __init__
        self.java_path = "java"
        self.jar_path = os.path.join(os.path.dirname(__file__), "..", "..", "lib")
        # ALL THREE JAR FILES - Windows classpath format
        self.classpath = f"{self.jar_path}\\flying-saucer-core-9.1.22.jar;{self.jar_path}\\flying-saucer-pdf-itext5-9.1.22.jar;{self.jar_path}\\itextpdf-5.5.13.1.jar"
        
    def generate_datasheet(self, product_data: Dict[str, Any]) -> BytesIO:
        """Generate PHOS-quality PDF using Flying Saucer"""
        try:
            print(f"=== Flying Saucer PDF Generator START ===")
            print(f"Product: {product_data.get('product_name', 'Unknown')}")
            
            # Check ALL JAR files exist
            required_jars = [
                "flying-saucer-core-9.1.22.jar",
                "flying-saucer-pdf-itext5-9.1.22.jar", 
                "itextpdf-5.5.13.1.jar"
            ]
            
            for jar in required_jars:
                jar_path = os.path.join(self.jar_path, jar)
                if not os.path.exists(jar_path):
                    raise Exception(f"Missing JAR file: {jar}. Please download it to {self.jar_path}")
                print(f"✓ {jar} found")
            
            # Create perfect PHOS-style HTML
            html_content = self._create_phos_style_html(product_data)
            
            # Create temporary files
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as html_file:
                html_file.write(html_content)
                html_file_path = html_file.name
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as pdf_file:
                pdf_file_path = pdf_file.name
            
            try:
                # Generate PDF using Flying Saucer Java process
                self._generate_pdf_with_java(html_file_path, pdf_file_path)
                
                # Read generated PDF
                with open(pdf_file_path, 'rb') as f:
                    pdf_data = f.read()
                
                if len(pdf_data) == 0:
                    raise Exception("Generated PDF file is empty")
                
                pdf_buffer = BytesIO(pdf_data)
                print(f"✅ PHOS-style PDF generated successfully ({len(pdf_data)} bytes)")
                return pdf_buffer
                
            finally:
                # Cleanup temporary files
                if os.path.exists(html_file_path):
                    os.unlink(html_file_path)
                if os.path.exists(pdf_file_path):
                    os.unlink(pdf_file_path)
                    
        except Exception as e:
            print(f"❌ ERROR in Flying Saucer PDF generator: {str(e)}")
            raise e
    
    def _generate_pdf_with_java(self, html_file: str, pdf_file: str):
        """Generate PDF using Java Flying Saucer with explicit font loading"""
        
        # Create a properly named temporary directory
        temp_dir = tempfile.mkdtemp()
        java_file_path = os.path.join(temp_dir, "PDFGen.java")
        
        # Get absolute path to fonts directory
        fonts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "fonts"))
        
        # Debug: Check if fonts directory exists and list files
        print(f"=== FONT LOADING DEBUG ===")
        print(f"Fonts directory: {fonts_dir}")
        print(f"Directory exists: {os.path.exists(fonts_dir)}")
        
        if os.path.exists(fonts_dir):
            font_files = os.listdir(fonts_dir)
            print(f"Font files found: {font_files}")
            
            # Find YuGothic font files
            yugothic_fonts = [f for f in font_files if 'YuGoth' in f]
            print(f"YuGothic fonts: {yugothic_fonts}")
        else:
            print("Fonts directory not found!")
        
        # Convert Windows path separators to forward slashes for Java
        fonts_dir_java = fonts_dir.replace("\\", "/")
        
        # Java class with correct Flying Saucer font registration
        java_class = f'''import org.xhtmlrenderer.pdf.ITextRenderer;
    import java.io.*;
    import java.nio.file.Files;
    import java.nio.file.Paths;

    class PDFGen {{
        public static void main(String[] args) {{
            try {{
                String htmlFile = args[0];
                String pdfFile = args[1];
                
                String htmlContent = new String(Files.readAllBytes(Paths.get(htmlFile)), "UTF-8");
                
                ITextRenderer renderer = new ITextRenderer();
                
                // CRITICAL: Register fonts with the correct method signature
                String fontsDir = "{fonts_dir_java}";
                System.out.println("Fonts directory: " + fontsDir);
                
                try {{
                    // Register each font file separately 
                    String regularFont = fontsDir + "/YuGothR.ttc";
                    if (new File(regularFont).exists()) {{
                        renderer.getFontResolver().addFont(regularFont, true);
                        System.out.println("✓ YuGothic Regular registered");
                    }}
                    
                    String boldFont = fontsDir + "/YuGothB.ttc";
                    if (new File(boldFont).exists()) {{
                        renderer.getFontResolver().addFont(boldFont, true);
                        System.out.println("✓ YuGothic Bold registered");
                    }}
                    
                    String mediumFont = fontsDir + "/YuGothM.ttc";
                    if (new File(mediumFont).exists()) {{
                        renderer.getFontResolver().addFont(mediumFont, true);
                        System.out.println("✓ YuGothic Medium registered");
                    }}
                    
                    String lightFont = fontsDir + "/YuGothL.ttc";
                    if (new File(lightFont).exists()) {{
                        renderer.getFontResolver().addFont(lightFont, true);
                        System.out.println("✓ YuGothic Light registered");
                    }}
                    
                    System.out.println("Font registration completed - ready to generate PDF");
                    
                }} catch (Exception fontError) {{
                    System.err.println("Font registration failed: " + fontError.getMessage());
                    fontError.printStackTrace();
                }}
                
                System.out.println("Font registration completed. Proceeding with PDF generation...");
                
                // Enable high quality rendering
                renderer.getSharedContext().setPrint(true);
                renderer.getSharedContext().setInteractive(false);
                renderer.getSharedContext().getTextRenderer().setSmoothingThreshold(0);
                
                renderer.setDocumentFromString(htmlContent);
                renderer.layout();
                
                FileOutputStream fos = new FileOutputStream(pdfFile);
                renderer.createPDF(fos);
                fos.close();
                
                System.out.println("PDF_SUCCESS");
                
            }} catch (Exception e) {{
                System.err.println("PDF_ERROR: " + e.getMessage());
                e.printStackTrace();
                System.exit(1);
            }}
        }}
    }}'''
        
        try:
            # Write Java file
            with open(java_file_path, 'w', encoding='utf-8') as f:
                f.write(java_class)
            
            print(f"Created Java file: {java_file_path}")
            
            # Compile Java class
            compile_cmd = [
                "javac",
                "-cp", self.classpath,
                java_file_path
            ]
            
            print(f"Compiling: {' '.join(compile_cmd)}")
            
            compile_result = subprocess.run(compile_cmd, capture_output=True, text=True)
            if compile_result.returncode != 0:
                raise Exception(f"Java compilation failed: {compile_result.stderr}")
            
            print("✓ Java compilation successful")
            
            # Run Java class
            run_cmd = [
                self.java_path,
                "-cp", f"{self.classpath};{temp_dir}",
                "PDFGen",
                html_file,
                pdf_file
            ]
            
            print(f"Running: {' '.join(run_cmd)}")
            
            run_result = subprocess.run(run_cmd, capture_output=True, text=True, timeout=30)
            
            print(f"Java stdout: {run_result.stdout}")
            if run_result.stderr:
                print(f"Java stderr: {run_result.stderr}")
            
            if run_result.returncode != 0:
                raise Exception(f"PDF generation failed with exit code {run_result.returncode}: {run_result.stderr}")
                
            if "PDF_SUCCESS" not in run_result.stdout:
                raise Exception(f"PDF generation did not complete successfully. Output: {run_result.stdout}")
                
            print("✓ PDF generation completed successfully")
                
        finally:
            # Cleanup temp directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    def _create_phos_style_html(self, product_data: Dict[str, Any]) -> str:
        """Create perfect PHOS-style HTML that Flying Saucer can render"""
        
        # Extract data
        product_name = product_data.get('product_name', 'REGULUS ALPHA')
        final_part_code = product_data.get('final_part_code', product_data.get('base_part_code', 'LY-DL-RUA-9W-30-2700K-IP20'))
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        # Get product info
        product = product_data.get('product', {})
        description = product.get('description')
        
        # Get product category from database
        product_category = product_data.get('product_category', 'DOWNLIGHT')
        print(f"=== PRODUCT CATEGORY DEBUG ===")
        print(f"Product category: {product_category}")
        
        # Get selected variant
        selected_variant = self._get_selected_variant(product_data)
        
        # Get selected options
        selected_options = product_data.get('selected_options', {})
        
        # Logo URLs
        logo_url = "https://ijhthgduecrvuwnukzcg.supabase.co/storage/v1/object/sign/product-images/visual-assets/Video-outtro.jpg?token=eyJraWQiOiJzdG9yYWdlLXVybC1zaWduaW5nLWtleV9jMjY5MWQxYi0wMGFlLTQzMzEtYmZhOC00MWEyMDRiYmMzZmUiLCJhbGciOiJIUzI1NiJ9.eyJ1cmwiOiJwcm9kdWN0LWltYWdlcy92aXN1YWwtYXNzZXRzL1ZpZGVvLW91dHRyby5qcGciLCJpYXQiOjE3NDk2NTQ0MDAsImV4cCI6MzMyNTQxMTg0MDB9.MRXBbzHe26_6zSrekouErabse7BR4icxXXhB81D_ItU"
        full_logo_url = "https://ijhthgduecrvuwnukzcg.supabase.co/storage/v1/object/sign/product-images/visual-assets/footerlogo.jpg?token=eyJraWQiOiJzdG9yYWdlLXVybC1zaWduaW5nLWtleV9jMjY5MWQxYi0wMGFlLTQzMzEtYmZhOC00MWEyMDRiYmMzZmUiLCJhbGciOiJIUzI1NiJ9.eyJ1cmwiOiJwcm9kdWN0LWltYWdlcy92aXN1YWwtYXNzZXRzL2Zvb3RlcmxvZ28uanBnIiwiaWF0IjoxNzQ5NjYyNzgxLCJleHAiOjMzMjU0MTI2NzgxfQ.NgJQR2DQltNrMXkbodKKaWY3uT1srZ04-mURMH3UYJg"
        
        # Get accessories - properly handle the selected accessories from frontend
        accessories = product_data.get('accessories', [])
        print(f"=== ACCESSORIES DEBUG ===")
        print(f"Accessories data: {accessories}")
        print(f"Type: {type(accessories)}")
        print(f"Number of accessories: {len(accessories) if accessories else 0}")
        
        # Build accessories HTML - FIXED to include part codes
        accessories_html = ""
        if accessories and len(accessories) > 0:
            for i, accessory in enumerate(accessories):
                print(f"  Accessory {i}: {accessory}")
                
                # Get accessory name
                accessory_name = (accessory.get('name') or 
                                accessory.get('accessory_name') or 
                                accessory.get('product_name') or 
                                'Unknown Accessory')
                
                # Get part code - this is what was missing!
                part_code = (accessory.get('part_code') or 
                        accessory.get('accessory_part_code') or '')
                
                print(f"    Name: {accessory_name}")
                print(f"    Part Code: {part_code}")
                
                # Create rich accessory display with image if available
                accessory_image_url = (accessory.get('image_url') or 
                                    accessory.get('accessory_image_url') or '')
                
                if accessory_image_url:
                    # With image layout - include part code
                    accessories_html += f'''
                    <table class="accessory-row">
                        <tr>
                            <td class="accessory-image-cell">
                                <img src="{accessory_image_url}" alt="{accessory_name}" class="accessory-image"/>
                            </td>
                            <td class="accessory-text-cell">
                                <div class="accessory-name-block">{accessory_name}</div>
                                {f'<div class="accessory-part-block">{part_code}</div>' if part_code else ''}
                            </td>
                        </tr>
                    </table>'''
                else:
                    # Without image layout - include part code
                    if part_code:
                        accessories_html += f'''
                        <div class="accessory-item">
                            <div class="accessory-name">{accessory_name}</div>
                            <div class="accessory-part-code">{part_code}</div>
                        </div>'''
                    else:
                        accessories_html += f'<div class="accessory-item">{accessory_name}</div>'
        else:
            accessories_html = '<div class="accessory-item" style="color: #999; font-style: italic;">None selected</div>'
        
        print(f"Final accessories HTML: {accessories_html}")
        
        # Get images
        product_image_url = product.get('product_image_url', '')
        dimension_image_url = product.get('dimension_image_url', '')
        
        # Get certifications
        certifications = product_data.get('visual_assets', {}).get('certifications', [])
        print(f"=== CERTIFICATIONS DEBUG IN PDF GENERATOR ===")
        # TEMPORARY FIX: Force certifications for testing
        print("=== FORCING CERTIFICATIONS FOR TESTING ===")
        product_data['visual_assets'] = {
            'certifications': [
                {
                    'file_name': 'RoHS Certification',
                    'file_url': 'https://ijhthgduecrvuwnukzcg.supabase.co/storage/v1/object/sign/product-images/visual-assets/rohs-certification.png',
                    'asset_type': 'certification'
                },
                {
                    'file_name': 'CE Certification', 
                    'file_url': 'https://ijhthgduecrvuwnukzcg.supabase.co/storage/v1/object/sign/product-images/visual-assets/ce-certification.png',
                    'asset_type': 'certification'
                }
            ]
        }
        print(f"Forced {len(product_data['visual_assets']['certifications'])} certifications")
        certifications_html = ""
        if certifications:
            for cert in certifications:
                cert_url = cert.get('file_url', '')
                cert_name = cert.get('file_name', 'Certification')
                if cert_url:
                    certifications_html += f'<img src="{cert_url}" alt="{cert_name}" class="cert-logo"/>'
    
    # TABLE-BASED LAYOUT FOR FLYING SAUCER - WITH FIXED CATEGORY RECTANGLE
        html_content = f'''<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8"/>
        <style>
            @page {{
                @top-center {{
                    content: element(header);
                }}
                @bottom-center {{
                    content: element(footer);
                }}
                size: A4;
                margin: 10mm 15mm 15mm 15mm;
            }}
            
            body {{
                font-family: 'Yu Gothic', 'YuGothic', 'Yu Gothic UI', Times, serif;
                font-size: 10pt;
                font-weight: normal;
                line-height: 1.2;
                color: #333;
                margin: 0;
                padding: 0;
            }}
            
            .header {{
                width: 100%;
                padding-bottom: 5pt;
                margin-bottom: 10pt;
            }}
            
            .header-content {{
                display: table;
                width: 100%;
            }}
            
            .company-info {{
                display: table-cell;
                vertical-align: top;
                position: relative;
            }}
            
            .logo-section {{
                display: inline-block;
                vertical-align: top;
                margin-right: 0pt;
                height: 37pt;
                width: 120pt;
            }}
            
            .company-logo {{
                height: 35pt;
                width: auto;
                margin-bottom: 2pt;
            }}
            
            .company-logo-text {{
                font-family: 'YuGothic', Arial, sans-serif;
                font-size: 28pt;
                font-weight: bold;
                letter-spacing: 4pt;
                color: #333;
                line-height: 30pt;
                margin: 0;
                height: 30pt;
            }}
            
            .company-tagline {{
                font-family: 'YuGothic', Arial, sans-serif;
                font-size: 7pt;
                font-weight: bold;
                letter-spacing: 2pt;
                color: #666;
                text-transform: uppercase;
                margin: 0;
                height: 7pt;
                line-height: 7pt;
            }}
            
            .product-category {{
                font-family: 'Yu Gothic', 'YuGothic', 'Yu Gothic UI', Times, serif;
                background-color: #4a4a4a;
                color: white;
                padding: 0 8pt;
                font-size: 15pt;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 0.5pt;
                border-radius: 2pt;
                display: inline-block;
                vertical-align: top;
                height: 35pt;
                line-height: 35pt;
                min-width: 400pt;
                text-align: right;
                position: absolute;
                left: 45pt;
                top: 0pt;
            }}

            .green-rectangle {{
                background-color: #90bd2c;
                color: white;
                padding: 0 8pt;
                font-size: 8pt;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 0.5pt;
                border-radius: 2pt;
                display: inline-block;
                vertical-align: top;
                height: 35pt;
                line-height: 35pt;
                min-width: 20pt;
                text-align: center;
                position: absolute;
                left: 470pt;
                top: 0pt;
            }}
            
            .divider {{
                border-bottom: 2px solid #333;
                margin-top: 8pt;
                width: 100%;
                clear: both;
            }}
            
            .product-title {{
                font-family: 'Yu Gothic', 'YuGothic', 'Yu Gothic UI', Times, serif;
                font-size: 20pt;
                font-weight: bold;
                margin: 0 0 8pt 0;
                color: #333;
                line-height: 1.1;
                border-left: 4pt solid #90bd2c;
                padding-left: 8pt;
            }}
            
            .images-table {{
                width: 100%;
                margin-bottom: 15pt;
                border-collapse: collapse;
            }}
            
            .images-table td {{
                width: 50%;
                text-align: center;
                padding: 5pt;
            }}
            
            .product-image, .dimension-image {{
                max-width: 95%;
                height: auto;
            }}
            
            .main-table {{
                width: 100%;
                border-collapse: collapse;
            }}
            
            .main-table td {{
                vertical-align: top;
                padding: 0;
            }}
            
            .left-column {{
                width: 65%;
                padding-right: 10pt;
            }}
            
            .right-column {{
                width: 35%;
                padding-left: 10pt;
            }}
            
            .section {{
                margin-bottom: 12pt;
            }}
            
            .section-header {{
                font-family: 'Yu Gothic', 'YuGothic', 'Yu Gothic UI', Times, serif;
                font-size: 12pt;
                font-weight: bold;
                margin: 0 0 6pt 0;
                padding: 2pt 0 2pt 6pt;
                color: #333;
                line-height: 1.2;
                border-left: 3pt solid #90bd2c;
                display: block;
            }}
            
            .part-code {{
                font-family: 'YuGothic', 'Courier New', monospace;
                font-size: 11pt;
                font-weight: bold;
                margin: 3pt 0 6pt 0;
                color: #333;
                line-height: 1.0;
            }}
            
            .spec-table {{
                width: 100%;
                border-collapse: collapse;
                margin: 0;
            }}
            
            .spec-table td {{
                font-family: 'Yu Gothic', 'YuGothic', 'Yu Gothic UI', Times, serif;
                padding: 1.25pt 0;
                border: none;
                font-weight: bold;
                font-size: 8.5pt;
                line-height: 1.2;
                vertical-align: top;
            }}
            
            .label-col {{
                color: #333;
                font-weight: bold;
                width: 60%;
            }}
            
            .value-col {{
                color: #666;
                font-weight: normal;
                text-align: left;
                width: 40%;
            }}
            
            /* FIXED ACCESSORIES STYLES - Added part code support */
            .accessory-item {{
                font-family: 'Yu Gothic', 'YuGothic', 'Yu Gothic UI', Times, serif;
                font-size: 8pt;
                margin: 3pt 0;
                color: #666;
                border-bottom: 1px dotted #ddd;
                padding-bottom: 2pt;
            }}
            
            .accessory-item .accessory-name {{
                font-weight: bold;
                margin-bottom: 1pt;
                color: #333;
            }}
            
            .accessory-item .accessory-part-code {{
                font-size: 7pt;
                color: #888;
                font-family: 'Courier New', monospace;
                font-style: italic;
                margin-left: 4pt;
            }}
            
            .accessory-item-with-image {{
                font-family: 'YuGothic', Arial, sans-serif;
                margin: 4pt 0;
                display: flex;
                align-items: center;
                font-size: 8pt;
                color: #666;
                border-bottom: 1px dotted #ddd;
                padding-bottom: 4pt;
            }}

            .accessory-row {{
                width: 100%;
                margin-bottom: 8pt;
                border-spacing: 0;
            }}

            .accessory-text-cell {{
                vertical-align: middle;
            }}

            .accessory-image-cell {{
                width: 40pt;
                vertical-align: middle;
                padding-right: 6pt;
            }}
            
            .accessory-image {{
                width: 30pt;
                height: 30pt;
                margin-right: 6pt;
                border: 1px solid #ddd;
                border-radius: 2pt;
            }}

            .accessory-name-block {{
                background-color: #333;
                color: white;
                font-size: 8pt;
                font-weight: bold;
                padding: 3pt 6pt;
                margin-bottom: 1pt;
            }}

            .accessory-part-block {{
                background-color: #f3f3f3;
                font-size: 7pt;
                color: #333;
                padding: 3pt 6pt;
                font-family: 'Courier New', monospace;
            }}
            
            .accessory-details {{
                flex: 1;
                display: flex;
                flex-direction: column;
            }}
            
            .accessory-details .accessory-name {{
                font-weight: bold;
                margin-bottom: 1pt;
                color: #333;
            }}
            
            .accessory-details .accessory-part-code {{
                font-size: 7pt;
                color: #888;
                font-family: 'Courier New', monospace;
                font-style: italic;
            }}
            
            .cert-logo {{
                width: 45pt;
                height: 45pt;
                margin: 3pt;
                display: inline-block;
            }}
            
            /* Footer CSS */
            .footer {{
                position: running(footer);
                font-family: 'Yu Gothic', 'YuGothic', 'Yu Gothic UI', Times, serif;
                font-size: 9pt;
                font-weight: normal;
                color: #333;
                border-top: 2px solid #333;
                padding: 0pt 2pt;
                background: white;
                width: 100%;
            }}

            .footer-table {{
                width: 100%;
                border-collapse: collapse;
            }}

            .footer-table td {{
                vertical-align: middle;
                padding: 2pt 5pt;
            }}

            .footer-left {{
                font-family: 'YuGothic', Arial, sans-serif;
                text-align: left;
                font-weight: bold;
                width: 33%;
            }}

            .footer-center {{
                text-align: center;
                width: 34%;
            }}

            .footer-logo {{
                height: 25pt;
            }}

            .footer-right {{
                font-family: 'YuGothic', Arial, sans-serif;
                text-align: right;
                font-weight: bold;
                width: 33%;
            }}
        </style>
    </head>
    <body>
        <div class="page-content">
            <!-- Header with FIXED category rectangle next to logo -->
            <div class="header">
                <div class="header-content">
                    <div class="company-info">
                        <div class="logo-section">
                            <!-- Try the logo image first -->
                            <img src="{logo_url}" alt="LYLUX" class="company-logo" 
                                onerror="this.style.display='none'; this.nextElementSibling.style.display='block';" />
                            <!-- Fallback text logo (hidden by default) -->
                            <div class="company-logo-text" style="display: none;">LYLUX</div>
                        </div>
                        <!-- FIXED Product Category rectangle - dark gray with white text -->
                        <div class="product-category">{product_category.upper()}</div>
                        <div class="green-rectangle"></div>
                    </div>
                </div>
                <div class="divider"></div>
            </div>

            <!-- Product Title -->
            <div class="product-title">{product_name.upper()}</div>
            
            <!-- Images Section -->
            <table class="images-table">
                <tr>
                    <td>{f'<img src="{product_image_url}" alt="{product_name}" class="product-image"/>' if product_image_url else 'Product Image'}</td>
                    <td>{f'<img src="{dimension_image_url}" alt="Technical Drawing" class="dimension-image"/>' if dimension_image_url else 'Technical Drawing'}</td>
                </tr>
            </table>

            <!-- Main Content Table -->
            <table class="main-table">
                <tr>
                    <td class="left-column">
                        <!-- GENERAL -->
                        <div class="section">
                            <div class="section-header">GENERAL</div>
                            <table class="spec-table">
                                <tr><td class="label-col">Material</td><td class="value-col">Die Cast Aluminium</td></tr>
                                <tr><td class="label-col">Finish</td><td class="value-col">Powder Coated</td></tr>
                                <tr><td class="label-col">RAL Code</td><td class="value-col">RAL9016</td></tr>
                                <tr><td class="label-col">Reflector Colour</td><td class="value-col">Black</td></tr>
                                <tr><td class="label-col">IP</td><td class="value-col">IP20</td></tr>
                            </table>
                        </div>

                        <!-- LED -->
                        <div class="section">
                            <div class="section-header">LED</div>
                            <table class="spec-table">
                                <tr><td class="label-col">CCT</td><td class="value-col">{selected_options.get('Colour Temperature', {}).get('option_label', '2700K')}</td></tr>
                                <tr><td class="label-col">CRI</td><td class="value-col">{selected_options.get('CRI', {}).get('option_label', '90')}</td></tr>
                                <tr><td class="label-col">LED Output</td><td class="value-col">{selected_variant.get('system_output', 440)}lm</td></tr>
                                <tr><td class="label-col">System Output</td><td class="value-col">{selected_variant.get('system_output', 440)}lm-15%</td></tr>
                                <tr><td class="label-col">Lifetime</td><td class="value-col">50000h@l80B10</td></tr>
                                <tr><td class="label-col">SDCM</td><td class="value-col">3</td></tr>
                            </table>
                        </div>

                        <!-- OPTICS -->
                        <div class="section">
                            <div class="section-header">OPTICS</div>
                            <table class="spec-table">
                                <tr><td class="label-col">Beam Angle</td><td class="value-col">{selected_options.get('Beam Angle', {}).get('option_label', '18°')}</td></tr>
                            </table>
                        </div>

                        <!-- ELECTRIC -->
                        <div class="section">
                            <div class="section-header">ELECTRIC</div>
                            <table class="spec-table">
                                <tr><td class="label-col">LED Driver</td><td class="value-col">{selected_options.get('Control Type', {}).get('option_label', 'Non Dimmable')}</td></tr>
                                <tr><td class="label-col">LED power</td><td class="value-col">{selected_variant.get('system_power', 4)}W</td></tr>
                                <tr><td class="label-col">System Power</td><td class="value-col">{selected_variant.get('system_power', 6)}W</td></tr>
                                <tr><td class="label-col">LED Current</td><td class="value-col">350mA</td></tr>
                            </table>
                        </div>

                        <!-- DIMENSION -->
                        <div class="section">
                            <div class="section-header">DIMENSION</div>
                            <table class="spec-table">
                                <tr><td class="label-col">D1</td><td class="value-col">50mm</td></tr>
                                <tr><td class="label-col">H</td><td class="value-col">50mm</td></tr>
                                <tr><td class="label-col">D2</td><td class="value-col">55mm</td></tr>
                                <tr><td class="label-col">Cutout</td><td class="value-col">50mm</td></tr>
                            </table>
                        </div>
                    </td>
                    
                    <td class="right-column">
                        <!-- ACCESSORIES (TOP) - NOW WITH PART CODES -->
                        <div class="section">
                            <div class="section-header">ACCESSORIES</div>
                            <div class="accessories-container">
                                {accessories_html}
                            </div>
                        </div>
                    
                        <!-- PRODUCT PART CODE (MIDDLE) -->
                        <div class="section">
                            <div class="section-header">PRODUCT PART CODE</div>
                            <div class="part-code">{final_part_code}</div>
                        </div>

                        <!-- CERTIFICATIONS (BOTTOM) -->
                        <div class="section">
                            <div class="section-header">CERTIFICATIONS</div>
                            <div class="certifications-container">
                                {certifications_html if certifications_html else '<div style="font-size: 8pt; color: #666;">Certifications loading...</div>'}
                            </div>
                        </div>
                    </td>
                </tr>
            </table>
        </div>

        <!-- Footer HTML -->
        <div class="footer">
            <table class="footer-table">
                <tr>
                    <td class="footer-left">
                        All rights reserved Lylux 2024<br/>
                        www.lylux-group.com
                    </td>
                    <td class="footer-center">
                        <img src="{full_logo_url}" alt="LYLUX" class="footer-logo" onerror="this.style.display='none';" />
                    </td>
                    <td class="footer-right">
                        1
                    </td>
                </tr>
            </table>
        </div>
    </body>
    </html>'''
        
        return html_content
    
    def _get_selected_variant(self, product_data: Dict[str, Any]):
        """Get the selected variant or first variant"""
        selected_variant_id = product_data.get('selected_variant_id')
        variants = product_data.get('variants', [])
        
        if selected_variant_id:
            for variant in variants:
                if variant.get('id') == selected_variant_id:
                    return variant
        
        # Return first variant or default values
        if variants:
            return variants[0]
        else:
            return {
                'system_output': 420,
                'system_power': 4,
                'efficiency': 105
            }