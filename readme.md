🔧 Task Overview: Interactive PDF Generator Web App for Lylux
We have been assigned a project by a lighting design company called Lylux. They provide product data in messy Excel files and previously requested an automated system to generate 50+ product datasheets (PDFs) for every possible specification combination.

After further discussion, we’ve decided to build a user-friendly web application that allows manual control and customization of datasheet generation. This approach eliminates unnecessary output and gives users flexibility to select only the combinations they care about.

📥 Input:
Unorganized Excel file containing product metadata (product code, specs, certifications, images, etc.)

Static assets like:

Product images

Certification logos (e.g., CE, IP65)

Dimension diagrams

Branding elements like logo and headers

📤 Output:
A single PDF at a time, designed to match a sample datasheet format (provided).

Each PDF will reflect only the specifications and customizable options the user selects via the UI.

Users will be able to dynamically configure the following:

Product Code

System Output / Power / Efficiency

Input Voltage & Beam Angle

Color Temperature

Color Finish

Cover Option

Control Type

CRI Option

🧩 Web App Features:
Upload Section:

Upload unorganized Excel file

Upload static assets (e.g., product images, CE/IP65 icons, diagrams)

Smart Mapping & Preview:

Map Excel fields to the correct datasheet fields

Preview available product configurations

Dynamic PDF Builder:

UI elements like dropdowns and checkboxes to select:

Any combination of specifications

Which attributes to include or leave blank

Preview formatted PDF before download

Export Option:

Generate PDF using selected options

Download or email the PDF directly from the app

🛠 Implementation Considerations:
Frontend Framework: React, Vue, or any UI-friendly tech stack

Backend (optional): Node.js / FastAPI / Flask (for processing files, PDF rendering)

PDF Generator: jsPDF, pdf-lib (JS), ReportLab (Python), or similar

Excel Parser: SheetJS (JS), pandas/openpyxl (Python)

Deployment: Lightweight host (e.g., Vercel, Heroku, or custom VPS)

✅ Summary of Key Requirements:
Element Description
Input Messy Excel + images/icons
Output One clean PDF at a time (user-selected combo)
Static Content Headings, diagrams, logos, dimension details
Dynamic Content All specification & customizable options selected via UI
Goal Let user build PDFs interactively from Excel inputs — no mass generation
