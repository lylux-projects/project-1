# backend/test_pdf_simple.py
import pdfkit
import os
import platform

def test_wkhtmltopdf():
    """Test if wkhtmltopdf is working"""
    
    # PHOS-style HTML inline
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page { size: A4; margin: 25mm; }
            body { font-family: Helvetica; font-size: 10px; color: #333; }
            .header { display: flex; justify-content: space-between; margin-bottom: 15mm; }
            .logo { font-size: 28px; letter-spacing: 6px; }
            .tagline { font-size: 7px; letter-spacing: 2px; color: #666; margin-top: 2mm; }
            .date { font-size: 10px; color: #666; }
            .divider { border-bottom: 1px solid #333; margin-bottom: 8mm; }
            .title { font-size: 18px; font-weight: bold; margin: 6mm 0 4mm 0; }
            .orange { color: #D4B88C; margin-right: 4px; }
            .description { font-size: 11px; margin-bottom: 12mm; color: #666; }
            .section { font-size: 11px; font-weight: bold; margin: 8mm 0 4mm 0; }
            .spec { display: flex; justify-content: space-between; padding: 1mm 0; }
            .footer { position: fixed; bottom: 15mm; left: 25mm; right: 25mm; display: flex; justify-content: space-between; font-size: 9px; color: #666; }
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                <div class="logo">LYLUX</div>
                <div class="tagline">E N G I N E E R I N G   L I G H T</div>
            </div>
            <div class="date">Date<br><strong>10/06/2025</strong></div>
        </div>
        
        <div class="divider"></div>
        
        <h1 class="title">
            <span class="orange">|</span> REGULUS ALPHA
        </h1>
        
        <p class="description">
            The Regulus Alpha is a recessed, high-efficiency downlight with advanced thermal management and features a beautifully sculpted anti-glare design.
        </p>
        
        <h2 class="section">
            <span class="orange">|</span> PRODUCT PART CODE
        </h2>
        <div style="font-size: 12px; font-weight: bold; margin: 3mm 0 6mm 0;">LY-DL-RUA-9W-30-2700K-IP20</div>
        
        <h2 class="section">
            <span class="orange">|</span> PRODUCT FINISHES
        </h2>
        <div class="spec"><span>Beam Angle</span><span>30° Medium</span></div>
        <div class="spec"><span>Colour Temperature</span><span>2700K Warm White</span></div>
        <div class="spec"><span>IP Rating</span><span>IP20 (Indoor)</span></div>
        
        <h2 class="section">
            <span class="orange">|</span> TECHNICAL SPECIFICATION
        </h2>
        <div class="spec"><span>Luminaire Lumens</span><span>945lm</span></div>
        <div class="spec"><span>Circuit Watts</span><span>9W</span></div>
        <div class="spec"><span>Luminaire Efficacy</span><span>105lm/W</span></div>
        <div class="spec"><span>Beam Angle</span><span>30°</span></div>
        <div class="spec"><span>CCT</span><span>2700k</span></div>
        <div class="spec"><span>Binning</span><span>2 step</span></div>
        <div class="spec"><span>CRI</span><span>80</span></div>
        <div class="spec"><span>Lumen Maintenance</span><span>LM80</span></div>
        <div class="spec"><span>Lifetime</span><span>50000hrs</span></div>
        <div class="spec"><span>Current</span><span>350mA</span></div>
        <div class="spec"><span>Operating Temperature</span><span>-20°C to 50°C</span></div>
        
        <div class="footer">
            <div>LYLUX.COM</div>
            <div style="text-align: center; font-weight: bold;">LYLUX<br><span style="font-size: 6px;">ENGINEERING LIGHT</span></div>
            <div>+44 XXX XXX XXXX</div>
        </div>
    </body>
    </html>
    """
    
    options = {
        'page-size': 'A4',
        'margin-top': '25mm',
        'margin-right': '25mm', 
        'margin-bottom': '25mm',
        'margin-left': '25mm',
        'encoding': "UTF-8",
        'no-outline': None,
        'enable-local-file-access': None,
        'print-media-type': None
    }
    
    # Auto-detect wkhtmltopdf
    config = None
    if platform.system() == 'Windows':
        possible_paths = [
            r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
            r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe',
        ]
        for path in possible_paths:
            if os.path.exists(path):
                config = pdfkit.configuration(wkhtmltopdf=path)
                print(f"✅ Found wkhtmltopdf at: {path}")
                break
    
    try:
        print("🔄 Generating PHOS-style PDF...")
        
        if config:
            pdf_bytes = pdfkit.from_string(html_content, False, options=options, configuration=config)
        else:
            pdf_bytes = pdfkit.from_string(html_content, False, options=options)
        
        # Save PDF
        with open('lylux_phos_style.pdf', 'wb') as f:
            f.write(pdf_bytes)
        
        print("✅ SUCCESS! Generated: lylux_phos_style.pdf")
        print("📂 Open the PDF to see your PHOS-style layout!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("\n🔧 SOLUTIONS:")
        print("1. Download wkhtmltopdf from: https://wkhtmltopdf.org/downloads.html")
        print("2. Install the Windows 64-bit version")
        print("3. Run this test again")
        return False

if __name__ == "__main__":
    test_wkhtmltopdf()