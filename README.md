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

- Python 3.10 or newer
- Google Chrome or Chromium

### Python dependencies

- playwright
- pypdf

---

## Installation

1. Clone the repository:
```bash
git clone https://github.com/chuachunmin/NewsScraper.git
cd NewsScraper


2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate   # macOS / Linux
venv\Scripts\activate      # Windows


3. Install dependencies:

pip install playwright pypdf

4. Install Playwright browsers:

playwright install

---

## Configuration

Edit the CONFIG section in the script.

### Login credentials
```bash
USERNAME = r”user”
PASSWORD = r”pass”


### Select newspaper
```bash
PAPER_CODE = “ST”  # or “BT”


Supported values:

- ST – The Straits Times  
- BT – The Business Times  

---

## Running the Script

Run:
```bash
python main.py


Execution flow:

1. Browser opens
2. Login is performed
3. Newspaper viewer loads
4. Pages are navigated automatically
5. PDFs are captured and merged

---

## Output

Final PDF files are saved to:
```bash
output/STYYYYMMDD.pdf
output/BTYYYYMMDD.pdf


Example:
```bash
output/BT20251212.pdf


Temporary per-page PDFs are stored in:

output/page_pdfs/

This directory is deleted automatically after the merge completes.

---

## Notes

- The script runs in non-headless mode for stability
- Ads are detected and waited out automatically
- Navigation stops only when the next-page button disappears
- PDFs are captured from network responses, not screenshots

---

## Disclaimer

This script is intended for personal use by users with legitimate access to the NLB SPH Newspapers portal.  
Ensure compliance with all applicable terms of service.

---

## License

MIT License
