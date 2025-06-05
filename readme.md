Task Overview:

I have been given a task by a lighting company called Lylux. They design lights and provide product details in Excel format, but the data is completely unorganized. My task is to automate the process of converting this messy Excel data into well-formatted PDFs that look exactly like the sample output I’ve shared (a product sheet or datasheet PDF).

Key Details:

Input:
An Excel file containing unorganized data (like product codes, images, small certifications icons (CE, IP65), diagrams, and various specifications).

Output:
Multiple PDFs, each representing one unique combination of product specifications and customizable options.

How it Works:

The core output format:
The final PDF should match the sample product datasheet design I shared.

It includes main images (which stay the same for the same product).

Product headings, company logo, and diagrams also stay the same.

Dimensions stay the same (since the product is the same).

Dynamic sections:
The sections that change in each PDF are:

Specifications: e.g., Product Code, System Output, System Power, System Efficiency, Input Voltage, Beam Angle

Customizable Specifications: e.g., Color Temperature, Color Finish, Cover Option, Control Option, CRI Option

Combinations:
For each unique combination of the customizable specifications, one unique PDF should be generated.

For example, if there are 50 possible combinations, I need 50 different PDFs.

Each PDF only includes one specific combination, not a list of all combinations.

Implementation Requirements:

The process should automatically:

Read the jumbled Excel data and map it to the output template.

Generate all possible combinations of the customizable specifications.

Create one PDF for each combination, keeping the static parts (images, headings, diagrams) the same.

The final PDFs should be professionally formatted, matching the style and layout of the sample datasheet.

This automation can be implemented:

In code (like Python, JavaScript, or any preferred language with PDF and Excel handling libraries).

Or through n8n or another no-code automation platform, with modules to read Excel data, map it, and generate PDF documents for each combination.

Summary of Key Requirements:

✅ Input: messy Excel file
✅ Output: multiple well-formatted PDFs, each with one product combination
✅ Static parts: images, main headings, diagrams, dimensions
✅ Dynamic parts: product specifications and customizable specifications
✅ Automation to generate every possible combination
