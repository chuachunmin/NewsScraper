from pathlib import Path
from datetime import datetime

from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter

# =============================
# CONFIG
# =============================

SPH_URL = "https://eresources.nlb.gov.sg/main/sphnewspapers"

# Login credentials (edit these)
USERNAME = r"username"
PASSWORD = r"password"  # raw string fine

# Login input selectors
USERNAME_SELECTOR = "#username"
PASSWORD_SELECTOR = "#password"

# Which paper to open (thumbnail image xpath on the main SPH page)
ST_XPATH = "/html/body/div[1]/div/div[1]/div[3]/div[1]/div/div/a/img"
BT_XPATH = "/html/body/div[1]/div/div[1]/div[3]/div[2]/div/div/a/img"

# Choose which paper to download
PAPER_XPATH = ST_XPATH  # or BT_XPATH

# XPaths you gave
LOGIN_LINK_XPATH = "/html/body/header/div/nlb-header/div/nav/div[2]/div/div[3]/ui-others/div/a"

FIRST_TARGET_XPATH = PAPER_XPATH
SECOND_TARGET_XPATH = "//*[@id='app']/div/div/div[3]/div/div/div[1]/button"
THIRD_TARGET_XPATH = "//*[@id='app']/div/div/div[2]/div/div/div[2]/div/div[2]/button"

# Next-page button logic:
# - visible & enabled   -> clickable (turn page)
# - visible & disabled  -> ads
# - not visible         -> last page
NEXT_BUTTON_XPATH = "//*[@id='next-page-button']"

# Output paths
OUTPUT_DIR = Path("output")
PAGE_PDFS_DIR = OUTPUT_DIR / "page_pdfs"

# Globals for PDFs
PER_PAGE_BASES: set[str] = set()   # store base URLs we've successfully saved
PER_PAGE_FILES: list[Path] = []    # paths in the order saved
PAGE_COUNTER: int = 0              # purely for logging/filenames


# =============================
# HELPERS
# =============================

def xp(xpath: str) -> str:
    """Tell Playwright explicitly this is an XPath selector."""
    return f"xpath={xpath}"


def ensure_dirs():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PAGE_PDFS_DIR.mkdir(parents=True, exist_ok=True)


def setup_pdf_response_listener(page):
    """
    Attach a response listener that:
      - detects per-page OPS PDFs
      - saves PDF bytes immediately to disk
      - tracks file paths for later merging

    IMPORTANT FIX:
      Only mark a base URL as "seen" AFTER response.body() succeeds.
    """
    def handle_response(response):
        global PAGE_COUNTER

        try:
            url = response.url

            # Only care about per-page OPS PDFs (ignore other stuff)
            if "/OPS/" not in url:
                return
            if "_pdf.pdf" not in url:
                return

            # Normalise base by stripping query
            base = url.split("?", 1)[0]

            # If we've already successfully saved this base, skip
            if base in PER_PAGE_BASES:
                return

            # Try to get body. This is where the first-page failure happened.
            try:
                body = response.body()
            except Exception as e:
                # DO NOT mark 'base' as seen here.
                # If a later response for the same URL has a real body,
                # we want to try again.
                print(f"[!]   Error handling PDF response for {url}: {e}")
                return

            # Now we know we have real bytes -> mark as seen and save
            PER_PAGE_BASES.add(base)

            PAGE_COUNTER += 1
            page_index = PAGE_COUNTER
            page_pdf_path = PAGE_PDFS_DIR / f"page_{page_index:03d}.pdf"
            page_pdf_path.write_bytes(body)
            PER_PAGE_FILES.append(page_pdf_path)

            print(f"[i]   New PDF URL saved as page {page_index}: {url}")

        except Exception as e:
            # Never crash the whole run from inside the callback
            print(f"[!]   Unexpected error in response handler: {e}")

    page.on("response", handle_response)


def perform_login(page):
    print("[i] Waiting for login link...")
    page.wait_for_selector(xp(LOGIN_LINK_XPATH))

    print("[i] Clicking login link...")
    page.click(xp(LOGIN_LINK_XPATH))

    print("[i] Filling username...")
    page.wait_for_selector(USERNAME_SELECTOR)
    page.fill(USERNAME_SELECTOR, USERNAME)

    print("[i] Filling password...")
    page.wait_for_selector(PASSWORD_SELECTOR)
    page.fill(PASSWORD_SELECTOR, PASSWORD)

    print("[i] Submitting login via ENTER...")
    page.keyboard.press("Enter")

    page.wait_for_load_state("networkidle")
    print("[i] Login complete (assuming credentials are correct).")


def open_viewer_page(context, main_page):
    """Click the paper thumbnail, attach listener, and drill into the viewer."""
    print("[i] Waiting for PAPER thumbnail (FIRST_TARGET_XPATH)...")
    main_page.wait_for_selector(xp(FIRST_TARGET_XPATH))

    print("[i] Clicking PAPER thumbnail, expecting viewer tab...")
    with context.expect_page() as viewer_info:
        main_page.click(xp(FIRST_TARGET_XPATH))
    viewer_page = viewer_info.value

    viewer_page.wait_for_load_state("domcontentloaded")

    # Attach PDF listener as early as possible
    setup_pdf_response_listener(viewer_page)

    print("[i] Waiting for SECOND element (button)...")
    viewer_page.wait_for_selector(xp(SECOND_TARGET_XPATH))
    print("[i] Clicking SECOND element...")
    viewer_page.click(xp(SECOND_TARGET_XPATH))

    print("[i] Waiting for THIRD element (button)...")
    viewer_page.wait_for_selector(xp(THIRD_TARGET_XPATH))
    print("[i] Clicking THIRD element...")
    viewer_page.click(xp(THIRD_TARGET_XPATH))

    return viewer_page


def analyze_next_button(page) -> str:
    """
    Inspect the next-page button.

    Returns:
        "clickable"  -> button is visible & enabled (we should click it)
        "disabled"   -> button visible but disabled/blocked (ads)
        "missing"    -> button not visible at all (last page)
    """
    try:
        locator = page.locator(xp(NEXT_BUTTON_XPATH))
        count = locator.count()
        if count == 0:
            return "missing"

        btn = locator.first

        visible = btn.is_visible()
        style = btn.get_attribute("style") or ""
        disabled_attr = btn.get_attribute("disabled")
        aria_disabled = (btn.get_attribute("aria-disabled") or "").lower()
        class_name = btn.get_attribute("class") or ""

        # Not visible or display:none => treat as missing/last page
        if (not visible) or ("display: none" in style):
            return "missing"

        # Disabled => ad
        if (
            disabled_attr is not None
            or aria_disabled == "true"
            or "is-disabled" in class_name
            or "pointer-events: none" in style
        ):
            return "disabled"

        return "clickable"
    except Exception:
        # If anything goes wrong reading attributes, be safe and assume missing
        return "missing"


def navigate_all_pages(viewer_page):
    """
    Walk the entire issue by watching the next-page button state while the
    response listener saves all PDFs.

    - clickable  -> click
    - disabled   -> ad, wait
    - missing    -> last page
    """
    max_steps = 300  # safety
    step = 0

    print("[i] Starting navigation driven by next-page button state & PDF responses...")

    # Initial wait to let page 1 PDFs load
    print("[i] Initial wait for PDFs on first page (8000 ms)...")
    viewer_page.wait_for_timeout(8000)
    print(f"[i]   PDFs saved after initial wait: {len(PER_PAGE_FILES)}")

    while step < max_steps:
        state = analyze_next_button(viewer_page)
        print(f"[i] Navigation step {step}, distinct per-page PDFs so far: {len(PER_PAGE_FILES)}")

        if state == "clickable":
            print("[i]   Next-page button clickable; clicking...")
            viewer_page.click(xp(NEXT_BUTTON_XPATH))
            viewer_page.wait_for_timeout(500)  # allow responses to arrive
        elif state == "disabled":
            print("[i]   Next-page button present but disabled/blocked (likely ad). Waiting this step...")
            viewer_page.wait_for_timeout(1000)
        else:  # "missing"
            print("[i]   Next-page button missing/not visible; assuming last page. Stopping navigation.")
            break

        step += 1

    # Give any straggler responses a moment to finish
    print("[i] Final short wait for any remaining PDF responses (3000 ms)...")
    viewer_page.wait_for_timeout(3000)

    print(f"[i] Finished navigation. Total per-page PDFs saved: {len(PER_PAGE_FILES)}")


def merge_saved_pdfs(final_pdf_path: Path):
    """
    Merge already-saved per-page PDFs into a single file using pypdf.
    """
    writer = PdfWriter()

    print(f"[i] Merging {len(PER_PAGE_FILES)} PDFs into {final_pdf_path}...")
    for path in PER_PAGE_FILES:
        print(f"[i]   Adding {path.name}")
        reader = PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)

    with final_pdf_path.open("wb") as f:
        writer.write(f)

    print(f"[i] Merged PDF saved to: {final_pdf_path}")


def main():
    ensure_dirs()
    today_str = datetime.now().strftime("%Y%m%d")
    final_pdf_path = OUTPUT_DIR / f"{today_str}.pdf"
    print(f"[i] Final merged PDF will be: {final_pdf_path}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        print("[i] Opening SPH page...")
        page.goto(SPH_URL, wait_until="load")

        perform_login(page)
        viewer_page = open_viewer_page(context, page)

        navigate_all_pages(viewer_page)
        merge_saved_pdfs(final_pdf_path)

        browser.close()

    print("\n[i] All done.")


if __name__ == "__main__":
    main()
