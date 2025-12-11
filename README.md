Here is a clean, minimal README.md with no emojis, focused strictly on instructions and usage.

⸻

SPH e-Paper PDF Scraper

This script automates downloading Straits Times or Business Times e-paper pages (via NLB) and saves the original high-resolution PDFs. Pages are detected through network responses and merged into a single output PDF.

⸻

Requirements
	•	Python 3.10 or later
	•	Playwright
	•	pypdf

Install dependencies:

python3 -m venv venv
source venv/bin/activate

pip install playwright pypdf
playwright install


⸻

Configuration

Edit credentials in main.py:

NLB_USERNAME = r"username"
NLB_PASSWORD = r"password"

Select which paper to download by setting the correct XPath:

PAPER_XPATH = ST_XPATH   # for Straits Times
# PAPER_XPATH = BT_XPATH # for Business Times

Output files will be saved under:

output/
output/page_pdfs/


⸻

Running the Script

Run:

python main.py

The script will:
	1.	Open NLB’s SPH newspapers page
	2.	Log in using the provided credentials
	3.	Open the selected newspaper
	4.	Capture every page’s PDF via network responses
	5.	Merge them into a single PDF stored in output/YYYYMMDD.pdf

⸻

Notes
	•	This script relies on network PDF requests from the e-paper viewer.
	•	The next-page button state determines whether to continue, wait for ads, or stop at the end.
	•	XPaths may need updating if NLB or SPH changes their layout.
	•	This is intended for personal offline reading only.

⸻

If you want, I can also write a troubleshooting section, advanced usage, or examples.
