# SPH Newspaper PDF Downloader

This script automates the download of full newspaper issues (page-by-page PDFs) from the **NLB SPH Newspapers portal**, then merges them into a single PDF file.

It uses **Playwright** to automate the browser and **pypdf** to merge the PDFs.

---

## Features

- Logs in to the NLB SPH portal
- Opens a selected newspaper (e.g. Straits Times or Business Times)
- Automatically navigates through all pages
- Handles ads that temporarily disable the “next page” button
- Downloads each page’s PDF directly from network responses
- Preserves correct page order
- Merges all pages into a single PDF
- Cleans up temporary per-page PDFs after completion

---

## Requirements

- Python 3.10+
- Google Chrome / Chromium installed

Python packages:
- `playwright`
- `pypdf`

---

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/chuachunmin/NewsScraper.git
   cd NewsScraper

2.	Create and activate a virtual environment (recommended):
	```bash
	python -m venv venv
	source venv/bin/activate   # macOS / Linux
	venv\Scripts\activate      # Windows


3.	Install dependencies:
	```bash
	pip install playwright pypdf


4.	Install Playwright browsers:
	```bash
	playwright install



⸻

Configuration

Edit the CONFIG section in the script:

Login credentials
	```bash
	USERNAME = r"user"
	PASSWORD = r"pass"


Choose which paper to download
	```bash
	PAPER_CODE = "ST"  # or "BT"


Supported values:
	•	ST – The Straits Times
	•	BT – The Business Times

⸻

Running the Script

Run the script normally:
	```bash
	python main.py


What happens:
	1.	A browser window opens
	2.	The script logs in
	3.	The newspaper viewer opens
	4.	Pages are automatically navigated and captured
	5.	A merged PDF is created in the output/ folder

⸻

Output
	•	Final PDF:
	```bash
	output/STYYYYMMDD.pdf
	output/BTYYYYMMDD.pdf


Example:
	```bash
	output/BT20251212.pdf


	•	Temporary per-page PDFs are stored in:
	```bash
	output/page_pdfs/


These are automatically deleted after the merge completes.

⸻

Notes
	•	The script runs in non-headless mode for stability.
	•	Ads are detected automatically and waited out.
	•	The script stops only when the “next page” button disappears.
	•	Page PDFs are captured from actual network responses (not screenshots).

⸻

Disclaimer

This script is intended for personal use by users with legitimate access to the NLB SPH portal.
Ensure compliance with NLB and SPH terms of service.

⸻

License

MIT License

